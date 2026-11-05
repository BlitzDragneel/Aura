import os
from dataclasses import dataclass, field

def _env(name, default):
    return os.environ.get(name, default)

@dataclass
class Settings:
    db_path: str = field(default_factory=lambda: _env("OMEGA_DB", "omega_recorder.sqlite"))
    rest: str = field(default_factory=lambda: _env("OMEGA_REST", "https://fapi.binance.com"))
    ws: str = field(default_factory=lambda: _env("OMEGA_WS", "wss://fstream.binance.com/ws"))
    archive: str = field(default_factory=lambda: _env("OMEGA_ARCHIVE", "https://data.binance.vision"))
    # The archive's file listing (the bucket behind data.binance.vision). Not verified from the build sandbox: run selfcheck.
    archive_list: str = field(default_factory=lambda: _env("OMEGA_ARCHIVE_LIST", "https://s3-ap-northeast-1.amazonaws.com/data.binance.vision"))
    backfill_from: str = field(default_factory=lambda: _env("OMEGA_BACKFILL_FROM", "2020-01"))
    watch_n: int = field(default_factory=lambda: int(_env("OMEGA_WATCH_N", "40")))      # OI, ratios, 1m candles
    depth_n: int = field(default_factory=lambda: int(_env("OMEGA_DEPTH_N", "10")))      # order-book summaries
    forward_start: str = field(default_factory=lambda: _env("OMEGA_FORWARD_START", "2026-11-01"))  # paper record start (UTC date)
    token: str = field(default_factory=lambda: _env("OMEGA_TOKEN", ""))                 # needed for write endpoints; never stored in files
    read_token: str = field(default_factory=lambda: _env("OMEGA_READ_TOKEN", ""))       # optional: when set, reads need it too (public servers)
    cors: str = field(default_factory=lambda: _env("OMEGA_CORS", "*"))
    jobs_enabled: bool = field(default_factory=lambda: _env("OMEGA_JOBS", "1") == "1")
