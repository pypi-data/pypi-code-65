import warnings

import altair as alt
import finviz
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import requests
from bs4 import BeautifulSoup
from yahoo_fin.stock_info import get_quote_table, get_stats, get_live_price
from yahoofinancials import YahooFinancials

warnings.filterwarnings('ignore')

pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)


def getQuote(ticker):
    return str(round(get_live_price(ticker), 2))


def finviz_summaryTable(symbols):
    # Get Column Header
    req = requests.get("https://finviz.com/quote.ashx?t=FB")
    soup = BeautifulSoup(req.content, 'html.parser')
    table = soup.find_all(lambda tag: tag.name == 'table')
    rows = table[8].findAll(lambda tag: tag.name == 'tr')
    out = []
    for i in range(len(rows)):
        td = rows[i].find_all('td')
        out = out + [x.text for x in td]

    ls = ['Ticker', 'Sector', 'Sub-Sector', 'Country'] + out[::2]

    dict_ls = {k: ls[k] for k in range(len(ls))}
    df = pd.DataFrame()
    print('Fetching Data...')
    for j in range(len(symbols)):

        try:

            req = requests.get("https://finviz.com/quote.ashx?t=" + symbols[j])
            if req.status_code != 200:
                continue
            soup = BeautifulSoup(req.content, 'html.parser')
            table = soup.find_all(lambda tag: tag.name == 'table')
            rows = table[6].findAll(lambda tag: tag.name == 'tr')
            sector = []
            for i in range(len(rows)):
                td = rows[i].find_all('td')
                sector = sector + [x.text for x in td]
            sector = sector[2].split('|')
            rows = table[8].findAll(lambda tag: tag.name == 'tr')
            out = []
            for i in range(len(rows)):
                td = rows[i].find_all('td')
                out = out + [x.text for x in td]
            out = [symbols[j]] + sector + out[1::2]
            out_df = pd.DataFrame(out).transpose()
            df = df.append(out_df, ignore_index=True)
            print('Done!')

            df = df.rename(columns=dict_ls)

        except BaseException as E:
            print("Could not find data:", E)

    return (df)


def yf_summaryTable(tickerList):
    values = []
    for i in tickerList:
        try:
            value = get_quote_table(i, dict_result=True)
            values.append(value)
        except BaseException as e:
            print(e)

    outD = dict(zip(tickerList, values))

    return outD


def yf_stats_compTable(tickerList):
    values = []
    for i in tickerList:
        try:
            value = get_stats(i)
            values.append(value)
        except BaseException as e:
            print(e)

    outD = dict(zip(tickerList, values))

    return outD


def get_prices(tickerlist, start, end, period):
    yahoo_financials = YahooFinancials(tickerlist)
    jsonDATA = yahoo_financials.get_historical_price_data(start, end, period)
    return jsonDATA


def formatPeers(inputs):
    ColumnList = list(inputs.columns)
    yearList = list(inputs.Ticker)

    print(ColumnList)
    print(yearList)

    transposed = inputs.transpose()
    cleaned = transposed.reset_index()

    new_header = cleaned.iloc[0]  # grab the first row for the header
    cleaned = cleaned[1:]  # take the data less the header row
    cleaned.columns = new_header  # set the header row as the df header

    byYear = cleaned.set_index("Ticker").stack()

    df = pd.DataFrame(byYear, columns=['Value'])
    df.reset_index(inplace=True)
    print(df.columns)
    df.rename(columns={0: 'Ticker'}, inplace=True)
    df.dropna(inplace=True)
    df['Value'] = pd.to_numeric(df['Value'], errors='coerce')

    new_header = df.iloc[0]  # grab the first row for the header
    df = df[1:]  # take the data less the header row
    df.columns = new_header  # set the header row as the df header

    return df


def interactive_bat(data):
    source = data
    brush = alt.selection(type='interval', encodings=['x'])

    bars = alt.Chart().mark_bar().encode(
        x='Ticker:N',
        y='mean(Value):Q',
        opacity=alt.condition(brush, alt.OpacityValue(1), alt.OpacityValue(0.7)),
    ).add_selection(
        brush
    )

    line = alt.Chart().mark_rule(color='firebrick').encode(
        y='mean(Value):Q',
        size=alt.SizeValue(3)
    ).transform_filter(
        brush
    )

    graph = alt.layer(bars, line, data=source)

    return graph


def set_universe(subject_company, peer_list):
    peers = peer_list
    tickerList = []
    tickerList.append(subject_company)
    for i in peers:
        tickerList.append(i)

    return tickerList


def long_format_fins(inputs):
    ColumnList = list(inputs.columns)
    yearList = list(inputs.Year)

    # transposed = inputs.transpose()
    cleaned = inputs.rename_axis('Metric')

    # print(cleaned.columns)
    # cleaned.drop(cleaned.columns[0],inplace=True)
    byYear = cleaned.set_index('Year').stack()

    df = pd.DataFrame(byYear, columns=['Value'])
    df.reset_index(inplace=True)
    # print(df.columns)
    # print(df)
    df.rename(columns={'level_1': 'Metric'}, inplace=True)
    # df.dropna(inplace=True)
    # df['Value'] = pd.to_numeric(df['Value'], errors='coerce')
    # print(df)

    # print(df.columns)
    df = df[~df['Metric'].isin(['Value', 'index'])]
    # df = df.drop(['level_0','index'],axis=0)
    # print(df.Year)

    df.Year = df.Year.astype(str)
    return df


