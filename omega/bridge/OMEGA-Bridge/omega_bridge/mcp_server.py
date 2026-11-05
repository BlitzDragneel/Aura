"""The Bridge as a Claude Desktop connector (MCP over stdio). Claude Desktop asks you before every tool call."""
import json
try: from mcp.server.mcpserver import MCPServer as _S          # mcp 2.x
except ImportError: from mcp.server.fastmcp import FastMCP as _S  # mcp 1.x
from .core import Bridge
from . import log
B = Bridge(); app = _S('omega-bridge', instructions='Controls the owner\'s Binance USDT-M futures and MT5 (Exness) accounts from their PC, behind a guard: demo/testnet unless they switched live on, a stop on every order, capped risk and size, a daily loss limit and a kill switch. Always preview_order first and show the user the exact order; call place_order with confirm=true only after the user explicitly says to send it.')
def J(x): return json.dumps(x, default=str, indent=1)
@app.tool()
def status() -> str:
    """Both venues: connected or not, demo/testnet/LIVE, balance, open positions, today's result, the guard's limits, the kill switch."""
    return J(B.status())
@app.tool()
def price(venue: str, symbol: str) -> str:
    """Current price. venue: binance or mt5 (Exness). Example: binance BTCUSDT, mt5 XAUUSD."""
    return J(B.b().price(symbol.upper()) if venue == 'binance' else B.m().price(symbol.upper()))
@app.tool()
def positions(venue: str) -> str:
    """Open positions on binance or mt5."""
    return J(B.positions(venue))
@app.tool()
def preview_order(venue: str, symbol: str, side: str, stop: float, size_usd: float = 0, volume: float = 0, risk_usd: float = 0, order_type: str = 'MARKET', price: float = 0, target: float = 0) -> str:
    """Build the exact order (rounded to the exchange's rules) and run every guard check. Sends nothing.
    binance: size_usd (notional) or volume (contracts). mt5: volume (lots) or risk_usd (money lost if the stop is hit)."""
    return J(B.preview(venue, symbol, side, size_usd=size_usd or None, volume=volume or None, risk_usd=risk_usd or None, type_=order_type, price=price or None, stop=stop, target=target or None))
@app.tool()
def place_order(venue: str, symbol: str, side: str, stop: float, confirm: bool, size_usd: float = 0, volume: float = 0, risk_usd: float = 0, order_type: str = 'MARKET', price: float = 0, target: float = 0) -> str:
    """Send the order, only if confirm is true and every guard check passes. Use after preview_order and the user's explicit go-ahead."""
    return J(B.place(venue, symbol, side, confirm=confirm, size_usd=size_usd or None, volume=volume or None, risk_usd=risk_usd or None, type_=order_type, price=price or None, stop=stop, target=target or None))
@app.tool()
def close_position(venue: str, symbol: str) -> str:
    """Close the whole position in a symbol at market (and cancel its stop/target orders on Binance)."""
    return J(B.close(venue, symbol))
@app.tool()
def kill_switch(on: bool, flatten: bool = False) -> str:
    """on=true blocks every new order; flatten=true also closes all positions on both venues. on=false lifts it."""
    return J(B.kill(on, flatten))
@app.tool()
def order_log(n: int = 20) -> str:
    """The last n entries of the order log (sent, refused, errors, closes, kill switch)."""
    return J(log.tail(n))
@app.tool()
def funding_monitor(top: int = 10) -> str:
    """Live funding rates (annualized), the highest and the most negative, with warnings. Information only: places nothing.
    E34 found the delta-neutral funding harvest FAILED in 2025–26 because funding can flip violently."""
    from .funding import snapshot
    return J(snapshot(top))
def run(): app.run('stdio')
