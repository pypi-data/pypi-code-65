from derobertis_cv.models.university import UniversityModel
from derobertis_cv.pldata.constants.institutions import UF_NAME, VCU_NAME
from derobertis_cv.pldata.cover_letters.models import HiringManager, ApplicationTarget
from derobertis_cv.pltemplates.logo import image_base64

UF = UniversityModel(UF_NAME, 'Gainesville, FL', abbreviation='UF', logo_base64=image_base64('uf-logo.png'))
VCU = UniversityModel(VCU_NAME, 'Richmond, VA', abbreviation='VCU', logo_base64=image_base64('vcu-logo.png'))

PLACEHOLDER_UNIVERSITY = UniversityModel(
    '(School name)',
    '(City, state)',
    abbreviation='(School abbreviation)',
    address_lines=[
        '(Department name)',
        '(Street address)',
        '(City, state, ZIP)',
    ]
)

PLACEHOLDER_UNIVERSITY_TARGET = ApplicationTarget(
    PLACEHOLDER_UNIVERSITY,
    'Assistant Professor',
)

EL_PASO = UniversityModel(
    'University of Texas at El Paso',
    'El Paso, TX',
    abbreviation='UTEP',
    address_lines=[
        'Economics and Finance',
        'Business Room 236',
        '500 West University Avenue',
        'El Paso, TX  79968'
    ]
)

EL_PASO_TARGET = ApplicationTarget(
    EL_PASO,
    'Assistant Professor',
)

DRAKE = UniversityModel(
    'Drake University College of Business & Public Administration',
    'Des Moines, IA',
    abbreviation='DU',
    address_lines=[
        'Finance Department',
        'Aliber Hall',
        '2507 University Ave',
        'Des Moines, IA 50311',
    ]
)

DRAKE_TARGET = ApplicationTarget(
    DRAKE,
    'Assistant Professor'
)