"""Backfill from Binance's public archive (data.binance.vision), including delisted perpetuals."""
import csv, io, re, time, zipfile
import xml.etree.ElementTree as ET
from .binance import kline_rows
from .db import kline_sql

NS = "{http://s3.amazonaws.com/doc/2006-03-01/}"

def parse_listing(xml_text):
    """S3 listing XML -> (prefixes, keys, next_marker or None)."""
    root = ET.fromstring(xml_text)
    pref = [e.findtext(f"{NS}Prefix") for e in root.findall(f"{NS}CommonPrefixes")]
    keys = [e.findtext(f"{NS}Key") for e in root.findall(f"{NS}Contents")]
    trunc = (root.findtext(f"{NS}IsTruncated") or "false").lower() == "true"
    nxt = root.findtext(f"{NS}NextMarker") or ((keys or pref)[-1] if trunc and (keys or pref) else None)
    return pref, keys, (nxt if trunc else None)

async def list_all(client, list_url, prefix, delimiter="/"):
    pref, keys, marker = [], [], None
    while True:
        params = dict(prefix=prefix, delimiter=delimiter)
        if marker: params["marker"] = marker
        r = await client.get(list_url, params=params); r.raise_for_status()
        p, k, marker = parse_listing(r.text); pref += p; keys += k
        if not marker: return pref, keys

def read_zip_csv(blob):
    z = zipfile.ZipFile(io.BytesIO(blob)); name = z.namelist()[0]
    rows = list(csv.reader(io.TextIOWrapper(z.open(name), "utf-8")))
    if rows and rows[0] and not re.match(r"^-?\d", rows[0][0]):   # files from 2022 on carry a header row
        return rows[0], rows[1:]
    return None, rows

def funding_rows(sym, header, rows):
    out = []
    for r in rows:
        if header and "calc_time" in header:
            t = int(r[header.index("calc_time")]); rate = float(r[header.index("last_funding_rate")])
        else:
            t, rate = int(r[0]), float(r[-1])
        t = t // 1000 if t > 10**14 else t
        out.append((sym, t, rate, None, "archive"))
    return out

async def backfill(db, client, s, symbols=None, months=None, log=print):
    """Monthly 1h klines + funding for every USDT perpetual in the archive (listed or not). Skips files already fetched."""
    root = "data/futures/um/monthly/klines/"
    pref, _ = await list_all(client, s.archive_list, root)
    archive_syms = sorted(p[len(root):].strip("/") for p in pref if p.endswith("USDT/"))
    db.many("INSERT OR IGNORE INTO symbols(sym,status,first_seen) VALUES(?,?,?)",
            [(x, "ARCHIVE_ONLY", int(time.time() * 1000)) for x in archive_syms])
    todo = [x for x in archive_syms if symbols is None or x in symbols]
    done = {r["path"] for r in db.q("SELECT path FROM archive_files")}
    total = 0
    for sym in todo:
        for kind, sub in (("k", f"{root}{sym}/1h/"), ("f", f"data/futures/um/monthly/fundingRate/{sym}/")):
            _, keys = await list_all(client, s.archive_list, sub)
            for key in keys:
                if not key.endswith(".zip") or key in done: continue
                m = re.search(r"(\d{4}-\d{2})\.zip$", key)
                if not m or m.group(1) < s.backfill_from or (months and m.group(1) not in months): continue
                r = await client.get(f"{s.archive}/{key}")
                if r.status_code == 404: continue
                r.raise_for_status()
                header, rows = read_zip_csv(r.content)
                if kind == "k":
                    n = db.many(kline_sql("k1h", True), kline_rows(sym, rows, "archive"))
                else:
                    n = db.many("INSERT OR REPLACE INTO funding(sym,t,rate,mark,src) VALUES(?,?,?,?,?)", funding_rows(sym, header, rows))
                db.run("INSERT OR REPLACE INTO archive_files VALUES(?,?,?)", (key, n, int(time.time() * 1000)))
                total += n
        log(f"archive {sym}: total rows so far {total}")
    return total, len(archive_syms)
