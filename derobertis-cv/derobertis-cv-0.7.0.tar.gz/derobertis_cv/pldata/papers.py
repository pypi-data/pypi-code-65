from dataclasses import dataclass
from typing import Optional, Sequence, Any, List

import pyexlatex.resume as lr

from derobertis_cv.models.category import CategoryModel
from derobertis_cv.pldata.authors import CO_AUTHORS
from derobertis_cv.pldata.research_categories import CATEGORIES
from derobertis_cv.pldata.constants.authors import (
    ANDY,
    NIMAL,
    SUGATA,
    CORBIN,
    JIMMY
)
from derobertis_cv.pltemplates.coauthor import CoAuthor


@dataclass
class ResearchProjectModel:
    title: str
    co_authors: Optional[Sequence[CoAuthor]] = None
    href: Optional[str] = None
    description: Optional[str] = None
    latex_description: Optional[Any] = None
    categories: Optional[Sequence[CategoryModel]] = None
    wip: bool = False
    
    def to_pyexlatex_publication(self, include_description: bool = True) -> lr.Publication:
        if not include_description:
            description = None
        else:
            description = self.latex_description or self.description

        return lr.Publication(
            self.title,
            co_authors=self.co_authors,
            href=self.href,
            description=description
        )

    @staticmethod
    def list_to_pyexlatex_publication_list(models: List['ResearchProjectModel'], include_descriptions: bool = True):
        return [model.to_pyexlatex_publication(include_description=include_descriptions) for model in models]


def get_working_papers():
    crypto_latex_description = """
    Cryptoassets represent a novel asset class in which tokens are generated and transacted
    using cryptography through blockchains. To date, few studies have attempted to derive a
    fundamental valuation for a cryptocurrency. I developed a model based on the Quantity
    Theory of Money (QTM) that informs us about fundamental value of a currency, and applied it 
    to understand cryptocurrency valuation. For most cryptocurrencies, an expectation
    of future use as a currency drives the valuation. I analyzed attention, sentiment, and R&D
    measures as proxies that form this expectation, and found that they are all significantly
    related to cryptocurrency returns. A portfolio that was long high attention cryptocurrencies
    with weekly rebalancing would have earned a 0.58% daily alpha from mid-2017 to the end
    of 2019. The portfolio which is long high attention cryptocurrencies and short low attention 
    cryptocurrencies has an even higher daily alpha of 0.72%, though it is not currently a
    tradeable strategy due to short-sale constraints. A portfolio formed from cryptocurrencies
    with high investor sentiment would have yielded a 0.33% daily alpha. R&D does not show
    as strong effects, but is still significantly related, and all the proxies for future usage remain
    significant with a variety of analyses and controls including other crypto market factors such
    as $MKT_c$, $SMB_c$, and $UMD_c$, and dual portfolio sorts on maturity, size, and momentum.
    """
    crypto_description = (
        crypto_latex_description
            .replace('$MKT_c$', 'MKT')
            .replace('$SMB_c$', 'SMB')
            .replace('$UMD_c$', 'UMD')
    )


    return [
        ResearchProjectModel(
            'Valuation without Cash Flows: What are Cryptoasset Fundamentals?',
            description=crypto_description,
            latex_description=crypto_latex_description,
            categories=[
                CATEGORIES['Alternative Assets'],
                CATEGORIES['Crypto-assets'],
                CATEGORIES['Asset Pricing'],
                CATEGORIES['Portfolio Analysis'],
                CATEGORIES['Investor Attention'],
                CATEGORIES['Investor Sentiment'],
            ]
        ),
        ResearchProjectModel(
            'Government Equity Capital Market Intervention and Stock Returns',
            [CO_AUTHORS[ANDY], CO_AUTHORS[NIMAL]],
            description="""
            As part of their market intervention strategy, the Bank of Japan (BOJ) has been purchasing 
            shares of ETFs tracking Japan’s major stock indices, reaching as much as ¥16.3 trillion
            in holdings by December of 2017. We show that firms that end up with high BOJ ownership
            have 1.78% higher daily returns and alpha of 0.29% in the window of (-1, 1) around BOJ purchase 
            days compared to firms with no ownership. We further show that there are significant
            price distortion effects as the BOJ purchases assets proportionally to their index weighting
            and not their market value. We analyze the Nikkei 225 as a price-weighted target index,
            and provide evidence that firms with high price-weightings but low market capitalization
            out-perform by 9.12% annually compared to the average firm. We show evidence that this
            out-performance is due to higher Bank of Japan ownership.
            """,
            categories=[
                CATEGORIES['Asset Pricing'],
                CATEGORIES['Portfolio Analysis'],
                CATEGORIES['Market Intervention'],
                CATEGORIES['Monetary Policy'],
                CATEGORIES['International Finance'],
            ]
        ),
        ResearchProjectModel(
            'Are Investors Paying (for) Attention?',
            description="""
            I examine the informativeness of investor attention on pricing of
            assets by using a new proxy based on Google search data. In contrast to prior
            studies using Google data, my new proxy contains cross-sectional firm attention information
            in addition to time-series information. I focus on firms that consistently 
            receive high or low attention, rather than attention-grabbing events.
            I find that firms with low attention outperform firms with high attention by
            8.16% annually, and after isolating the unique information in search volume
            and removing the impact of attention-grabbing events, the outperformance is
            still statistically and economically significant at 6.36% annually.
            """,
            categories=[
                CATEGORIES['Asset Pricing'],
                CATEGORIES['Portfolio Analysis'],
                CATEGORIES['Investor Attention'],
                CATEGORIES['Behavioral Finance'],
            ]
        ),
        ResearchProjectModel(
            'OSPIN: Informed Trading in Options and Stock Markets',
            [CO_AUTHORS[JIMMY], CO_AUTHORS[NIMAL], CO_AUTHORS[SUGATA]],
            description="""
            To gain a better understanding of the role of information in the price discovery
            of stock and option markets,  
            we propose and estimate a joint structural model of trading in both markets, yielding
            correlated directional informed trading in both markets, informed
            volatility trading in the option market, and correlated (buy/sell) liquidity trades in both
            markets. The model parameters and the probabilities of informed and liquidity trading in
            both markets are estimated using signed high frequency stock and options trading data for
            different option contracts. We find that moneyness and maturity play an important role in
            informed trading and on the microstructure price discovery of the stock and options markets.
            Further, we find the high frequency informed trading measures in the options market spike just 
            before earnings announcements and remain high for a few days after the announcement.
            """,
            categories=[
                CATEGORIES['Options'],
                CATEGORIES['Volatility'],
                CATEGORIES['Informed Trading'],
                CATEGORIES['Liquidity'],
            ]
        )
    ]


