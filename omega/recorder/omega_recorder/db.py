import sqlite3, threading, time

SCHEMA = """
PRAGMA journal_mode=WAL;
CREATE TABLE IF NOT EXISTS symbols(sym TEXT PRIMARY KEY, status TEXT, contract TEXT, onboard INTEGER, delivery INTEGER,
  min_notional REAL, tick REAL, first_seen INTEGER, last_seen INTEGER, delisted_at INTEGER);
CREATE TABLE IF NOT EXISTS listing_events(ts INTEGER, sym TEXT, old_status TEXT, new_status TEXT);
CREATE TABLE IF NOT EXISTS k1h(sym TEXT, t INTEGER, o REAL, h REAL, l REAL, c REAL, v REAL, qv REAL, n INTEGER, tbv REAL,
  src TEXT, PRIMARY KEY(sym, t)) WITHOUT ROWID;
CREATE TABLE IF NOT EXISTS k1m(sym TEXT, t INTEGER, o REAL, h REAL, l REAL, c REAL, v REAL, qv REAL, n INTEGER, tbv REAL,
  PRIMARY KEY(sym, t)) WITHOUT ROWID;
CREATE TABLE IF NOT EXISTS funding(sym TEXT, t INTEGER, rate REAL, mark REAL, src TEXT, PRIMARY KEY(sym, t)) WITHOUT ROWID;
CREATE TABLE IF NOT EXISTS premium(sym TEXT, t INTEGER, mark REAL, idx REAL, last_rate REAL, next_t INTEGER, PRIMARY KEY(sym, t)) WITHOUT ROWID;
CREATE TABLE IF NOT EXISTS oi(sym TEXT, t INTEGER, oi REAL, oi_value REAL, PRIMARY KEY(sym, t)) WITHOUT ROWID;
CREATE TABLE IF NOT EXISTS ratios(sym TEXT, t INTEGER, kind TEXT, val REAL, a REAL, b REAL, PRIMARY KEY(sym, t, kind)) WITHOUT ROWID;
CREATE TABLE IF NOT EXISTS liquidations(sym TEXT, t INTEGER, side TEXT, price REAL, qty REAL, avg_price REAL, status TEXT);
CREATE INDEX IF NOT EXISTS liq_t ON liquidations(t);
CREATE TABLE IF NOT EXISTS depth(sym TEXT, t INTEGER, mid REAL, spread_bps REAL, bid05 REAL, ask05 REAL, bid2 REAL, ask2 REAL,
  PRIMARY KEY(sym, t)) WITHOUT ROWID;
CREATE TABLE IF NOT EXISTS events(id INTEGER PRIMARY KEY, kind TEXT, t INTEGER, note TEXT, source TEXT);
CREATE TABLE IF NOT EXISTS archive_files(path TEXT PRIMARY KEY, rows INTEGER, fetched INTEGER);
CREATE TABLE IF NOT EXISTS job_runs(job TEXT, started INTEGER, finished INTEGER, ok INTEGER, rows INTEGER, error TEXT);
CREATE INDEX IF NOT EXISTS job_runs_job ON job_runs(job, started);
"""

class DB:
    def __init__(self, path):
        self.path = path
        self.lock = threading.Lock()
        self.con = sqlite3.connect(path, check_same_thread=False)
        self.con.row_factory = sqlite3.Row
        with self.lock:
            self.con.executescript(SCHEMA)

    def many(self, sql, rows):
        rows = list(rows)
        if not rows:
            return 0
        with self.lock:
            self.con.executemany(sql, rows); self.con.commit()
        return len(rows)

    def run(self, sql, args=()):
        with self.lock:
            cur = self.con.execute(sql, args); self.con.commit(); return cur.lastrowid

    def q(self, sql, args=()):
        with self.lock:
            return [dict(r) for r in self.con.execute(sql, args).fetchall()]

    def one(self, sql, args=()):
        r = self.q(sql, args)
        return r[0] if r else None

    def job(self, name, started, ok, rows, error=None):
        self.run("INSERT INTO job_runs VALUES(?,?,?,?,?,?)", (name, started, int(time.time() * 1000), int(ok), rows, error))
        self.run("DELETE FROM job_runs WHERE job=? AND started < ?", (name, started - 14 * 86400_000))

K_SQL = "INSERT OR REPLACE INTO {t}(sym,t,o,h,l,c,v,qv,n,tbv{src}) VALUES(?,?,?,?,?,?,?,?,?,?{q})"
def kline_sql(table, with_src):
    return K_SQL.format(t=table, src=",src" if with_src else "", q=",?" if with_src else "")
