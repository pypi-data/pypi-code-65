import datetime
import requests
import json
from delorean import Delorean, parse
from numpy.random import choice
from random import randint
from mimesis.enums import Gender, TLDType
from mimesis import Generic
from faker import Faker
import pandas as pd


# import your mimesis and faker providers
mimesis_generic = Generic('en')
fake = Faker()

# set some constants
AssociationId = '8128'
StateAssociationId = '0862'

# these values are for fun
simp_state = 'OR'
simp_area_codes = [636, 939]


# corrected designations information list
designations_list = [{
    'code': 'ABR', 'description': 'Accredited Buyers Representative'}, {
    'code': 'ALC', 'description': 'Accredited Land Consultant'}, {
    'code': 'CCIM', 'description': 'Certified Commercial Investment Member'}, {
    'code': 'CIPS', 'description': 'Certified International Property Specialist'}, {
    'code': 'CPM', 'description': 'Certified Property Manager'}, {
    'code': 'CRB', 'description': 'Certified Real Estate Brokerage Manager'}, {
    'code': 'CRS', 'description': 'Certified Residential Specialist'}, {
    'code': 'CRE', 'description': 'Counselor of Real Estate'}, {
    'code': 'GAA', 'description': 'General Accredited Appraiser'}, {
    'code': 'GREEN', 'description': 'NARs Green Designation'}, {
    'code': 'GRI', 'description': 'Graduate REALTOR Institute'}, {
    'code': 'PMN', 'description': 'Performance Management Network'}, {
    'code': 'RENE', 'description': 'Real Estate Negotiation Expert'}, {
    'code': 'RCE', 'description': 'REALTOR Association Certified Executive'}, {
    'code': 'RAA', 'description': 'Residential Accredited Appraiser'}, {
    'code': 'SRS', 'description': 'Seller Representative Specialist'}, {
    'code': 'SIOR', 'description': 'Society of Industrial and Office REALTORS'}, {
    'code': 'SRES', 'description': 'Seniors Real Estate Specialist'
    }]


## worker functions

# returns either the result of a function or an empty string, weighted 70/30
def sometimes(func):
    elements = ['', func]
    weights = [0.7, 0.3]
    return choice(elements, p=weights)


# returns either the result of a function or an empty string, weighted 20/80
def usually(func):
    elements = ['', func]
    weights = [0.2, 0.8]
    return choice(elements, p=weights)


# produces a random int of 'n' digits length
def random_n_digits(n):
    range_start = 10**(n-1)
    range_end = (10**n)-1
    return randint(range_start, range_end)


# bool y/n, usually N
def usually_no():
    elements = ['Y', 'N'] 
    weights = [0.05, 0.95]
    return choice(elements, p=weights)


# bool y/n, usually Y
def usually_yes():
    elements = ['Y', 'N'] 
    weights = [0.95, 0.05]
    return choice(elements, p=weights)


# generation randomizer
def gen_gen():
    elements = ['', 'Jr.', 'Sr.', 'II', 'III', 'IV', 'VIII'] 
    weights = [0.84, 0.04, 0.04, 0.04, 0.02, 0.018, 0.002]
    return choice(elements, p=weights)


# simpsons cities randomizer
def simp_city():
    elements = ['Springfield', 'Shelbyville', 'Capital City', 'Ogdenville', 'North Haverbrook'] 
    weights = [0.40, 0.25, 0.15, 0.10, 0.10]
    return choice(elements, p=weights)


# preferred phone randomizer
def phone_pref():
    elements = ['H', 'O', 'C']
    weights = [0.20, 0.40, 0.40]
    return choice(elements, p=weights)


# mail location pref randomizer
def mail_loc():
    elements = ['H', 'O', 'M', 'F']
    weights = [0.30, 0.30, 0.30, 0.10]
    return choice(elements, p=weights)


# address 2 / unit number randomizer
def unit_no():
    elements = ['Suite ', 'Unit ', '#', 'Apt ']
    weights = [0.25, 0.25, 0.25, 0.25]
    out = choice(elements, p=weights)
    return f'{out}{randint(10, 950)}'


# address directional/suffix generator
def address_dir():
    elements = ['East', 'South', 'North','NW', 'SW', ]
    weights = [0.20, 0.20, 0.20, 0.20, 0.20]
    return choice(elements, p=weights)


