from dataclasses import dataclass, field
from enum import Enum
from typing import Sequence, List, Optional, Union, Dict

import inflect
from pyexlatex.logic.format.and_join import join_with_commas_and_and
from pyexlatex.models.format.text.linespacing import LineSpacing
from pyexlatex.typing import PyexlatexItems, PyexlatexItem
import pyexlatex as pl

from derobertis_cv.models.organization import Organization, OrganizationCharacteristics
from derobertis_cv.plbuild.paths import DOCUMENTS_BUILD_PATH, images_path
from derobertis_cv.pldata.authors import Author, AUTHORS
from derobertis_cv.pldata.constants.authors import ANDY, NIMAL, BAOLIAN
from derobertis_cv.pldata.constants.contact import SITE_URL, EMAIL, PHONE, ADDRESS_LINES, NAME, FIRST_NAME
from derobertis_cv.pldata.courses.fin_model import get_fin_model_course


class ApplicationComponents(str, Enum):
    CV = 'CV'
    JOB_MARKET_PAPER = 'Job market paper'
    GOVERNMENT_INTERVENTION_PAPER = 'Government intervention paper'
    INVESTOR_ATTENTION_PAPER = 'Investor attention paper'
    OTHER_RESEARCH = 'Other research work'
    RESEARCH_STATEMENT = 'Research statement'
    TEACHING_STATEMENT = 'Teaching statement'
    COURSE_OUTLINES = 'Course outlines'
    TRANSCRIPTS = 'Graduate transcripts'
    EVALUATIONS = 'Teaching evaluations'
    DIVERSITY = 'Diversity statement'
    COVER_LETTER = 'Cover Letter'
    REFERENCES = 'References'

    @staticmethod
    def aggregate(components: Sequence['ApplicationComponents'],
                  include_references: bool = False) -> List['ApplicationComponents']:
        out_comps: List['ApplicationComponents'] = []
        for comp in components:
            if comp in (
                ApplicationComponents.GOVERNMENT_INTERVENTION_PAPER,
                ApplicationComponents.INVESTOR_ATTENTION_PAPER
            ) and ApplicationComponents.OTHER_RESEARCH not in out_comps:
                out_comps.append(ApplicationComponents.OTHER_RESEARCH)
            elif not include_references and comp == ApplicationComponents.REFERENCES:
                continue
            else:
                out_comps.append(comp)
        return out_comps


class ApplicationFocus(str, Enum):
    ACADEMIC = 'academic'
    GOVERNMENT = 'government'


class Gender(str, Enum):
    MALE = 'male'
    FEMALE = 'female'


@dataclass
class HiringManager:
    last_name: str
    first_name: Optional[str] = None
    gender: Optional[Gender] = None
    title: Optional[str] = None
    is_doctor: bool = False
    married: bool = False
    is_person: bool = True
    
    @property
    def prefix(self) -> str:
        if not self.is_person:
            return ''
        if self.is_doctor:
            return 'Dr. '
        if self.gender == Gender.MALE:
            return f'Mr. '
        if self.gender == Gender.FEMALE:
            if self.married:
                return f'Mrs. '
            else:
                return f'Ms. '
        return ''

    @property
    def salutation_name(self) -> str:
        if not self.prefix:
            return self.full_name
        else:
            return f'{self.prefix}{self.last_name}'

    @property
    def full_name_with_prefix(self) -> str:
        return f'{self.prefix}{self.full_name}'

    @property
    def full_name_prefix_only_for_doctor(self) -> str:
        if self.is_doctor:
            return f'{self.prefix}{self.full_name}'
        return self.full_name
    
    @property
    def full_name(self) -> str:
        if self.first_name is None:
            return self.last_name
        else:
            return f'{self.first_name} {self.last_name}'


@dataclass
class ApplicationTarget:
    organization: Organization
    position_name: str
    person: Optional[HiringManager] = None

    def __post_init__(self):
        if self.person is None:
            self.person = HiringManager(
                f'{self.organization.abbreviation} Hiring Committee',
                is_person=False
            )


