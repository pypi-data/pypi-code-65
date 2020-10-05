from derobertis_cv.models.organization import Organization
from derobertis_cv.pldata.cover_letters.models import ApplicationTarget, HiringManager, Gender

SEC_DERA = Organization(
    'U.S. Securities and Exchange Commission',
    'Washington, DC',
    abbreviation='DERA',
    address_lines=[
        'Division of Economic and Risk Analysis',
        '100 F Street, NE',
        'Washington, DC 20549',
    ]
)

WYNETTA_JONES = HiringManager(
    'Jones',
    first_name='Wynetta',
    gender=Gender.FEMALE,
    title='Lead HR Specialist',
)

DERA_COMMITTEE = HiringManager(
    'DERA Hiring Committee',
    is_person=False
)

SEC_DERA_TARGET = ApplicationTarget(
    SEC_DERA,
    'Financial Economic Fellow',
    person=DERA_COMMITTEE
)

OFR = Organization(
    'Office of Financial Research',
    'Washington, DC',
    abbreviation='OFR',
    address_lines=[
        'cover letter being sent as email',
    ]
)

OFR_TARGET = ApplicationTarget(
    OFR,
    'Research Economist',
)

RICH_FED = Organization(
    'Federal Reserve Bank of Richmond',
    'Charlotte, NC',
    abbreviation='QSR',
    address_lines=[
        'Quantitative Supervision & Research',
        '530 East Trade Street',
        'Charlotte, NC  28202',
    ]
)

RICH_FED_TARGET = ApplicationTarget(
    RICH_FED,
    'Financial Economist',
)