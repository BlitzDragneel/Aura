"""python -m omega_recorder serve | selfcheck | backfill [SYM,SYM]"""
import asyncio, sys, os

def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "serve"
    if cmd == "serve":
        import uvicorn
        from .api import create_app
        uvicorn.run(create_app(), host=os.environ.get("OMEGA_HOST", "127.0.0.1"), port=int(os.environ.get("OMEGA_PORT", "8000")))
    elif cmd == "selfcheck":
        from .selfcheck import run; sys.exit(asyncio.run(run()))
    elif cmd == "backfill":
        import httpx
        from .config import Settings
        from .db import DB
        from .archive import backfill
        s = Settings(); syms = set(sys.argv[2].upper().split(",")) if len(sys.argv) > 2 else None
        async def go():
            async with httpx.AsyncClient(timeout=60) as c:
                n, k = await backfill(DB(s.db_path), c, s, syms); print(f"done: {n} rows from {k} archive symbols")
        asyncio.run(go())
    else:
        print(__doc__)

if __name__ == "__main__":
    main()
