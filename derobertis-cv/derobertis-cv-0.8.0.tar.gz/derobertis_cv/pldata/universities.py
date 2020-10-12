from derobertis_cv.models.organization import OrganizationCharacteristics
from derobertis_cv.models.university import UniversityModel
from derobertis_cv.pldata.constants.institutions import UF_NAME, VCU_NAME
from derobertis_cv.pldata.cover_letters.models import HiringManager, ApplicationTarget
from derobertis_cv.pltemplates.logo import image_base64

AP = 'Assistant Professor'

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
    AP,
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
    AP,
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
    AP,
)

MONASH = UniversityModel(
    'Monash University',
    'Melbourne, Victoria, Australia',
    abbreviation='MU',
    address_lines=[
        'Monash Business School',
        '900 Dandenong Road',
        'Caulfield East',
        'Victoria 3145',
        'Australia'
    ]
)

MONASH_HIRING_MANAGER = HiringManager(
    'Banking and Finance Recruitment Team',
    is_person=False
)

MONASH_TARGET = ApplicationTarget(
    MONASH,
    AP,
    person=MONASH_HIRING_MANAGER,
)

OREGON_STATE = UniversityModel(
    'Oregon State University',
    'Corvallis, OR',
    abbreviation='OSU',
    address_lines=[
        'College of Business',
        '2751 SW Jefferson Way',
        'Corvallis, OR  97331'
    ]
)

OREGON_STATE_TARGET = ApplicationTarget(
    OREGON_STATE,
    AP,
)

FIU = UniversityModel(
    'Florida International University',
    'Miami, FL',
    abbreviation='FIU',
    address_lines=[
        'College of Business',
        '11200 SW 8th St.',
        'Miami, FL  33174'
    ],
    city='Miami',
    characteristics=[
        OrganizationCharacteristics.WARM_WEATHER,
        OrganizationCharacteristics.LARGE_CITY,
    ]
)

FIU_TARGET = ApplicationTarget(FIU, AP)

UWM = UniversityModel(
    'University of Wisconsin Milwaukee',
    'Milwaukee, WI',
    abbreviation='UWM',
    address_lines=[
        'Sheldon B. Lubar School of Business',
        '3202 N Maryland Ave',
        'Milwaukee, WI  53202'
    ],
    city='Milwaukee',
    characteristics=[
        OrganizationCharacteristics.MID_SIZE_CITY,
    ]
)

UWM_TARGET = ApplicationTarget(UWM, AP)