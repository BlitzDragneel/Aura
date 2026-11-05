"""Order sizing and exchange rounding (Binance filters: LOT_SIZE stepSize/minQty, PRICE_FILTER tickSize, MIN_NOTIONAL)."""
import math


class SizingError(Exception):
    pass


def decimals(step):
    s = ("%.12f" % float(step)).rstrip("0")
    return len(s.split(".")[1]) if "." in s else 0


def floor_to(x, step):
    return round(math.floor(float(x) / step + 1e-9) * step, decimals(step))


def ceil_to(x, step):
    return round(math.ceil(float(x) / step - 1e-9) * step, decimals(step))


def round_price(px, tick, side, kind):
    """Round in the safe direction. Long entry limit: down (never pay more than the rule). Long stop (a sell): up,
    i.e. a hair closer to the price, so rounding never moves the stop toward liquidation. Shorts mirror."""
    if kind == "entry":
        return floor_to(px, tick) if side == "long" else ceil_to(px, tick)
    return ceil_to(px, tick) if side == "long" else floor_to(px, tick)


def quantity(margin_usdt, leverage, price, info, up_tolerance=0.10):
    """Contracts for `margin_usdt` at `leverage`: floor to the step; refuse below the exchange minimums."""
    if not (price and price > 0):
        raise SizingError("no price")
    q = floor_to(margin_usdt * leverage / price, info["step"])
    if q * price < info["minNotional"] - 1e-9 or q < info["minQty"]:
        # rounding down left it under the exchange minimum: go up to the minimum if that costs <= 10% more margin
        q2 = max(ceil_to(info["minNotional"] / price, info["step"]), info["minQty"])
        if q2 * price <= margin_usdt * leverage * (1 + up_tolerance):
            q = q2
    if q < info["minQty"] or q * price < info["minNotional"] - 1e-9:
        need = max(info["minNotional"], info["minQty"] * price) / leverage
        raise SizingError(f"{margin_usdt:.2f} USDT at {leverage}x buys {q} contracts = {q*price:.2f} USDT, below the "
                          f"exchange minimum ({info['minNotional']} USDT / {info['minQty']} qty); needs >= {need:.2f} USDT margin")
    return q
