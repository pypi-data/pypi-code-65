def get_business_type_regularise(business_type):
    try:
        if business_type.upper() in ('INDIVIDUAL', 'PROPRIETARY'):
            business_type = 'PROPRIETARY'
        else:
            business_type = business_type.upper()
    except:
        business_type = None
    return business_type

def get_state_name_regularise(state):
    try:
        if state.upper() in ('KARNATAKA','KARNATAKA ','BANGALORE'):
            state = 'KARNATAKA'
        elif state.upper() in ('MAHARSHTRA','MAHARASHTRA','MAHARASTRA'):
            state = 'MAHARASHTRA'
        elif state.upper() in ('TELANGANA','TELANAGANA'):
            state = 'TELANGANA'
        elif state.upper() in ('UTTAR PRADESH','UTTARPRADESH','NOIDA UTTAR PRADESH'):
            state = 'UTTAR PRADESH'
        elif state.upper() in ('DELHI','NEW DELHI'):
            state = 'DELHI'
        elif state.upper() in ('ORISSA','ODISHA'):
            state = 'ODISHA'
        elif state.upper() in ('PONDICHERRY','PUDUCHERRY'):
            state = 'PUDUCHERRY'
        elif state.upper() in ('GURGAON','HARYANA'):
            state = 'HARYANA'
        else:
            state = state.upper()
    except:
        state = None
    return state

def get_city_name_regularise(city):
    try:
        if city.upper() in ('BENGALURU','BANGALORE / BENGALURU','BANGALORE'):
            city = 'BANGALORE'
        elif  city.upper() in ('VISAKHAPATNAM','VIZAG / VISAKHAPATNAM','VIZAG'):
            city = 'VISAKHAPATNAM'
        elif  city.upper() in ('MYSORE','MYSORE / MYSURU','MYSURU'):
            city = 'MYSURU'
        elif  city.upper() in ('GURGAON','GURGAON / GURUGRAM','GURUGRAM'):
            city = 'GURUGRAM'
        elif  city.upper() in ('LUCKNOW','LUCKHNOW'):
            city = 'LUCKNOW'
        elif  city.upper() in ('PUNE','PUE'):
            city = 'PUNE'
        elif  city.upper() in ('GAUTAM BUDDHA NAGAR','NOIDA'):
            city = 'NOIDA'
        elif  city.upper() in ('MUMBAI','NOTINTERESTED','CPVREJECTEDDOCUMENTISSUE','NEGATIVEMUMBRA'):
            city = 'MUMBAI'
        elif  city.upper() in ('VIJAYAWADA','VIJAYWADA'):
            city = 'VIJAYAWADA'
        elif  city.upper() in ('PUNERULER','PUNE RULER','PUNE RURAL'):
            city = 'PUNE RURAL'
        else:
            city = city.upper()
    except:
        city = None
    return city

def get_tenure_regularise(tenure):
    try:
        if tenure in ('1 Months','1 Month','1 month'):
            return '1 month'
        else:
            return tenure
    except:
        return None
    
def define_interest_only_full_EDI(tenure):
    try:
        if '+' in tenure:
            return 'Interest_Only_Component'
        else:
            return 'Full_EDI_Only'
    except:
        return None

def disbursement_date_binning(disb_date):
    dbin = None
    if disb_date is not None:
        disb_day = disb_date.day
        if 1<= disb_day <=7:
            dbin = '01-07'
        elif 8<= disb_day <=14:
            dbin = '08-14'
        elif 15<= disb_day <=21:
            dbin = '15-21'
        elif 22<= disb_day:
            dbin = '21+'
    
    return dbin

category_Old = [None, 'BRONZE', 'SILVER', 'GOLD', 'PLATINUM', 'DIAMOND', 'AA1',
                'CC6', 'BB3', 'CC12', 'BB6', 'CC3', 'AA3', 'I4', 'I7', 'I13']
category_S1 = ['S1LG3','S1DG3', 'S1A3', 'S1LG6', 'S1DG9', 'S1DG6', 'S1A1', 'S1LG1', 'S1DG1',
               'S1A6', 'S1DG12', 'S1LG9']
category_S2 = ['S2A6', 'S2A3','S2DG6', 'S2A9' 'S2DG3', 'S2DG15', 'S2DG1', 'S2LG3','S2DG9', 'S2LG9',
               'S2LG12', 'S2DG12', 'S2DG1+6','S2A1+6','S2LG1+6', 'S2A1+3' ,'S2DG1+3', 'S2LG1+3'
               'S2DG1+12','S2LG1+12', 'S2A1+12']
category_S3 = ['S3LG3','S3A3', 'S3LG1', 'S3A1','S3DG6', 'S3DG3', 'S3LG6', 'S3DG9', 'S3DG1']

category_S4 = ['S4DG3', 'S4LG12','S4LG9', 'S4DG12', 'S4A9', 'S4LG3', 'S4LG6', 'S4A6','S4LG1',
                'S4LG1+6','S4LG1+3','S4LG1+12','S4A1+3', 'S4DG1+3', 'S4DG1+6','S4DG1+12']
category_Zomato = ['Z1','Z2','Z3','Z4','Z5','Z6','Z7','Z8','Z9']

def get_category_strucure(category):
    '''
    Takes risk category and tenure mixed string and return structure by which this application was processed.
    '''
    cat_sturct = None
    if category in category_Old:
        cat_sturct = 'category_Old'
    elif category in category_S1:
        cat_sturct = 'category_S1'
    elif category in category_S2:
        cat_sturct = 'category_S2'
    elif category in category_S3:
        cat_sturct = 'category_S3'
    elif category in category_S4:
        cat_sturct = 'category_S4'
    elif category in category_Zomato:
        cat_sturct = 'category_Zomato' 
    return cat_sturct

def define_essential_services(business_category):
    '''
    Takes business category of merchants and categories it as essential and non-essentials
    '''
    if business_category in ['Food_and_Drink', 'Medical','Fresh_Produce', 'Grocery','Dairy', 'Fuel']:
        return 'Essential_Services'
    else:
        return 'Non_Essential_Services'
    
def get_loan_product_type_regularise(loan_type):
    '''
    This function take loan_type as input and return organised form of loan type
    '''
    try:
        if loan_type=='' or loan_type in ('FIRST','REGULAR',None):
            return 'REGULAR'
        elif loan_type in ('SUBSEQUENT','TOPUP'):
            return 'TOPUP'
        else:
            return loan_type
    except:
        return loan_type