# get a random address dict
def generate_address_dict():
    address_dict = {
        #'City': mimesis_generic.address.city(),  # use for random city
        'City': simp_city(),
        'Country': 'US',
        #'State': mimesis_generic.address.state(abbr=True),  # use for random state
        'State': simp_state,
        'Street1': f'{mimesis_generic.address.street_number()} {mimesis_generic.address.street_name()} {mimesis_generic.address.street_suffix()}{usually(f""" {address_dir()}""")}',
        'Street2': f'{sometimes(unit_no())}',
        'Zip': mimesis_generic.address.zip_code(),
        'Zip6': f'{random_n_digits(4)}'
        }
    
    return address_dict


# generate phone number dicts with given area codes
def generate_phone_dict():
    area_codes = simp_area_codes
    phone_dict = {}
    #phone_dict['PhoneArea'] = int(random_n_digits(3))  # use for random area code
    phone_dict['PhoneArea'] = int(choice(area_codes))
    phone_dict['PhoneNumber'] = int(random_n_digits(7))
    return phone_dict


# generate random individual RE license numbers with FL style prefixes
def generate_re_licns():
    elements = ['SL', 'BK', 'BO']
    weights = [0.85, 0.13, 0.02]
    return f'{choice(elements, p=weights)}{random_n_digits(6)}'


# generate a random NAR member type (only R (90%) / RA (10%) with this config)
def generate_mem_type():
    elements = ['R', 'RA', 'AFF', 'I', 'N', 'S', 'MLO', 'L', 'CCO']
    weights = [0.90, 0.10, 0,0,0,0,0,0,0]
    return f'{choice(elements, p=weights)}'


## functions for biographical data generation

# get gender elements
def get_gender_dict():
    
    # set your choices and probabilties, make a choice
    # TODO - implement ISO standard
    elements = ['M', 'F'] 
    weights = [0.46, 0.54]
    chosen = choice(elements, p=weights)
    
    # create a blank dict
    gender_dict = {}
    
    # if male
    if chosen == 'M':
        gender_dict['title'] = 'male'
        gender_dict['abrv'] = 'M'
        gender_dict['enum'] = Gender.MALE
    
    # if female
    else:
        gender_dict['title'] = 'female'
        gender_dict['abrv'] = 'F'
        gender_dict['enum'] = Gender.FEMALE
    
    return gender_dict


# generate names using mimesis with Gender.ENUM as input
def get_name_dict(gender_enum):
    name_dict = {}
    name_dict['first'] = mimesis_generic.person.first_name(gender=gender_enum)
    name_dict['middle'] = sometimes(mimesis_generic.person.first_name(gender=gender_enum))
    name_dict['last'] = mimesis_generic.person.last_name()
    return name_dict


# generate a random age int between 19-95 with realistic-ish distribution for NAR members
def rand_age():
    elements = [randint(19, 25), randint(26, 34), randint(35, 45), randint(46, 55), randint(56, 72), randint(73, 80), randint(80, 95)] 
    weights = [0.01, 0.04, 0.05, 0.30, 0.55, 0.04, 0.01]
    return choice(elements, p=weights)


# generate a random number of years in RE/experience from given age ranges
def generate_yrs_xp(age):
    
    # if age is in range
    if age in range(19, 25):
        
        # generate a random int in this range and assign to 'yrs_xp'
        yrs_xp = randint(0,3)
    
    # continue with all age ranges
    elif age in range(26, 34):
        yrs_xp = randint(0,6)
    elif age in range(35, 45):
        yrs_xp = randint(0,11)
    elif age in range(46, 55):
        yrs_xp = randint(0, 18)
    elif age in range(56, 72):
        yrs_xp = randint(8, 36)
    elif age in range(73, 80):
        yrs_xp = randint(18, 45)
    else:
        yrs_xp = randint(30, 65)
    
    return yrs_xp


## functions for date generation

# get the current year as an int from Delorean
## TODO - refactor current year stuff - numpy int64 typing is causing issues in mimesis funcs
def get_current_year():
    return int((Delorean().truncate('year').datetime.strftime('%Y')))


# get a dob based on current year - age from mimesis.generic
def get_dob(aprox_age):
    current_year = int((Delorean().truncate('year').datetime.strftime('%Y')))
    return mimesis_generic.datetime.date(start=(current_year-aprox_age), end=(current_year-aprox_age)+1).strftime('%m-%d-%Y')