@dataclass
class CoverLetter:
    target: ApplicationTarget
    target_specific_content: PyexlatexItems
    included_components: Sequence[ApplicationComponents]
    focus: ApplicationFocus
    included_references: Sequence[Author] = (AUTHORS[ANDY], AUTHORS[NIMAL], AUTHORS[BAOLIAN])
    font_scale: float = 1
    line_spacing: float = 1
    as_email: bool = False
    by_email: bool = False
    file_renames: Optional[Dict[ApplicationComponents, str]] = field(
        default_factory=lambda: {ApplicationComponents.CV: 'Nick DeRobertis CV'}
    )

    def to_pyexlatex(self, output: bool = True, out_folder: str = DOCUMENTS_BUILD_PATH) -> pl.LetterDocument:
        contents = [
            self.blue,
            self.intro_paragraph,
            *self.desire_content,
            self.app_package(email=self.as_email),
            self.action_paragraph,
        ]

        packages = [
            pl.Package('geometry', modifier_str='margin=0.75in'),
            pl.Package('hyperref', modifier_str='hidelinks'),
            'graphicx',
        ]

        pre_env_contents = []
        signer_contents = []

        if not self.as_email:
            packages.append('fontspec')
            font_str = (
                r'\setmainfont{Latin Modern Roman}[Scale =' +
                str(self.font_scale) +
                ',Ligatures = {Common, TeX}]'
            )
            pre_env_contents.append(pl.Raw(font_str))
            signer_contents.extend([
                pl.VSpace(-1.6),
                pl.Graphic(images_path('signature.png'), width='5cm'),
                pl.OutputLineBreak(),
                NAME
            ])
        else:
            signer_contents.extend([pl.Raw(r'\HCode{<br>}'), NAME])

        if self.line_spacing != 1:
            packages.extend([
                'setspace',
                LineSpacing(self.line_spacing)
            ])

        saluation = f'Dear {self.target.person.salutation_name if self.target.person else "Sir or Madam"}:'


        letter = pl.LetterDocument(
            contents,
            contact_info=[NAME, *ADDRESS_LINES],
            to_contact_info=self.to_contact_info,
            signer_name=signer_contents,
            salutation=saluation,
            packages=packages,
            pre_env_contents=pre_env_contents,
            font_size=11,
        )

        if output:
            if self.as_email:
                letter.to_html(out_folder, outname=f'{self.target.organization.abbreviation} Cover Letter')
            else:
                letter.to_pdf(out_folder, outname=f'{self.target.organization.abbreviation} Cover Letter')
            if self.by_email:
                email_contents = [
                    saluation,
                    '',
                    self.separate_email_intro,
                    self.app_package(email=True, include_cover_letter=True),
                    self.separate_email_conclusion,
                    '\n',
                    *self.separate_email_signature,
                ]
                email_doc = pl.Document(email_contents)
                email_doc.to_html(out_folder, outname=f'{self.target.organization.abbreviation} Email Body')

        return letter

    @property
    def separate_email_intro(self) -> str:
        p = inflect.engine()
        a_position = p.a(self.target.position_name)

        return f"""
I hope this email finds you well. My name is {NAME} and I would like to submit my application 
to be {a_position} at {self.target.organization.abbreviation}.
""".strip()

    @property
    def separate_email_conclusion(self) -> str:
        return f"""
you will also receive supporting reference letters from 
{self.recommenders_str}. Please do not hesitate to reach out to them.
If you have any questions, please do not hesitate to contact me by replying to this email 
or at {PHONE}. 
""".strip()

    @property
    def separate_email_signature(self) -> PyexlatexItems:
        return [
            'Best Regards,',
            '',
            pl.Raw(r'\HCode{<br>}'),
            FIRST_NAME,
        ]

    @property
    def to_contact_info(self) -> List[str]:
        contact_info = [
            self.target.person.full_name_prefix_only_for_doctor if self.target.person else "",
            self.target.organization.title,
        ]

        if self.target.organization.address_lines is not None:
            contact_info.extend(self.target.organization.address_lines)

        return contact_info

    @property
    def intro_paragraph(self) -> str:
        p = inflect.engine()
        a_position = p.a(self.target.position_name)
        if self.as_email:
            site_highlight = f' (see more detail at {self.site_link()}).'
        else:
            site_highlight = f'.{self.site_footnote}'
        return f"""
I am writing to express my interest and enthusiasm to be {a_position} at 
{self.target.organization.abbreviation} and to submit my supporting application materials.
My name is {NAME} and I am a Ph.D. candidate in Finance at the University of Florida (graduating in May 2021).
During the Ph.D., I produced four working papers, five works 
in progress, developed and taught two courses across six different semesters in person and online with 
up to 4.8/5 evaluations, and created 34 open
source software projects that improve the efficiency and reproducibility of empirical research{site_highlight}
In addition to establishing a strong economics and finance foundation
during my Ph.D. studies, I also developed a comprehensive and unique set of analytical and soft
skills---a high competency in programming, econometrics, economic modeling, data science, and
communication. {self.interest_sentence}
        """.strip()

    @property
    def interest_sentence(self) -> str:
        if self.focus == ApplicationFocus.ACADEMIC:
            return f"""
I want to bring my strong research and software pipeline, along with 
my high competency for teaching and fully developed Financial Modeling course{self.modeling_footnote} to 
{self.target.organization.abbreviation}.
            """.strip()
        elif self.focus == ApplicationFocus.GOVERNMENT:
            return ''
            return f"""
I want to bring all of these skills along with a strong work ethic to {self.target.organization.abbreviation}.
            """.strip()
        else:
            raise ValueError(f'no handling for focus {self.focus}')

    @property
    def desire_content(self) -> List[PyexlatexItem]:
        contents: List[PyexlatexItem] = []
        if self.focus == ApplicationFocus.ACADEMIC:
            contents.extend([self.research_overview, self.teaching_overview])
        elif self.focus == ApplicationFocus.GOVERNMENT:
            contents.append(self.government_overview)
        else:
            raise ValueError(f'no handling for focus {self.focus}')

        contents.append(self.target_specific_content)

        return contents

    @property
    def research_overview(self) -> str:
        return """
My research agenda focuses on financial markets: analyzing the role of both fundamental and behavioral
information in price discovery, the effects of government intervention, and the performance of assets. 
My study "Government Equity Capital Market Intervention and Stock Returns" with Andy 
Naranjo and Mahendrarajah Nimalendran informs central bank personnel about the effects of purchasing 
broad-index equity ETFs on asset prices over time, which is valuable information at a time when the 
Federal Reserve is pursuing unprecedented levels of market intervention and even purchasing corporate debt. My job 
market paper, "Valuation without Cash Flows: What are Cryptoasset Fundamentals?" gives cryptocurrency investors 
both a theoretical framework and empirical models to assess the value of these assets, which could increase adoption and 
benefit society through elimination of counterparty risk, increased transparency, and speed of payments. 
My joint work on "OSPIN: Informed Trading in Options and Stock Markets" with
Yong Jin, Mahendrarajah Nimalendran, and Sugata Ray develops a new model to estimate the probability of informed 
trading that is more accurate as it considers the information in both the stock and options markets jointly, 
whereas prior models considered only stock markets,
which should be useful to researchers analyzing the information structure of markets and especially volatility 
information. Finally, my work on
"Are Investors Paying (for) Attention?" furthers the behavioral asset pricing literature focusing on investor attention,
the understanding of which may lead to more efficient prices as investors incorporate these effects into their 
valuation models. Each of my existing studies puts me down a path to do further research in those areas and I have 
a deep pipeline of works in progress.
        """

    @property
    def teaching_overview(self) -> str:
        return """
The common theme across the courses I've created and taught is a focus on preparing students for introductory
finance positions related to the course. I created Financial Modeling and Debt and Money Markets courses
from scratch to emphasize this focus and to de-emphasize institutional details that will be relevant for 
only a few students. I structure my courses to appeal to multiple learning types including auditory, visual, 
and kinesthetic learning and supplement by meeting with students to ensure that all students have an equal
opportunity to succeed. Financial Modeling is a capstone, senior course, which was previously taught using Excel but 
I have restructured it to focus mainly on Python skills. This is the first time a programming language has been taught
in an undergraduate finance course at UF, and one of only a handful of times a Ph.D. student has been allowed to 
teach a capstone course. I was granted this opportunity due to my teaching accolades, 4.8/5 evaluations and the 
Warrington College of Business Ph.D. Student Teaching Award, as well as my forward-thinking and technical skills.
        """

    @property
    def government_overview(self) -> str:
        return """
My research agenda focuses on financial markets: analyzing the role of both fundamental and behavioral
information in price discovery, the effects of government intervention, and the performance of assets. To
support my research agenda, I have developed a technical skill set that allows me to 
uncover novel data sets through 
web-scraping and API access, work with large data sets, and build
machine learning models to make predictions and classifications. 
        """

    def app_package(self, email: bool = False, include_cover_letter: bool = False) -> PyexlatexItems:
        included_components = ApplicationComponents.aggregate(self.included_components)
        components: List[Union[ApplicationComponents, str]]
        if len(included_components) < 4:
            if included_components[0] == ApplicationComponents.CV:
                components = [included_components[0].value]
            else:
                components = [included_components[0].casefold()]
            if len(included_components) > 1:
                components.extend([comp.casefold() for comp in included_components[1:]])
            if email:
                package = 'the application package attached to this email'
            else:
                package = 'this application package'
            if include_cover_letter:
                components.append(ApplicationComponents.COVER_LETTER.casefold())

            app_package = [
                f'In addition to {package} that includes my',
                join_with_commas_and_and(components)
            ]
            return app_package

        components = list(included_components)

        if email:
            intro = 'Attached to this email'
        else:
            intro = 'Within this application package'

        if include_cover_letter:
            components.append(ApplicationComponents.COVER_LETTER.casefold())

        included_components_bullets = pl.MultiColumn(
            pl.UnorderedList([comp.value if isinstance(comp, ApplicationComponents) else comp for comp in components]),
            3
        )

        return [
            f"{intro}, you will find the following components:",
            pl.VSpace(-0.2),
            included_components_bullets,
            pl.VSpace(-0.5),
            'In addition to this application package, '
        ]

    @property
    def action_paragraph(self) -> str:
        return f"""
you will also receive supporting reference letters from 
{self.recommenders_str}. Please do not hesitate to reach out to them.
{self.application_action_sentence}
If you have any questions, please do not hesitate to contact me. I am especially interested in 
{self.target.organization.abbreviation} given the excellent professional and personal fit. 
Please contact me at {EMAIL} or {PHONE}. 
        """.strip()

    @property
    def application_action_sentence(self) -> str:
        sentence = 'I also have '
        if self.focus == ApplicationFocus.ACADEMIC:
            if self.as_email:
                sentence += f'{self.site_link("personal")} and {self.modeling_link("Financial Modeling")} websites'
            else:
                sentence += 'personal and Financial Modeling websites'
        elif self.focus == ApplicationFocus.GOVERNMENT:
            if self.as_email:
                sentence += f'a {self.site_link("personal website")}'
            else:
                sentence += 'a personal website'
        else:
            raise ValueError(f'no handling for focus {self.focus}')
        if self.as_email:
            sentence += ' linked here'
        else:
            sentence += ' listed in the footnotes'
        sentence += ' and on my CV with additional information.'
        return sentence

    @property
    def recommenders_str(self) -> str:
        if self.recommenders_are_dissertation_chairs:
            name_str = join_with_commas_and_and([author.name for author in self.included_references])
            return f'my dissertation committee co-Chairs, Professors {name_str}'

        names = []
        for author in self.included_references:
            if author in [AUTHORS[ANDY], AUTHORS[NIMAL]]:
                names.append(f'{author.name} (co-Chair)')
            else:
                names.append(author.name)
        name_str = join_with_commas_and_and(names)
        return f'my dissertation committee, Professors {name_str}'

    @property
    def recommenders_are_dissertation_chairs(self) -> bool:
        return (
            len(self.included_references) == 2 and
            AUTHORS[ANDY] in self.included_references and
            AUTHORS[NIMAL] in self.included_references
        )

    def site_link(self, link_text: str = SITE_URL) -> pl.Hyperlink:
        return pl.Hyperlink(
            SITE_URL,
            pl.Bold(
                pl.TextColor(link_text, color=self.blue)
            ),
        )

    def modeling_link(self, link_text: Optional[str] = None):
        financial_modeling_url = get_fin_model_course().website_url
        if link_text is None:
            link_text = financial_modeling_url
        modeling_link = pl.Hyperlink(
            financial_modeling_url,
            pl.Bold(
                pl.TextColor(link_text, color=self.blue)
            ),
        )
        return modeling_link

    @property
    def site_footnote(self) -> pl.Footnote:
        site_footnote = pl.Footnote(['See more information on all of this at', self.site_link(), 'or on my CV.'])
        return site_footnote

    @property
    def modeling_footnote(self) -> pl.Footnote:
        modeling_footnote = pl.Footnote(
            ['See the Financial Modeling course content at the course website: ', self.modeling_link()])
        return modeling_footnote

    @property
    def blue(self) -> pl.RGB:
        return pl.RGB(50, 82, 209, color_name="darkblue")


