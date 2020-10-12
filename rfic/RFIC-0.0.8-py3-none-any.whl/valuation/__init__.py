# hide

import os
from collections import defaultdict
from datetime import datetime
from math import sqrt

import pandas as pd
import requests
from pyfinmod.basic import npv
from pyfinmod.ev import dcf, fcf
from pyfinmod.ev import enterprise_value
# from pyfinmod.financials import Financials
from pyfinmod.wacc import tax_rate
from pyfinmod.wacc import total_debt
from pyfinmod.wacc import wacc


class ParserError(Exception):
    pass


class Financials:
    """Financial data parser

    Parameters:
    ticker : str
        Public company ticker to fetch the financial data of (e.g. 'AAPL')

    """
    api = (os.environ["fmp_api"])

    base_url = "https://financialmodelingprep.com/api/v3/"
    datatypes = {
        "balance_sheet_statement": base_url + "financials/balance-sheet-statement/{}?apikey=" + api,
        "cash_flow_statement": base_url + "financials/cash-flow-statement/{}?apikey=" + api,
        "income_statement": base_url + "financials/income-statement/{}?apikey=" + api,
        "profile": base_url + "company/profile/{}?apikey=" + api,
    }

    def __init__(self, ticker):
        self.ticker = ticker
        self._balance_sheet_statement = None
        self._cash_flow_statement = None
        self._income_statement = None
        self._profile = None

    @staticmethod
    def _date_parse(date_str):
        """Parse dates and then convert from datetime.datetime to datetime.date

        """
        return datetime.strptime(date_str, "%Y-%m-%d").date()

    @staticmethod
    def _json_to_df(json):
        """Convert JSON to pd.DataFrame

        To be used for balance_sheet_statement, cash_flow_statement, and income_statement only

        """
        _r = defaultdict(list)
        keys = [i for i in json[0].keys() if i != "date"]
        _r["Items"] = keys
        for row in json:
            _r[Financials._date_parse(row["date"])] = [
                float(v) for k, v in row.items() if k in keys
            ]

        df = pd.DataFrame.from_dict(_r)
        df = df.set_index("Items")
        return df

    def _fetch_json(self, datatype):
        """Fetch the requested datatype from the corresponding URL provided in self.datatype class variable

        """
        try:
            url = self.datatypes[datatype].format(self.ticker)
            res = requests.get(url, timeout=5)
        except requests.exceptions.RequestException as e:
            raise ParserError("Failed to get data from external API {}".format(e))
        else:
            json = res.json()
            if not json:
                raise ParserError("Empty response from external API")
            return json

    def __getattr__(self, name):
        """Return financial data stored as attribute


        If balance sheet, cash flow statement, or income statement is requested then return a pd.DataFrame.
        If profile is requested then return a dictionary (JSON format).
        Otherwise, attempt to search self.profile for the requested data and return the corresponding value if found.

        """
        if name in ["balance_sheet_statement", "cash_flow_statement", "income_statement"]:
            cached_value = getattr(self, "_" + name, None)
            if cached_value is not None:
                return cached_value
            else:
                json_data = self._fetch_json(name)["financials"]
                df = self._json_to_df(json_data)
                setattr(self, "_" + name, df)
                return df
        elif name in ["profile"]:
            cached_value = getattr(self, "_" + name, None)
            if cached_value is not None:
                return cached_value
            else:
                json_data = self._fetch_json(name)["profile"]
                setattr(self, "_" + name, json_data)
                return json_data
        else:
            json_data = self.profile
            return float(json_data.get(name, 0))


# Calculate WACC


# hide