# get a join date based on yrs_xp from mimesis.generic
def get_join_date(yrs_xp):
    current_year = int((Delorean().truncate('year').datetime.strftime('%Y')))
    return mimesis_generic.datetime.date(start=(current_year-yrs_xp), end=(current_year-yrs_xp)+1).strftime('%m-%d-%Y')


# get an orientation date based on join date
def get_orientation_date(join_date):
    joined = parse(join_date).datetime
    o_range = joined + datetime.timedelta(weeks=9)
    return fake.date_between(joined, o_range).strftime('%m-%d-%Y')


# get a dues paid date from faker
def get_dues_paid_date():
    last_year = int(Delorean().truncate('year').datetime.strftime('%Y'))-1
    start_date = datetime.date(year=(last_year), month=8, day=25)
    end_date = datetime.date(year=(last_year), month=12, day=30)
    return fake.date_between(start_date=start_date, end_date=end_date).strftime('%m-%d-%Y')

# generate a random "Designations" section
def generate_designations(member_id, join_date):
    
    # get datetime for join date
    joined = parse(join_date).datetime
    
    # create a blank list
    designations = []
    
    # get a random number of designations
    for i in range(1, randint(2,5)):
        
        # for each, choose from designations_list
        dl = choice(designations_list)
        
        # add the designation and member info to a new dict and append it
        ## TODO - allows duplicates, improve
        designations.append({
                "DesignationCode": dl['code'],
                "DesignationDate": fake.date_between(joined).strftime('%m-%d-%Y'),
                "DesignationDescription": dl['description'],
                "MemberId": str(member_id),
                "Timestamp": int(random_n_digits(7))
                })
    
    # remove duplicates in pandas and return as a list of dicts
    df = pd.DataFrame(designations)
    df = df.drop_duplicates(subset = ["DesignationCode"])
    
    return df.to_dict('records')


# combine above methods into a single method
def get_person():
    gender_dict = get_gender_dict()
    name_dict = get_name_dict(gender_dict['enum'])
    person_dict = {**gender_dict, **name_dict}
    person_dict['aprox_age'] = rand_age()
    person_dict['yrs_xp'] = generate_yrs_xp(person_dict['aprox_age'])
    person_dict['MemberBirthDate'] = get_dob(person_dict['aprox_age'])
    person_dict['JoinedDate'] = get_join_date(person_dict['yrs_xp'])
    person_dict['MemberLocalJoinedDate'] = person_dict['JoinedDate']
    person_dict['MemberNRDSInsertDate'] = person_dict['JoinedDate']
    person_dict['MemberOrientationDate'] = get_orientation_date(person_dict['JoinedDate'])
    person_dict['MemberNationalDuesPaidDate'] = get_dues_paid_date()   
    person_dict['MemberStateDuesPaidDate'] = person_dict['MemberNationalDuesPaidDate']
    person_dict['MemberOnlineStatusDate'] = ''
    person_dict['MemberReinstatementDate'] = ''
    person_dict['MemberStatusDate'] = ''
    person_dict['MemberId'] = f'{AssociationId}{random_n_digits(5)}'
    person_dict['Designations'] = list(sometimes(generate_designations(person_dict['MemberId'], person_dict['JoinedDate'])))
    
    return person_dict