@dataclass
class CoverLetterDesireSection:
    target: ApplicationTarget
    focus: ApplicationFocus
    extra_content: Optional[PyexlatexItems] = None

    @property
    def default_paragraph(self) -> str:
        return '\n' + self.professional_paragraph + ' ' + self.personal_sentence + '\n'

    @property
    def professional_paragraph(self) -> str:
        if self.target.organization.abbreviation is None:
            raise ValueError('must have organization abbrevation to create desire paragraph professional portion')

        abbrev_posessive = (
            f"{self.target.organization.abbreviation}'s"
            if not self.target.organization.abbreviation.casefold().endswith('s')
            else f"{self.target.organization.abbreviation}'"
        )

        if self.focus != ApplicationFocus.ACADEMIC:
            raise NotImplementedError('need to implement auto desire paragraph for other than academic')

        para = f"""
My multiple lines of research and strong work ethic will contribute to {abbrev_posessive} goal of preeminence in 
research. Further, I will contribute to the goals of innovation and transformative, accessible education. 
It may already be apparent that I am not the typical Finance Ph.D. applicant: I have a much
larger emphasis on creating open-source software. My commitment to open-source is a commitment to inclusion and 
diversity: I believe everyone should have access to these tools regardless of their economic position, 
and that anyone should be able to learn from them, regardless of their location in the world or cultural 
background. I have already built tools for both research and education, and I want to continue innovating
at a university that encourages such efforts.
""".strip()

        return para

    @property
    def personal_sentence(self) -> str:
        if not self.target.organization.characteristics:
            raise ValueError('must pass characteristics to organization to generate default desire personal sentence')
        if self.target.organization.city is None:
            raise ValueError('must pass city to organization to generate default desire personal sentence')

        personal_sentence = "On a personal level, my wife and I "
        if OrganizationCharacteristics.SMALL_TOWN in self.target.organization.characteristics:
            personal_sentence += 'enjoy outdoor activities'
        elif OrganizationCharacteristics.MID_SIZE_CITY in self.target.organization.characteristics:
            personal_sentence += 'have an affinity for mid-side cities'
        elif OrganizationCharacteristics.LARGE_CITY in self.target.organization.characteristics:
            personal_sentence += 'have an affinity for larger cities'

        if OrganizationCharacteristics.WARM_WEATHER in self.target.organization.characteristics:
            personal_sentence += ' and warm weather'

        personal_sentence += f' so {self.target.organization.city} seems like a good fit.'
        return personal_sentence

    def to_pyexlatex(self) -> PyexlatexItems:
        if self.extra_content is None:
            return [self.default_paragraph]

        if isinstance(self.extra_content, (list, tuple)):
            return [self.default_paragraph, *self.extra_content]
        else:
            return [self.default_paragraph, self.extra_content]
