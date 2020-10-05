from derobertis_cv.plbuild.paths import DOCUMENTS_BUILD_PATH
from derobertis_cv.pldata.cover_letters.letter_config import get_cover_letters


def build_cover_letters(out_folder: str = DOCUMENTS_BUILD_PATH):
    cover_letters = get_cover_letters()
    for letter in cover_letters:
        print(f'Building letter for {letter.target.organization.abbreviation}')
        letter.to_pyexlatex(out_folder=out_folder)


if __name__ == '__main__':
    build_cover_letters()
