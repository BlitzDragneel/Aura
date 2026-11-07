# Bot-3 reachability survey of keyless public data sources (tested 2026-11-05 from this sandbox)

| Source | Endpoint tested | Result | History | Fetched to |
|---|---|---|---|---|
| Binance Vision premiumIndexKlines | data.binance.vision/data/futures/um/monthly/premiumIndexKlines/{SYM}/1h | 200 OK | 2020-01 → (per coin listing) | /home/user/data/premium_1h (60 coins) |
| Binance Vision metrics (OI, ratios) | .../futures/um/daily/metrics/{SYM} | 200 OK | 2020-09 → (BTC) | not fetched (E30/E33 already used OI/ratios) |
| Binance Vision spot klines | .../spot/monthly/klines/{SYM}/1h | 200 OK | 2017 → | /home/user/data/spot_1h (BTC, ETH, + FDUSD pairs) |
| Binance Vision mark/index klines, aggTrades | same tree | 200 OK (listing via S3 XML `s3-ap-northeast-1.amazonaws.com/data.binance.vision?prefix=`) | | not fetched |
| fapi.binance.com | /fapi/v1/time | **451 blocked** (restricted location) | | |
| api.bybit.com | /v5/market/kline | **403 blocked** (CloudFront country block) | | |
| OKX public | /api/v5/market/history-candles | 200 OK | 2020-01 → candles; funding-rate-history only recent (empty for 2020); rubik option OI/volume daily recent | not fetched |
| Coinbase Exchange | api.exchange.coinbase.com/products/{P}/candles | 200 OK, 300 bars/request | 2015 → | /home/user/data/coinbase_1h (BTC-USD, ETH-USD 2020 →) |
| Kraken, Bitstamp OHLC | public OHLC | 200 OK (Kraken only last 720 bars) | | not fetched |
| Deribit DVOL | /api/v2/public/get_volatility_index_data | 200 OK (continuation paging) | **2021-03-24 →** hourly | /home/user/data/deribit_dvol (BTC, ETH) |
| Deribit historical volatility | /public/get_historical_volatility | 200 OK, ~last 15 days only | | |
| Deribit option trades with IV | history.deribit.com get_last_trades_by_currency_and_time | 200 OK | 2021 → (tick level, heavy) | not fetched (time budget) |
| DefiLlama stablecoins | stablecoins.llama.fi/stablecoincharts/all | 200 OK | 2017-11 → daily | /home/user/data/stablecoins/total.parquet |
| alternative.me Fear & Greed | api.alternative.me/fng/?limit=0 | 200 OK | 2018-02 → daily | /home/user/data/fear_greed/fng.parquet |
| CoinMetrics community | community-api.coinmetrics.io/v4 asset-metrics | 200 OK, 31 free metrics incl. FlowInExNtv/FlowOutExNtv/SplyExNtv | 2009/2015 → daily | /home/user/data/coinmetrics (btc, eth) |
| blockchain.com charts | api.blockchain.info/charts | 200 OK | full | not fetched |
| mempool.space | /api/v1/mining/hashrate/3y | 200 OK | 3y | not fetched |
| FRED csv | fred.stlouisfed.org/graph/fredgraph.csv | 200 OK | | not fetched |
| CryptoCompare | min-api histohour | **401 key required** | | |
| stooq | csv | timeout | | |

Fetcher: `edges/research3/fetch_sources.py` (functions per source; reused by strategy files for live data).
