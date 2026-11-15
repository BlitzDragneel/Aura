import datetime as dt, json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))
from edges.alerts import notify


def st(asset, day="WAIT", calls=()):
    return dict(asset=asset, name=asset, read=dict(price=100.0, trend={"1h": {"state": "up"}}, volatility={"regime": "normal"}),
                horizons={"day": dict(state=day, reasons=["r"], direction=None)}, open_calls=list(calls))


def test_flow(tmp_path, monkeypatch):
    for k in ("TELEGRAM_BOT_TOKEN", "TELEGRAM_CHAT_ID", "WHATSAPP_PHONE", "CALLMEBOT_APIKEY"):
        monkeypatch.delenv(k, raising=False)
    (tmp_path / "assets").mkdir()
    w = lambda s: (tmp_path / "assets" / f"{s['asset']}.json").write_text(json.dumps(s))
    w(st("XAU", "WATCH"))
    t = dt.datetime(2026, 11, 15, 5, tzinfo=dt.timezone.utc)
    m, _ = notify.main(str(tmp_path), t)
    assert len(m) == 1 and "morning read" in m[0]            # first run: summary only
    m, _ = notify.main(str(tmp_path), t)
    assert m == []                                            # nothing changed
    w(st("XAU", "WAIT")); notify.main(str(tmp_path), t)
    w(st("XAU", "WATCH", [dict(id="c1", rule="x", side="buy", entry=1, stop=0, target=3)]))
    m, _ = notify.main(str(tmp_path), t)
    assert len(m) == 2 and "WATCH" in m[0] and "CALL" in m[1]
    t = t.replace(day=16)
    m, _ = notify.main(str(tmp_path), t.replace(hour=12))
    assert len(m) == 1 and "morning" in m[0]                  # daily summary once
    assert notify.main(str(tmp_path), t.replace(hour=13))[0] == []
