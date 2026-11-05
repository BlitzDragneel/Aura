import io, zipfile, numpy as np
import reference_load as L
from omega_recorder import exports, archive
from omega_recorder.binance import kline_rows, depth_summary

def test_export_reads_back_through_the_research_decoder():
    rng = np.random.default_rng(1); rows = []; c = 0.0123456
    for i in range(500):
        if i in (100, 101, 300): continue                       # missing hours
        o = c; c = c * np.exp(rng.normal(0, 0.01)); h = max(o, c) * 1.004; l = min(o, c) * 0.993
        rows.append(dict(t=(473_352 + i) * 3_600_000, o=o, h=h, l=l, c=c, v=float(rng.integers(1, 9e6))))
    m = L.dec_market(exports.encode_market("PEPEUSDT", rows), 60)
    assert list(m["t"] * 60 * 60_000) == [r["t"] for r in rows]          # candle times exact
    for k in "ohlc":
        got = m[k]; want = np.array([r[k] for r in rows])
        assert np.max(np.abs(got / want - 1)) < 2e-6, k                  # ≥ 6 significant digits
    assert np.array_equal(m["v"], [r["v"] for r in rows])

XML = """<?xml version="1.0" encoding="UTF-8"?><ListBucketResult xmlns="http://s3.amazonaws.com/doc/2006-03-01/">
<IsTruncated>{tr}</IsTruncated>{nm}{body}</ListBucketResult>"""
def listing(prefixes=(), keys=(), next_marker=None):
    body = "".join(f"<CommonPrefixes><Prefix>{p}</Prefix></CommonPrefixes>" for p in prefixes) + "".join(f"<Contents><Key>{k}</Key></Contents>" for k in keys)
    return XML.format(tr="true" if next_marker else "false", nm=f"<NextMarker>{next_marker}</NextMarker>" if next_marker else "", body=body)

def test_listing_parse_and_pagination_marker():
    p, k, nxt = archive.parse_listing(listing(["a/X/", "a/Y/"], [], "a/Y/"))
    assert p == ["a/X/", "a/Y/"] and nxt == "a/Y/"
    p, k, nxt = archive.parse_listing(listing([], ["a.zip"]))
    assert k == ["a.zip"] and nxt is None

def zipped(text, name="x.csv"):
    b = io.BytesIO(); z = zipfile.ZipFile(b, "w"); z.writestr(name, text); z.close(); return b.getvalue()

def test_archive_csv_with_and_without_header_and_microseconds():
    line = "1704067200000,42000.1,42100,41900,42050.5,123.4,1704070799999,5190000.1,1500,60.2,2531000,0"
    h, rows = archive.read_zip_csv(zipped(line + "\n"))
    assert h is None and kline_rows("BTCUSDT", rows, "archive")[0][:6] == ("BTCUSDT", 1704067200000, 42000.1, 42100.0, 41900.0, 42050.5)
    hdr = "open_time,open,high,low,close,volume,close_time,quote_volume,count,taker_buy_volume,taker_buy_quote_volume,ignore\n"
    h, rows = archive.read_zip_csv(zipped(hdr + line.replace("1704067200000", "1704067200000000", 1)))
    assert h[0] == "open_time" and kline_rows("BTCUSDT", rows)[0][1] == 1704067200000   # µs normalised to ms
    fh, fr = archive.read_zip_csv(zipped("calc_time,funding_interval_hours,last_funding_rate\n1704067200000,8,0.00012\n"))
    assert archive.funding_rows("BTCUSDT", fh, fr) == [("BTCUSDT", 1704067200000, 0.00012, None, "archive")]

def test_depth_summary():
    d = depth_summary(dict(bids=[["99.9", "10"], ["99.0", "5"], ["97", "100"]], asks=[["100.1", "4"], ["101", "3"], ["103", "100"]]))
    assert round(d["mid"], 6) == 100.0 and round(d["spread_bps"], 3) == 20.0
    assert round(d["bid05"], 6) == 999.0 and round(d["ask05"], 6) == 400.4 and round(d["bid2"], 3) == 999 + 495