class rfic_models:
    def __init__(self, ticker, tickerList):
        self.ticker = ticker
        self.tickerList = tickerList

    def dcf(fcfs, wacc, short_term_growth, long_term_growth):
        latest_fcf_date = fcfs.index.max()
        dates = pd.date_range(latest_fcf_date, periods=6, freq="365D")[1:]
        future_cash_flows = [fcfs[latest_fcf_date]]
        for i in range(5):  # 5?
            next_year_fcf = future_cash_flows[-1] * (1 + short_term_growth)
            future_cash_flows.append(next_year_fcf)
        future_cash_flows = future_cash_flows[1:]
        df = pd.DataFrame(data={"fcf": future_cash_flows, "date": dates})
        # df.set_index('date', inplace=True)
        df["terminal value"] = 0
        last_index = df.index[-1]
        last_short_term_fcf = df.at[last_index, "fcf"]
        df.at[last_index, "terminal value"] = (
                last_short_term_fcf * (1 + long_term_growth) / (wacc - long_term_growth)
        )
        df["cash flow"] = df[["fcf", "terminal value"]].apply(sum, axis=1)
        return npv(df, wacc) * sqrt((1 + wacc))
    def dcf_n1Shock(fcfs, wacc, SHOCK, short_term_growth, long_term_growth):
        latest_fcf_date = fcfs.index.max()
        dates = pd.date_range(latest_fcf_date, periods=6, freq="365D")[1:]
        future_cash_flows = [fcfs[latest_fcf_date]]
        for i in range(5):  # 5?
            # print(i)
            # print(SHOCK)
            if i == 0:
                next_year_fcf = future_cash_flows[-1] * (1 + short_term_growth)
                future_cash_flows.append(next_year_fcf * SHOCK)

            else:

                next_year_fcf = future_cash_flows[-1] * (1 + short_term_growth)
                future_cash_flows.append(next_year_fcf)

        future_cash_flows = future_cash_flows[1:]
        df = pd.DataFrame(data={"fcf": future_cash_flows, "date": dates})
        # df.set_index('date', inplace=True)
        df["terminal value"] = 0
        last_index = df.index[-1]
        last_short_term_fcf = df.at[last_index, "fcf"]
        df.at[last_index, "terminal value"] = (
                last_short_term_fcf * (1 + long_term_growth) / (wacc - long_term_growth)
        )
        df["cash flow"] = df[["fcf", "terminal value"]].apply(sum, axis=1)
        return npv(df, wacc) * sqrt((1 + wacc))


    def fcf_dcf_using_wacc(RFR, mkt_return, SR_g, LR_g, shock, subjectCompany=self.ticker):
        # print(fcf_dcf_using_wacc(RFR,mkt_return,SR_g,LR_g))
        parser = Financials(subjectCompany)
        lec = (parser.balance_sheet_statement.iloc[-5::5])

        for i in lec.itertuples():
            ec = (i._1)
            break

        parser = Financials(subjectCompany)
        parser.income_statement.columns
        currentPrice = parser.price

        # parser = Financials(subjectCompany)
        ev = enterprise_value(parser.balance_sheet_statement)[0]
        ecToev = ec / ev
        equitys_share = (1 - ecToev)

        # parser = Financials(subjectCompany)
        fcf_value = fcf(parser.cash_flow_statement)
        total_debt(parser.balance_sheet_statement)
        tax_rate(parser.income_statement)
        parser.mktCap

        # cost_of_debt(parser.balance_sheet_statement, parser.income_statement)

        # cost_of_equity(float(parser.beta), risk_free_interest_rate = RFR, market_return = mkt_return)
        # parser = Financials(subjectCompany)

        aapl_wacc = wacc(parser.mktCap,
                         parser.balance_sheet_statement,
                         parser.income_statement,
                         float(parser.beta),
                         risk_free_interest_rate=RFR,
                         market_return=mkt_return)

        # parser = Financials(subjectCompany)
        if shock:
            output = dcf_n1Shock(fcf(parser.cash_flow_statement), aapl_wacc, shock, short_term_growth=SR_g,
                                 long_term_growth=LR_g)
        else:
            output = dcf(fcf(parser.cash_flow_statement), aapl_wacc, short_term_growth=SR_g, long_term_growth=LR_g)

        value_per_share = output / (parser.income_statement.loc['Weighted Average Shs Out'][0])

        pps = equitys_share * value_per_share

        IR = ((pps - currentPrice) / currentPrice) * 100

        out = (value_per_share, pps, SR_g, LR_g, IR)
        return (out)
        # return float(value_per_share)


    def dcf_g_range_simple(RFR, mkt_return, SR_g_scenarios, LR_g):
        colz = ('Firm Value/Share ($)', 'Equity Value/Share ($)', 'SR CAGR', 'LR CAGR', 'Implied ROI (%)')
        records_dcf_1 = [colz]
        for i in range(len(SR_g_scenarios)):
            time.sleep(2)
            SR_g = SR_g_scenarios[i]
            records_dcf_1.append(fcf_dcf_using_wacc(RFR, mkt_return, SR_g, LR_g, False))
            # print(records_dcf_1)
            print("Done computing ", (i + 1), ' DCF out of ', len(SR_g_scenarios))

        dcf_growth_rates_outputs = pd.DataFrame.from_records(records_dcf_1, columns=list(records_dcf_1[0]))
        ind = (dcf_growth_rates_outputs.columns[4])
        out = dcf_growth_rates_outputs
        out = out.iloc[1:]
        out['Annual Growth Rate (%)'] = [i * 100 for i in (SR_g_scenarios)]

        return out


    def dcf_g_range_shock(RFR, mkt_return, SR_g_scenarios, LR_g, revenue_growth_decline_rate_shock):
        colz = ('Firm Value/Share ($)', 'Equity Value/Share ($)', 'SR CAGR', 'LR CAGR', 'Implied ROI (%)')
        records_dcf_1 = [colz]
        for i in range(len(SR_g_scenarios)):
            time.sleep(2)
            SR_g = SR_g_scenarios[i]
            records_dcf_1.append(fcf_dcf_using_wacc(RFR, mkt_return, SR_g, LR_g, revenue_growth_decline_rate_shock))
            # print(records_dcf_1)
            print("Done computing ", (i + 1), ' DCF out of ', len(SR_g_scenarios))

        dcf_growth_rates_outputs_shock = pd.DataFrame.from_records(records_dcf_1, columns=list(records_dcf_1[0]))
        out = dcf_growth_rates_outputs_shock
        out = out.iloc[1:]
        out['Annual Growth Rate (%)'] = [i * 100 for i in (SR_g_scenarios)]

        return out


    def peer_dcf_comparison(RFR, mkt_return, LR_g, SR_g,shock, tickerList=self.tickerList):
        colz = ('Firm Value/Share ($)', 'Equity Value/Share ($)', 'SR CAGR', 'LR CAGR', 'Implied ROI (%)')
        tList = []
        records_dcf_2 = []
        for i in tickerList:
            print(i)
            time.sleep(2)
            try:
                # time.sleep(1)
                records_dcf_2.append(fcf_dcf_using_wacc(RFR, mkt_return, SR_g, LR_g, shock, i))
                tList.append(i)
            # print(records_dcf_1)
            except:
                pass
        peer_dcf = pd.DataFrame.from_records(records_dcf_2, columns=colz)

        peer_dcf['ticker'] = tList
        peer_dcf.set_index('ticker', inplace=True)
        return peer_dcf