def get_random_member():

    # get bio details
    person_dict = get_person()

    # populate a dict with bio details and remaining info
    member_return = {
        'Member': {
            'AssociationId': AssociationId,
            'Designations': person_dict['Designations'],
            'DirectoryOptOut': usually_no(),
            'DuesWaivedLocalFlag': usually_no(),
            'DuesWaivedNationalFlag': usually_no(),
            'DuesWaivedStateFlag': usually_no(),
            'Email': mimesis_generic.person.email(),
            'JoinedDate': person_dict['JoinedDate'],
            'JunkMailFlag': usually_yes(),
            'MLSID': f'{random_n_digits(4)}',                                      # TODO - exact significance unknown
            'MemberArbitrationEthicsPending': usually_no(),
            'MemberBirthDate': person_dict['MemberBirthDate'],
            'MemberCellPhone': generate_phone_dict(),
            'MemberDesignatedRealtor': usually_no(),
            'MemberFirstName': person_dict['first'],
            'MemberGender':  person_dict['abrv'],
            'MemberGeneration':  gen_gen(),
            'MemberHomeAddress': generate_address_dict(),
            'MemberHomePhone': generate_phone_dict(),
            'MemberId': person_dict['MemberId'],
            'MemberLastName': person_dict['last'],
            'MemberLocalJoinedDate': person_dict['MemberLocalJoinedDate'],
            'MemberMLSAssociationId': f'{random_n_digits(5)}',                     # TODO - exact significance unknown
            'MemberMailAddress': generate_address_dict(),
            'MemberMiddleName': person_dict['middle'],
            'MemberNRDSInsertDate': person_dict['MemberNRDSInsertDate'],
            'MemberNationalDuesPaidDate': person_dict['MemberNationalDuesPaidDate'],
            'MemberNickname': sometimes(mimesis_generic.text.word()),
            'MemberOccupationName': mimesis_generic.person.occupation(),           # TODO - random placeholder - all valid values??
            'MemberOfficeVoiceExtension': f'{random_n_digits(4)}',
            'MemberOnlineStatus': usually_yes(),
            'MemberOnlineStatusDate': person_dict['MemberOnlineStatusDate'],
            'MemberOrientationDate': person_dict['MemberOrientationDate'],
            'MemberPager': generate_phone_dict(),
            'MemberPersonalFax': generate_phone_dict(),
            'MemberPreferredFax': phone_pref(),
            'MemberPreferredMail': mail_loc(),
            'MemberPreferredPhone': phone_pref(),
            'MemberPreferredPublication': mail_loc(),
            'MemberPrimaryStateAssociationId': StateAssociationId,
            'MemberRELicense': generate_re_licns(),
            'MemberReinstatementCode': '',                                         # TODO - all valid values??
            'MemberReinstatementDate': person_dict['MemberReinstatementDate'],
            'MemberSalutation': '',                                                # TODO
            'MemberStateDuesPaidDate': person_dict['MemberStateDuesPaidDate'],
            'MemberStatus': 'A',                                                   # TODO - all valid values??
            'MemberStatusDate': person_dict['MemberStatusDate'],
            'MemberSubclass': 'R',                                                 # TODO - all valid values??
            'MemberTitle': '',                                                     # TODO
            'MemberType': f'{generate_mem_type()}',
            'OfficeId': f'{AssociationId}',
            'OnRosterFlag': usually_yes(),
            'PointOfEntry': f'07000{AssociationId}',
            'PreviousNonMemberFlag': usually_no(),
            'PrimaryIndicator': 'P',                                               # TODO - all valid values??
            'StopEMailFlag': usually_no(),
            'StopFaxFlag': usually_no(),
            'StopMailFlag': usually_no(),
            'Timestamp': int(random_n_digits(7)),
            'WebPage': mimesis_generic.internet.home_page(tld_type=TLDType.UTLD)
        }
    }

    # convert the dict to json and return it
    return json.dumps(member_return)


## helper methods for NAR data

# takes a NRDS-id-like value of type int or str
# and and returns a valid NRDS id string or error
def parse_nrds_id(value):
    
    # evaluate if value is string
    if isinstance(value, str):
        
        # if so, 0-pad value to 9 characters (can produce strs of len 9+)
        nrds_id = str.zfill(value,9)
        
        # verify the resulting str is exactly 9 chars and contains no non-numeric chars
        if len(nrds_id) == 9 and nrds_id.isdigit():
            
            return nrds_id

        # if != 9 chars or contains non-numeric chars, error
        else:
            
            return f'error: invalid nrds id! input value: {value}'

    # else evaluate if value is integer
    elif isinstance(value, int):
        
        # convert it to a str and 0-pad value to 9 characters (can produce strs of len 9+)
        nrds_id = str.zfill(str(value),9)
        
        # if != 9 chars, error
        if len(nrds_id) != 9:
            
            return f'error: invalid nrds id! input value: {value}'
        
        else:
            return nrds_id
    
    # else value is not str or int, error
    else:
        return f'error: invalid nrds id! iput type - {value}, {type(value)}'


## NRDS API functions

# NRDS Beta API url
beta_base_url = 'https://beta.api.realtor.org/data'


# get data for a single member, given
# target member ID, user role, and sender member ID
def get_single_member(member_id, user_role, sender_member_id):

    payload = {
        'UserRole'      : user_role,
        'SenderMemberId': sender_member_id
        }

    url = f'{beta_base_url}/members/{member_id}'

    reply = requests.post(url, payload)
    return(reply)
