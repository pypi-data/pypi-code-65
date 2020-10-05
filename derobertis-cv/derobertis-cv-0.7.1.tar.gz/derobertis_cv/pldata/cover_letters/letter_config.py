from typing import List

from derobertis_cv.pldata.authors import AUTHORS
from derobertis_cv.pldata.constants.authors import NIMAL, ANDY
from derobertis_cv.pldata.cover_letters.models import CoverLetter, ApplicationComponents, ApplicationFocus
from derobertis_cv.pldata.organizations import SEC_DERA_TARGET, OFR_TARGET, RICH_FED_TARGET
from derobertis_cv.pldata.universities import EL_PASO_TARGET, DRAKE_TARGET


def get_cover_letters() -> List[CoverLetter]:
    return [
        CoverLetter(
            SEC_DERA_TARGET,
            [
"""
I believe I am an ideal fit at DERA as a Financial Economic Fellow given my related research in valuation,
corporate finance, and economic policy as well as technical skills related to developing economic models and
communicating insights from large quantities of data. I have a strong interest in regulatory issues in financial
markets and am equally comfortable being both self-guided and a team player providing high-quality results and
recommendations. Further, I have a locational preference towards Washington, DC as my family lives in
Northern Virginia, though I would be pleased to work at any potential DERA location.
""",
            ],
            included_components=[
                ApplicationComponents.CV,
                ApplicationComponents.TRANSCRIPTS,
                ApplicationComponents.JOB_MARKET_PAPER
            ],
            focus=ApplicationFocus.GOVERNMENT,
            included_references=(AUTHORS[ANDY], AUTHORS[NIMAL]),
            font_scale=0.93
        ),
        CoverLetter(
            EL_PASO_TARGET,
            [
"""
I believe I am an ideal fit at UTEP given that you are looking for an applicant in the area of investments and 
corporate finance, and I have research work in both. Further, the posting mentions FinTech under the preferred
specialties, and my Financial Modeling course is geared towards preparation for FinTech roles considering it 
combines finance knowledge and programming. On a personal level, my wife and I both have an affinity for 
mid-size cities and warm weather.
"""
            ],
            included_components=[
                ApplicationComponents.CV,
            ],
            focus=ApplicationFocus.ACADEMIC,
        ),
        CoverLetter(
            DRAKE_TARGET,
            [
"""
I believe I am an ideal fit at DU given that you are looking for an applicant who can teach corporate finance, 
valuation, and FinTech, and my Financial Modeling course hits on all these topics. I teach programming and 
modeling skills which prepare students for FinTech roles, and the projects in the course are related to 
DCF valuation and capital budgeting. Further, most of my research work involves valuation and my job market
paper is in the FinTech area due to the topic of cryptocurrencies. On a personal level, my wife and I both 
have an affinity for mid-size cities and outdoor activities so I think we would feel right at home in Des Moines.
"""
            ],
            included_components=[
                ApplicationComponents.CV,
                ApplicationComponents.JOB_MARKET_PAPER,
                ApplicationComponents.DIVERSITY,
                ApplicationComponents.TRANSCRIPTS,
                ApplicationComponents.EVALUATIONS,
            ],
            focus=ApplicationFocus.ACADEMIC,
        ),
        CoverLetter(
            OFR_TARGET,
            [
"""
I believe I am an ideal fit at OFR as a Research Economist given my related research in market microstructure and 
macroeconomics, as well as technical skills related to developing economic models and
communicating insights from large quantities of data. I have a strong interest in regulatory issues in financial
markets and am equally comfortable being both self-guided and a team player providing high-quality results and
recommendations. Further, I have a locational preference towards Washington, DC as my family lives in
Northern Virginia. Should I be selected, I would like to start at the end of July or beginning of August, but
I can be flexible on the timing.
"""
            ],
            included_components=[
                ApplicationComponents.CV,
                ApplicationComponents.JOB_MARKET_PAPER
            ],
            focus=ApplicationFocus.GOVERNMENT,
            as_email=True
        ),
        CoverLetter(
            RICH_FED_TARGET,
            [
"""
I believe I am an ideal fit at the Richmond Fed as a Financial Economist given my related research in market microstructure, 
macroeconomics, and economic policy as well as technical skills related to developing economic models and
communicating insights from large quantities of data. I am familiar with the Fed's supervisory work from both ends: 
I was an intern in the Credit Risk department at the Board of Governors and I worked directly with examiners in my 
role as a Portfolio Analyst rebuilding the models for the Allowance for Loan and Lease Losses at 
Eastern Virginia Bankshares. 
I have a strong interest in regulatory issues in financial
markets and am equally comfortable being both self-guided and a team player providing high-quality results and
recommendations. On a personal level, my wife and I both 
have an affinity for larger cities and my family is in Virginia so Charlotte and Baltimore would both be 
great locations for us.
"""
            ],
            included_components=[
                ApplicationComponents.CV,
                ApplicationComponents.JOB_MARKET_PAPER,
                ApplicationComponents.OTHER_RESEARCH
            ],
            focus=ApplicationFocus.GOVERNMENT,
            font_scale=0.95,
            line_spacing=0.8,
        )
    ]