def make_multi_LineGraph(data, logged):
    try:
        df = data
        if logged == True:
            # old = np.seterr(invalid='ignore')
            df.replace(0, np.nan, inplace=True)
            df['log'] = np.around(np.log(df['Value']), 2)
            # np.seterr(**old)
            # print(df['log'])
            aY = ('log:Q')
            scc = alt.Scale(type='log')
            color1 = alt.Color('Metric:N',
                               legend=alt.Legend(title="Natural Log of Metrics", labelFontSize=15, titleFontSize=17),
                               scale=alt.Scale(scheme='category20b'))
        else:
            aY = ('Value:Q')
            scc = alt.Scale(type='linear')
            color1 = alt.Color('Metric:N', legend=alt.Legend(title="Metrics", labelFontSize=15, titleFontSize=17),
                               scale=alt.Scale(scheme='category20b'))
        label = alt.selection_multi(fields=['Metric'], bind='legend',
                                    on='mouseover',  # select on mouseover events
                                    nearest=True,  # select data point nearest the cursor
                                    empty='none'  # empty selection includes no data points
                                    )
        # define our base line chart of stock prices
        base = alt.Chart().mark_line().encode(
            alt.X('Year:T'),
            alt.Y(aY, scale=scc),
            color=color1

            # alt.Color(' Metric:N'), opacity = alt.condition(label, alt.value(1), alt.value(0.5))

        )

        graph = alt.layer(
            base,  # base line chart

            # add a rule mark to serve as a guide line
            alt.Chart().mark_rule(color='#1C00ff00').encode(
                x='Year:T'
            ).transform_filter(label),

            # add circle marks for selected time points, hide unselected points
            base.mark_circle().encode(
                opacity=alt.condition(label, alt.value(1), alt.value(0))
            ).add_selection(label),

            # add white stroked text to provide a legible background for labels
            base.mark_text(align='left', dx=5, dy=-5, stroke='white', strokeWidth=4).encode(
                text=aY
            ).transform_filter(label),

            # add text labels for stock prices
            base.mark_text(align='left', dx=5, dy=-5).encode(
                text=aY
            ).transform_filter(label),

            data=df
        ).properties(
            width=700,
            height=400
        )

        return graph
    except BaseException as e:
        print(e)
        pass


def wiki_russel_list():
    """
    Returns a list of the russell 1000 index
    """
    res = requests.get('https://en.wikipedia.org/wiki/Russell_1000_Index')
    # res = requests.get("http://www.nationmaster.com/country-info/stats/Media/Internet-users")
    soup = BeautifulSoup(res.content, 'lxml')
    a1 = soup.find_all('table')
    getReturns = a1[2]
    getTickers = a1[3]
    # print(a1)

    df1 = pd.read_html(str(getReturns))
    AnnualReturns = df1[0]
    # a1 = soup.find_all('table')[3]
    df2 = pd.read_html(str(getTickers))
    print(len(df2))
    russ1kList = df2[0]
    return russ1kList


def make_wide_ratio_table_finviz(tickerList):
    recs = []
    xyz = 0
    for i in tickerList:
        try:
            hold = [i]
            for b in (finviz.get_stock(i)):
                colls = (list((finviz.get_stock(i)).keys()))
                hold.append(finviz.get_stock(i)[b])
            recs.append(hold)
        except BaseException as e:
            print(e, "could not find", i)
    # print(colls)
    listCols = (list(['Ticker']))
    for i in colls:
        # print(i)
        listCols.append(i)

    # print(listCols)
    bigTable = pd.DataFrame.from_records(recs, columns=listCols)
    return bigTable


from scipy.stats import zscore


def make_subplotted_hist(bigTable):
    bt_c = bigTable
    bt_c = bt_c.apply(pd.to_numeric, args=('coerce',))
    bt_c = bt_c.apply(lambda x: x if np.std(x) == 0 else zscore(x))
    bt_c = bt_c.dropna(axis="columns").set_index(bigTable.Ticker)
    columns_list = bt_c.columns

    bt_c = bt_c.transpose()
    bt_c.index.name = "Metric"
    bt_c = bt_c.stack()
    bt_c = bt_c.to_frame().rename(columns={0: "Value"})
    df = bt_c
    indexer__ = 0
    indexList = []
    for i in df.itertuples():

        ii = (i.Index[0])
        if ii not in indexList:
            # print(ii)
            indexList.append(ii)

    # print(indexList)
    f, a = plt.subplots(len(indexList), 1, figsize=(60, 500), sharex=True)

    # indexer__ +=1
    for i in indexList:
        # print(i, indexer__)
        df.xs(i).plot(kind='bar', ax=a[indexer__], fontsize=30).set_ylabel(str("Z-Score of: " + i), fontsize=30)
        indexer__ += 1
    f.tight_layout(pad=3.0)

    # f.subplots_adjust(left=0.1, bottom=0.1, right=0.6, top=0.8)
    # f.axis("off")
    # plt.show()
    # plt.draw()
    # # fig1.savefig('tessstttyyy.png', dpi=100)
    f.savefig('comparative_figures.pdf')