def get_works_in_progress():
    return [
        ResearchProjectModel(
            'Explaining the Cross-Section of Cryptocurrency Returns',
            description="""
            There are thousands of cryptocurrencies, but no model to explain their price movements.
            One cryptocurrency stands out in terms of its public awareness and market capitalization: Bitcoin.
            Anecdotal evidence suggests that cryptocurrency returns are related to Bitcoin returns. This study
            seeks to determine a pricing model which relates individual cryptocurrency returns to Bitcoin returns.
            """,
            categories=[
                CATEGORIES['Alternative Assets'],
                CATEGORIES['Crypto-assets'],
                CATEGORIES['Asset Pricing'],
                CATEGORIES['Portfolio Analysis'],
            ],
            wip=True
        ),
        ResearchProjectModel(
            'Does Government Equity Market Intervention Affect Liquidity and Volatility?',
            [CO_AUTHORS[ANDY], CO_AUTHORS[NIMAL]],
            description="""
            Bank of Japan (BOJ) ETF purchases have resulted in the BOJ owning more than 60% of total outstanding 
            ETFs by December of 2017. Considering such a large volume of purchases, we focus on liquidity effects in 
            both the ETF market and the market for the
            underlying shares. Further, as the BOJ is only purchasing 
            and not selling, we examine how downside volatility decreases.
            """,
            categories=[
                CATEGORIES['Market Intervention'],
                CATEGORIES['Monetary Policy'],
                CATEGORIES['International Finance'],
                CATEGORIES['Volatility'],
            ],
            wip=True
        ),
        ResearchProjectModel(
            'The Effect of Equity Market Intervention on Corporate Financing',
            [CO_AUTHORS[ANDY], CO_AUTHORS[NIMAL]],
            description="""
            We show in prior work that
            stock prices of the underlying firms increase in response to Bank of Japan (BOJ) purchases of ETFs of major
            stock indices. Considering a higher share value, firms should
            be more likely to choose equity than debt when raising capital. This effect may be mediated by the low
            cost of debt during this time period.
            """,
            categories=[
                CATEGORIES['Market Intervention'],
                CATEGORIES['Monetary Policy'],
                CATEGORIES['International Finance'],
                CATEGORIES['Corporate Financing'],
                CATEGORIES['Equity'],
                CATEGORIES['Debt'],
            ],
            wip=True
        ),
        ResearchProjectModel(
            'How do CEOs Respond to Public and Investor Scrutiny?',
            [CO_AUTHORS[CORBIN]],
            description="""
            In the United States, there has been a trend towards increased public scrutiny of CEO pay, in both the 
            press and in regulation. As far as regulation, first companies had to release a summary table of 
            compensation, then "Say on Pay" legislation was introduced so that shareholders vote to approve the CEO
            compensation. We examine the quantity and quality of CEOs that move from the public sector to the 
            private sector, using regulatory changes as exogenous shocks. 
            """,
            categories=[
                CATEGORIES['Executive Compensation'],
                CATEGORIES['Investor Scrutiny'],
                CATEGORIES['Regulation'],
            ],
            wip=True
        ),
        ResearchProjectModel(
            'Do Insiders Learn From Short Sellers?',
            [CO_AUTHORS[CORBIN]],
            description="""
            Differing groups of investors, such as insiders, short-sellers, and analysts, have different information 
            sets on which to trade. While the use and transmission of information by insiders has been extensively 
            studied, there is a lack of research on how insiders learn from external investors such as short-sellers.
            We examine the response of insider trading to surprises in short interest.
            """,
            categories=[
                CATEGORIES['Insider Trading'],
                CATEGORIES['Short Sales'],
                CATEGORIES['Information Transmission'],
            ],
            wip=True
        ),
    ]
