import os
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional, List

from PyPDF2 import PdfFileMerger

from derobertis_cv.plbuild.paths import DOCUMENTS_BUILD_PATH, documents_build_path, pdfs_path, APPLICATIONS_OUT_PATH
from derobertis_cv.pldata.constants.contact import NAME
from derobertis_cv.pldata.cover_letters.letter_config import get_cover_letters
from derobertis_cv.pldata.cover_letters.models import ApplicationComponents, ApplicationFocus, CoverLetter


@dataclass
class FileLocations:
    letter: CoverLetter

    def location(self, component: ApplicationComponents) -> Path:
        cover_letter_name = f'{self.letter.target.organization.abbreviation} Cover Letter.pdf'

        file_locations: Dict[ApplicationComponents, str] = {
            ApplicationComponents.JOB_MARKET_PAPER: pdfs_path('Job Market Paper - Valuation without Cash Flows.pdf'),
            ApplicationComponents.GOVERNMENT_INTERVENTION_PAPER: pdfs_path('Government Equity Market '
                                                                           'Intervention and the Cross_Section '
                                                                           'of Stock Returns.pdf'),
            ApplicationComponents.INVESTOR_ATTENTION_PAPER: pdfs_path('Are Investors Paying (for) Attention?.pdf'),
            ApplicationComponents.RESEARCH_STATEMENT: documents_build_path('Research Statement.pdf'),
            ApplicationComponents.TEACHING_STATEMENT: documents_build_path('Teaching Statement.pdf'),
            ApplicationComponents.COURSE_OUTLINES: pdfs_path('Course Outline.pdf'),
            ApplicationComponents.TRANSCRIPTS: pdfs_path('All Transcripts.pdf'),
            ApplicationComponents.EVALUATIONS: pdfs_path('All Evaluations.pdf'),
            ApplicationComponents.DIVERSITY: documents_build_path('Diversity Statement.pdf'),
            ApplicationComponents.COVER_LETTER: documents_build_path(cover_letter_name),
            ApplicationComponents.REFERENCES: documents_build_path(f'{NAME} References.pdf')
        }

        if self.letter.focus == ApplicationFocus.ACADEMIC:
            file_locations[ApplicationComponents.CV] = documents_build_path(f'{NAME} CV.pdf')
        elif self.letter.focus == ApplicationFocus.GOVERNMENT:
            file_locations[ApplicationComponents.CV] = documents_build_path(f'{NAME} Hybrid CV.pdf')
        else:
            raise NotImplementedError(f'need to get correct CV for focus {self.letter.focus}')

        try:
            location = file_locations[component]
        except KeyError:
            raise NotImplementedError(f'cannot find location of application component {component}')

        return Path(location)


def build_applications(letter_out_folder: str = DOCUMENTS_BUILD_PATH,
                       application_out_folder: str = APPLICATIONS_OUT_PATH):
    cover_letters = get_cover_letters()
    for letter in cover_letters:
        _build_application(letter, letter_out_folder=letter_out_folder, application_out_folder=application_out_folder)


def build_application(target_abbreviation: str, letter_out_folder: str = DOCUMENTS_BUILD_PATH,
                       application_out_folder: str = APPLICATIONS_OUT_PATH):
    cover_letters = get_cover_letters()
    for letter in cover_letters:
        if letter.target.organization.abbreviation is None:
            raise ValueError(f'must have organization abbreviation to build for {letter}')

        if letter.target.organization.abbreviation.casefold() == target_abbreviation.casefold():
            _build_application(
                letter, letter_out_folder=letter_out_folder, application_out_folder=application_out_folder
            )
            return

    possible_abbreviations = [letter.target.organization.abbreviation for letter in cover_letters]
    raise ValueError(f'could not find cover letter matching abbreviation {target_abbreviation}. '
                     f'Should be one of {possible_abbreviations}')


def _build_application(letter: CoverLetter, letter_out_folder: str = DOCUMENTS_BUILD_PATH,
                       application_out_folder: str = APPLICATIONS_OUT_PATH):
    abbrev = letter.target.organization.abbreviation
    if abbrev is None:
        raise ValueError(f'must have organization abbreviation to build for {letter}')

    print(f'Building letter for {abbrev}')
    letter.to_pyexlatex(out_folder=letter_out_folder)

    print(f'Building application for {abbrev}')
    file_locs = FileLocations(letter)
    this_out_folder = Path(application_out_folder) / abbrev
    if os.path.exists(this_out_folder):
        shutil.rmtree(this_out_folder)
    os.makedirs(this_out_folder)
    combined_out_path = this_out_folder / f'Nick DeRobertis {abbrev} Application.pdf'
    merger = PdfFileMerger()

    components: List[ApplicationComponents] = []
    if not letter.as_email:
        components.append(ApplicationComponents.COVER_LETTER)
    components.extend(letter.included_components)

    for component in components:
        if letter.file_renames and component in letter.file_renames:
            out_path = this_out_folder / (letter.file_renames[component] + '.pdf')
        else:
            out_path = this_out_folder
        source = file_locs.location(component)
        shutil.copy(source, out_path)
        merger.append(str(source))
    merger.write(str(combined_out_path))


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('--name', required=False, help="Abbreviation of cover letter to build")
    args = parser.parse_args()

    if args.name:
        build_application(args.name)
    else:
        build_applications()
