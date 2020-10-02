from findatapy.market import MarketDataGenerator, Market, MarketDataRequest

md_request = MarketDataRequest(start_date='01 Jun 2017', tickers='EURUSD', data_source='bloomberg',
                               fields='close', category='fx')

market = Market(market_data_generator=MarketDataGenerator())

df = market.fetch_market(md_request)

print(df)

from chartpy import Chart

Chart(engine='plotly').plot(df)