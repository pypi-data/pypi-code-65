from findatapy.market import Market, MarketDataRequest, MarketDataGenerator

market = Market(market_data_generator=MarketDataGenerator())

md_request = MarketDataRequest(start_date='07 Feb 2020', finish_date='20 Feb 2020', cut='LOC',
freq='daily', data_source='binance', category='crypto',
fields=['close', 'volume', 'quote-asset-volume'],
tickers=['XBTUSDT'])

df = market.fetch_market(md_request)
print(df.head(5))
print(df.tail(5))