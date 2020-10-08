import pyexlatex as pl
import pyexlatex.resume as lr

from derobertis_cv import plbuild
from derobertis_cv.plbuild.paths import images_path
from derobertis_cv.pldata.constants.contact import CONTACT_LINES
from derobertis_cv.pldata.cv import CVModel, get_cv_contents, ResumeSection, get_cv_packages, get_cv_pre_env_contents
from derobertis_cv.pldata.jobs import CV_JOB_MODIFIERS, CV_EXCLUDED_COMPANIES
from derobertis_cv.pldata.skills import CV_RENAME_SKILLS, CV_EXCLUDE_SKILLS, CV_SKILL_SECTION_ORDER
from derobertis_cv.pldata.software.config import EXCLUDED_SOFTWARE_PROJECTS, PROFESSIONAL_SOFTWARE_PROJECT_ORDER

AUTHORS = ['Nick DeRobertis']

DOCUMENT_CLASS = lr.Resume
OUTPUT_LOCATION = plbuild.paths.DOCUMENTS_BUILD_PATH
HANDOUTS_OUTPUT_LOCATION = None


SECTIONS = [
    ResumeSection.OVERVIEW,
    pl.VSpace(0.2),
    ResumeSection.EDUCATION,
    pl.VSpace(0.2),
    ResumeSection.PROFESSIONAL_EXPERIENCE,
    ResumeSection.ACADEMIC_EXPERIENCE,
    pl.PageBreak(),
    ResumeSection.SKILLS,
    pl.PageBreak(),
    ResumeSection.WORKING_PAPERS,
    pl.VSpace(0.2),
    ResumeSection.WORKS_IN_PROGRESS,
    pl.VSpace(0.2),
    ResumeSection.AWARDS_GRANTS,
    pl.VSpace(0.4),
    ResumeSection.SOFTWARE_PROJECTS,
]


def get_content():
    model = CVModel(
        SECTIONS,
        excluded_software_projects=EXCLUDED_SOFTWARE_PROJECTS,
        software_project_order=PROFESSIONAL_SOFTWARE_PROJECT_ORDER,
        include_private_jobs=True,
        rename_skills=CV_RENAME_SKILLS,
        exclude_skills=CV_EXCLUDE_SKILLS,
        skill_section_order=CV_SKILL_SECTION_ORDER,
        include_working_paper_descriptions=False,
        modify_job_descriptions=CV_JOB_MODIFIERS,
        excluded_companies=CV_EXCLUDED_COMPANIES,
    )
    contents = get_cv_contents(model)
    return contents

DOCUMENT_CLASS_KWARGS = dict(
    contact_lines=CONTACT_LINES,
    packages=get_cv_packages(),
    pre_env_contents=get_cv_pre_env_contents(),
)
OUTPUT_NAME = f'{AUTHORS[0]} Professional CV'
