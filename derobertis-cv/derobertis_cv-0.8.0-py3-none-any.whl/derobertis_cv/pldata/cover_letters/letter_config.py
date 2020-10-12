from typing import List

from derobertis_cv.pldata.authors import AUTHORS
from derobertis_cv.pldata.constants.authors import NIMAL, ANDY
from derobertis_cv.pldata.cover_letters.models import CoverLetter, ApplicationComponents, ApplicationFocus, \
    CoverLetterDesireSection
from derobertis_cv.pldata.organizations import SEC_DERA_TARGET, OFR_TARGET, RICH_FED_TARGET, PLACEHOLDER_GOV_TARGET
from derobertis_cv.pldata.universities import EL_PASO_TARGET, DRAKE_TARGET, PLACEHOLDER_UNIVERSITY_TARGET, \
    MONASH_TARGET, OREGON_STATE_TARGET, FIU_TARGET, UWM_TARGET


def get_cover_letters() -> List[CoverLetter]:
    all_concrete_components = [comp for comp in ApplicationComponents if comp != ApplicationComponents.OTHER_RESEARCH]

    return [
        CoverLetter(
            PLACEHOLDER_GOV_TARGET,
            [
"""
(Organization-specific paragraph)
""",
            ],
            included_components=all_concrete_components,
            focus=ApplicationFocus.GOVERNMENT,
        ),
        CoverLetter(
            PLACEHOLDER_UNIVERSITY_TARGET,
            [
                """
                (School-specific paragraph)
                """,
            ],
            included_components=all_concrete_components,
            focus=ApplicationFocus.ACADEMIC,
        ),
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
modeling skills that prepare students for FinTech roles, and the projects in the course are related to 
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
                ApplicationComponents.INVESTOR_ATTENTION_PAPER,
                ApplicationComponents.GOVERNMENT_INTERVENTION_PAPER,
            ],
            focus=ApplicationFocus.GOVERNMENT,
            font_scale=0.95,
            line_spacing=0.8,
        ),
        CoverLetter(
            MONASH_TARGET,
            [
"""
I believe I am an ideal fit at MU given that you are looking for an applicant with research and 
teaching experience in complex financial instruments, financial modeling, and international
finance. As my job market paper develops a model of cryptocurrency valuation and tests it empirically,
it is related to the first two of those areas. The Government Equity Capital Market Intervention study analyzes 
the effects of the Bank of Japan intervening in equity markets through
ETF purchases so it is related to the third. Finally, by the time I would start I will have two years 
of experience teaching my Financial Modeling course. On a personal level, my wife and I have been interested 
in living abroad and would like to be in a larger city with warm weather so Melbourne seems like a great fit.
"""
            ],
            included_components=[
                ApplicationComponents.CV,
                ApplicationComponents.JOB_MARKET_PAPER,
            ],
            focus=ApplicationFocus.ACADEMIC,
            line_spacing=1.1,
            by_email=True,
        ),
        CoverLetter(
            OREGON_STATE_TARGET,
            [
"""
My multiple lines of research and strong work ethic will contribute to the College of Business' goal of preeminence in 
research. Further, I will contribute to the goals of innovation and transformative, accessible education. 
It may already be apparent that I am not the typical Finance Ph.D. applicant: I have a much
larger emphasis on creating open-source software. My commitment to open-source is a commitment to inclusion and 
diversity: I believe everyone should have access to these tools regardless of their economic position, 
and that anyone should be able to learn from them, regardless of their location in the world or cultural 
background. I have already built tools for both research and education, and I want to continue innovating
at a university that encourages such efforts. On a personal level, my wife and I have always wanted to move to the 
West Coast and we enjoy outdoor activities so Corvallis seems like a good fit.
"""
            ],
            included_components=[
                ApplicationComponents.CV,
                ApplicationComponents.TEACHING_STATEMENT,
                ApplicationComponents.RESEARCH_STATEMENT,
                ApplicationComponents.JOB_MARKET_PAPER,
                ApplicationComponents.GOVERNMENT_INTERVENTION_PAPER,
                ApplicationComponents.EVALUATIONS
            ],
            focus=ApplicationFocus.ACADEMIC,
            file_renames={
                ApplicationComponents.JOB_MARKET_PAPER: 'Job Market Paper',
            }
        ),
        CoverLetter(
            FIU_TARGET,
            CoverLetterDesireSection(FIU_TARGET, ApplicationFocus.ACADEMIC).to_pyexlatex(),
            included_components=[
                ApplicationComponents.CV,
                ApplicationComponents.JOB_MARKET_PAPER,
                ApplicationComponents.TRANSCRIPTS,
                ApplicationComponents.EVALUATIONS,
                ApplicationComponents.RESEARCH_STATEMENT,
                ApplicationComponents.TEACHING_STATEMENT,
            ],
            focus=ApplicationFocus.ACADEMIC,
            line_spacing=1.1,
            font_scale=1.05,
        ),
        CoverLetter(
            UWM_TARGET,
            CoverLetterDesireSection(UWM_TARGET, ApplicationFocus.ACADEMIC).to_pyexlatex(),
            included_components=[
                ApplicationComponents.CV,
                ApplicationComponents.JOB_MARKET_PAPER,
                ApplicationComponents.REFERENCES,
            ],
            focus=ApplicationFocus.ACADEMIC,
            line_spacing=1.1,
            font_scale=1.05,
        )
    ]
