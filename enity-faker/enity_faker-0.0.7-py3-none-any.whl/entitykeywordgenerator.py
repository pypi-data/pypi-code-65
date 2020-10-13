from .keywords import KeywordsType
from .formatprovider import FormatProvider
from .formatgenerator import FormatGenerator
from faker import Faker
from faker.providers import BaseProvider
import json
import random

fake = Faker()
fake.add_provider(FormatProvider)

def generate_fake_by_id(entityid):
    entity_config = get_entities_json()
    entities = [e for e in entity_config if entityid == e["id"]]
    if(len(entities)>0):
        entity = entities[0]
        generic_keywords = ["Id", "# Id", "Serial Number", "No.", "Personal Id", "Personal #", "PIN", "Unique Id", "Personnel Number", "Personnel #", "Personal Info.", "Individual Id", "Credential No.", "Credential Number", "Affiliation", "Card Number", "Card Id", "Id Card"]
        if(len(entity["formats"])>0):
            formats = entity["formats"]
        else:
            formats = FormatGenerator.generatebyid(entity["id"])
        return fake.generate_fake(formats= formats)
    else:
        "entity not found!!"

def generate_entites(entityid, keywordtype, numberofinstances, changed_entities = []):
    entity_config = get_entities_json()
    entities = [e for e in entity_config if entityid == e["id"]]
    if(len(entities)>0):
        entity = entities[0]
        entity_changed = [e for e in changed_entities if entityid == e["id"]]
        if(len(entity_changed) > 0):
            if("specifickeywords" in entity_changed[0]):
                entity["specifickeywords"] = entity_changed[0]["specifickeywords"]
            if("generickeywords" in entity_changed[0]):
                generic_keywords = entity_changed[0]["generickeywords"]
        generic_keywords = ["Id", "# Id", "Serial Number", "No.", "Personal Id", "Personal #", "PIN", "Unique Id", "Personnel Number", "Personnel #", "Personal Info.", "Individual Id", "Credential No.", "Credential Number", "Affiliation", "Card Number", "Card Id", "Id Card"]
        if(len(entity["formats"])>0):
            formats = entity["formats"]
        else:
            formats = FormatGenerator.generatebyid(entity["id"])
        fakeinstances = []
        if(keywordtype == KeywordsType.Specific):
            keywords = entity["specifickeywords"]
        elif (keywordtype == KeywordsType.Generic):
            keywords = generic_keywords
        elif (keywordtype == KeywordsType.Conflict):
            keywords = entity["specifickeywords"]
        elif (keywordtype == KeywordsType.Empty):
            keywords = []

        for n in range(numberofinstances):
            if(keywordtype == KeywordsType.Empty):
                keyword = ""
            else:
                keyword = random.choice(keywords)
            fakeinstance = [fake.generate_fake(formats= formats), keyword]
            fakeinstances.append(fakeinstance)
        print(fakeinstances)
        return fakeinstances
    else:
        return "entity not found!!"

def get_entities_json():
    entities =  """[
                    {
                        "id": "abaroutingnumber",
                        "generickeywords": [],
                        "specifickeywords": ["aba", "aba #", "aba routing #", "aba routing number", "aba#", "abarouting#", "aba number", "abaroutingnumber", "american bank association routing #", "american bank association routing number", "americanbankassociationrouting#", "americanbankassociationroutingnumber", "bank routing number", "bankrouting#", "bankroutingnumber", "routing transit number", "RTN"],
                        "formats": [],
                        "similarentitiescount": 0,
                        "functionstosatisfy": []
                    },
                    {
                        "id": "argentinanationalidnumber",
                        "generickeywords": [],
                        "specifickeywords": ["Argentina National Identity number", "Identity", "Identification National Identity Card", "DNI", "NIC National Registry of Persons", "Documento Nacional de Identidad", "Registro Nacional de las Personas", "Identidad", "Identificación"],
                        "formats": ["##.###.###"],
                        "similarentitiescount": 0,
                        "functionstosatisfy": []
                    },
                    {
                        "id": "australiabankaccnumber",
                        "generickeywords": [],
                        "specifickeywords": ["swift bank code", "correspondent bank", "base currency", "usa account", "holder address", "bank address", "information account", "fund transfers", "bank charges", "bank details", "banking information", "full names", "iaea"],
                        "formats": ["###-###"],
                        "similarentitiescount": 0,
                        "functionstosatisfy": []
                    },
                    {
                        "id": "australiadriverlicencenumber",
                        "generickeywords": [],
                        "specifickeywords": ["international driving permits", "australian automobile association", "international driving permit", "DriverLicence", "DriverLicences", "Driver Lic", "Driver Licence", "Driver Licences", "DriversLic", "DriversLicence", "DriversLicences", "Drivers Lic", "Drivers Lics", "Drivers Licence", "Drivers Licences", "Driver'Lic", "Driver'Lics", "Driver'Licence", "Driver'Licences", "Driver' Lic", "Driver' Lics", "Driver' Licence", "Driver' Licences", "Driver'sLic", "Driver'sLics", "Driver'sLicence", "Driver'sLicences", "Driver's Lic", "Driver's Lics", "Driver's Licence", "Driver's Licences", "DriverLic#", "DriverLics#", "DriverLicence#", "DriverLicences#", "Driver Lic#", "Driver Lics#", "Driver Licence#", "Driver Licences#", "DriversLic#", "DriversLics#", "DriversLicence#", "DriversLicences#", "Drivers Lic#", "Drivers Lics#", "Drivers Licence#", "Drivers Licences#", "Driver'Lic#", "Driver'Lics#", "Driver'Licence#", "Driver'Licences#", "Driver' Lic#", "Driver' Lics#", "Driver' Licence#", "Driver' Licences#", "Driver'sLic#", "Driver'sLics#", "Driver'sLicence#", "Driver'sLicences#", "Driver's Lic#", "Driver's Lics#", "Driver's Licence#", "Driver's Licences#","aaa", "DriverLicense", "DriverLicenses", "Driver License", "Driver Licenses", "DriversLicense", "DriversLicenses", "Drivers License", "Drivers Licenses", "Driver'License", "Driver'Licenses", "Driver' License", "Driver' Licenses", "Driver'sLicense", "Driver'sLicenses", "Driver's License", "Driver's Licenses", "DriverLicense#", "DriverLicenses#", "Driver License#", "Driver Licenses#", "DriversLicense#", "DriversLicenses#", "Drivers License#", "Drivers Licenses#", "Driver'License#", "Driver'Licenses#", "Driver' License#", "Driver' Licenses#", "Driver'sLicense#", "Driver'sLicenses#", "Driver's License#", "Driver's Licenses#"],
                        "formats": ["#########","??##?????","#########","?????????"],
                        "similarentitiescount": 0,
                        "functionstosatisfy": []
                    },
                    {
                        "id": "australiamedicalaccnumber",
                        "generickeywords": [],
                        "specifickeywords": ["bank account details", "medicare payments", "mortgage account", "bank payments", "information branch", "credit card loan", "department of human services", "local service", "medicare"],
                        "formats": [],
                        "similarentitiescount": 0,
                        "functionstosatisfy": []
                    },
                    {
                        "id": "australiapassportnumber",
                        "generickeywords": [],
                        "specifickeywords": ["Passport Number", "Passport No", "Passport #", "Passport#", "PassportID", "Passportno", "passportnumber", "パスポート", "パスポート番号", "パスポ ートのNum", "パスポート ＃", "Numéro de passeport", "Passeport n °", "Passeport Non", "Passeport #", "Passeport#", "PasseportNon", "Passeportn °", "passport", "passport details", "immigration and citizenship", "commonwealth of australia", "department of immigration", "residential address", "department of immigration and citizenship", "visa", "national identity card", "passport number", "travel document", "issuing authority"],
                        "formats": ["?#######"],
                        "similarentitiescount": 0,
                        "functionstosatisfy": []
                    },
                    {
                        "id": "australiataxfilenumber",
                        "generickeywords": [],
                        "specifickeywords": ["australian business number", "marginal tax rate", "medicare levy", "portfolio number", "service veterans", "withholding tax", "individual tax return", "tax file number", "tfn", "00000000", "11111111", "22222222", "33333333", "44444444", "55555555", "66666666", "77777777", "88888888", "99999999", "000000000", "111111111", "222222222", "333333333", "444444444", "555555555", "666666666", "777777777", "888888888", "999999999", "0000000000", "1111111111", "2222222222", "3333333333", "4444444444", "5555555555", "6666666666", "7777777777", "8888888888", "9999999999"],
                        "formats": ["### ### #^","#######^","### ### ##^","########^"],
                        "similarentitiescount": 0,
                        "functionstosatisfy": []
                    },
                    {
                        "id": "austriadriverlicencenumber",
                        "generickeywords": [],
                        "specifickeywords": ["dl#", "driver license", "driver license number", "driver licence", "drivers lic.", "drivers license", "driver's licence", "driver's license", "driver's license number", "driver's licence number", "driving license number", "dlno#", "fuhrerschein", "fuhrerschein republik osterreich"],
                        "formats": ["########"],
                        "similarentitiescount": 0,
                        "functionstosatisfy": []
                    },
                    {
                        "id": "austrianationalidnumber",
                        "generickeywords": [],
                        "specifickeywords": ["identity number", "national id", "personalausweis republik österreich"],
                        "formats": [],
                        "similarentitiescount": 0,
                        "functionstosatisfy": []
                    },
                    {
                        "id": "austriapassportnumber",
                        "generickeywords": [],
                        "specifickeywords": ["passport number", "austrian passport number", "passport no", "reisepass", "österreichisch reisepass"],
                        "formats": ["? #######","?#######"],
                        "similarentitiescount": 0,
                        "functionstosatisfy": []
                    },
                    {
                        "id": "austriassn",
                        "generickeywords": [],
                        "specifickeywords": ["social security no", "social security number", "social security code", "insurance number", "austrian ssn", "ssn#", "ssn", "insurance code", "insurance code#", "socialsecurityno#", "sozialversicherungsnummer", "soziale sicherheit kein", "versicherungsnummer"],
                        "formats": [],
                        "similarentitiescount": 0,
                        "functionstosatisfy": []
                    },
                    {
                        "id": "austriataxidnumber",
                        "generickeywords": [],
                        "specifickeywords": ["österreich", "st.nr.", "steuernummer", "tax id", "tax identification no", "tax identification number", "tax no#", "tax no", "tax number", "tax registration number", "taxid#", "taxidno#", "taxidnumber#", "taxno#", "taxnumber#", "taxnumber", "tin id", "tin no", "tin#", "tax number"],
                        "formats": ["##-###'####","#########"],
                        "similarentitiescount": 0,
                        "functionstosatisfy": []
                    },
                    {
                        "id": "belgiumdriverlicencenumber",
                        "generickeywords": [],
                        "specifickeywords": ["dl#", "driver license", "driver license number", "driver licence", "drivers lic.", "drivers license", "drivers licence", "driver's license", "driver's license number", "driver's licence number", "dlno#", "rijbewijs", "rijbewijsnummer", "führerscheinnummer", "fuhrerscheinnummer", "fuehrerscheinnummer", "führerschein- nr", "fuehrerschein- Nr", "fuehrerschein- nr"],
                        "formats": ["##########"],
                        "similarentitiescount": 0,
                        "functionstosatisfy": []
                    },
                    {
                        "id": "belgiumnationalnumber",
                        "generickeywords": [],
                        "specifickeywords": ["belasting aantal", "bnn#", "bnn", "carte d’identité", "identifiant national", "identifiantnational#", "identificatie", "identification", "identifikation", "identifikationsnummer", "identifizierung", "identité", "identiteit", "identiteitskaart", "identity", "inscription", "national number", "national register", "nationalnumber#", "nationalnumber", "nif#", "nif", "numéro d'assuré", "numéro de registre national", "numéro de sécurité", "numéro d'identification", "numéro d'immatriculation", "numéro national", "numéronational#", "personal id number", "personalausweis", "personalidnumber#", "registratie", "registration", "registrationsnumme", "registrierung", "social security number", "ssn#", "ssn", "steuernummer", "tax id", "tax identification no", "tax identification number", "tax no#", "tax no", "tax number", "tax registration number", "taxid#", "taxidno#", "taxidnumber#", "taxno#", "taxnumber#", "taxnumber", "tin id", "tin no", "tin#"],
                        "formats": [],
                        "similarentitiescount": 0,
                        "functionstosatisfy": []
                    },
                    {
                        "id": "belgiumpassportnumber",
                        "generickeywords": [],
                        "specifickeywords": ["passport number", "belgian passport number", "passport no", "paspoort", "paspoortnummer", "reisepass kein", "reisepass"],
                        "formats": ["??######"],
                        "similarentitiescount": 0,
                        "functionstosatisfy": []
                    },
                    {
                        "id": "belgiumssn",
                        "generickeywords": [],
                        "specifickeywords": ["belgian national number", "national number", "social security number", "nationalnumber#", "ssn#", "ssn", "nationalnumber", "bnn#", "bnn", "personal id number", "personalidnumber#", "numéro national", "numéro de sécurité", "numéro d'assuré", "identifiant national", "identifiantnational#", "numéronational#"],
                        "formats": ["##########^"],
                        "similarentitiescount": 0,
                        "functionstosatisfy": []
                    },
                    {
                        "id": "belgiumtaxidnumber",
                        "generickeywords": [],
                        "specifickeywords": ["belasting aantal", "bnn#", "bnn", "carte d’identité", "identifiant national", "identifiantnational#", "identificatie", "identification", "identifikation", "identifikationsnummer", "identifizierung", "identité", "identiteit", "identiteitskaart", "identity", "inscription", "national number", "national register", "nationalnumber#", "nationalnumber", "nif#", "nif", "numéro d'assuré", "numéro de registre national", "numéro de sécurité", "numéro d'identification", "numéro d'immatriculation", "numéro national", "numéronational#", "personal id number", "personalausweis", "personalidnumber#", "registratie", "registration", "registrationsnumme", "registrierung", "social security number", "ssn#", "ssn", "steuernummer", "tax id", "tax identification no", "tax identification number", "tax no#", "tax no", "tax number", "tax registration number", "taxid#", "taxidno#", "taxidnumber#", "taxno#", "taxnumber#", "taxnumber", "tin id", "tin no", "tin#"],
                        "formats": [],
                        "similarentitiescount": 0,
                        "functionstosatisfy": []
                    },
                    {
                        "id": "brazilcpfnumber",
                        "generickeywords": [],
                        "specifickeywords": ["CPF", "Identification", "Registration", "Revenue", "Cadastro de Pessoas Físicas", "Imposto", "Identificação", "Inscrição", "Receita"],
                        "formats": ["###.###.###-^^","#########^^"],
                        "similarentitiescount": 0,
                        "functionstosatisfy": []
                    },
                    {
                        "id": "brazillegalentitynumber",
                        "generickeywords": [],
                        "specifickeywords": ["CNPJ", "CNPJ/MF", "CNPJ-MF", "National Registry of Legal Entities", "Taxpayers Registry", "Legal entity", "Legal entities", "Registration Status", "Business", "Company", "CNPJ", "Cadastro Nacional da Pessoa Jurídica", "Cadastro Geral de Contribuintes", "CGC", "Pessoa jurídica", "Pessoas jurídicas", "Situação cadastral", "Inscrição", "Empresa"],
                        "formats": [],
                        "similarentitiescount": 0,
                        "functionstosatisfy": []
                    },
                    {
                        "id": "brazilnationalidCard",
                        "generickeywords": [],
                        "specifickeywords": ["Cédula de identidade", "identity card", "national id", "número de rregistro", "registro de Iidentidade", "registro geral", "RG (this keyword is case sensitive)", "RIC (this keyword is case sensitive)"],
                        "formats": ["##.###.###-^","##########-^"],
                        "similarentitiescount": 0,
                        "functionstosatisfy": []
                    },
                    {
                        "id": "bulgariadriverslicensenumber",
                        "generickeywords": [],
                        "specifickeywords": ["dl#", "driver license", "driver license number", "driver licence", "drivers lic.", "drivers license", "drivers licence", "driver's license", "driver's license number", "driver's licence number", "driving license number", "dlno#", "свидетелство за управление на мпс", "свидетелство за управление на моторно превозно средство", "сумпс", "шофьорска книжка"],
                        "formats": ["#########"],
                        "similarentitiescount": 0,
                        "functionstosatisfy": []
                    },
                    {
                        "id": "bulgarianationalidnumber",
                        "generickeywords": [],
                        "specifickeywords": ["bnn#", "bnn", "bucn#", "bucn", "edinen grazhdanski nomer", "egn#", "egn", "identification number", "national id", "national number", "nationalnumber#", "nationalnumber", "personal id", "personal no", "personal number", "personalidnumber#", "social security number", "ssn#", "ssn", "uniform civil id", "uniform civil no", "uniform civil number", "uniformcivilno#", "uniformcivilno", "uniformcivilnumber#", "uniformcivilnumber", "unique citizenship number", "егн#", "егн", "единен граждански номер", "идентификационен номер", "личен номер", "лична идентификация", "лично не", "национален номер", "номер на гражданството", "униформ id", "униформ граждански id", "униформ граждански не", "униформ граждански номер", "униформгражданскиid#", "униформгражданскине.#"],
                        "formats": [],
                        "similarentitiescount": 0,
                        "functionstosatisfy": []
                    },
                    {
                        "id": "bulgariapassportnumber",
                        "generickeywords": [],
                        "specifickeywords": ["passport number", "bulgarian passport number", "passport no", "номер на паспорта"],
                        "formats": ["#########"],
                        "similarentitiescount": 0,
                        "functionstosatisfy": []
                    },
                    {
                        "id": "bulgariataxidnumber",
                        "generickeywords": [],
                        "specifickeywords": ["bnn#", "bnn", "bucn#", "bucn", "edinen grazhdanski nomer", "egn#", "egn", "identification number", "national id", "national number", "nationalnumber#", "nationalnumber", "personal id", "personal no", "personal number", "personalidnumber#", "social security number", "ssn#", "ssn", "uniform civil id", "uniform civil no", "uniform civil number", "uniformcivilno#", "uniformcivilno", "uniformcivilnumber#", "uniformcivilnumber", "unique citizenship number", "егн#", "егн", "единен граждански номер", "идентификационен номер", "личен номер", "лична идентификация", "лично не", "национален номер", "номер на гражданството", "униформ id", "униформ граждански id", "униформ граждански не", "униформ граждански номер", "униформгражданскиid#", "униформгражданскине.#"],
                        "formats": ["##########"],
                        "similarentitiescount": 0,
                        "functionstosatisfy": []
                    },
                    {
                        "id": "canadabankaccnumber",
                        "generickeywords": [],
                        "specifickeywords": ["canada savings bonds", "canada revenue agency", "canadian financial institution", "direct deposit form", "canadian citizen", "legal representative", "notary public", "commissioner for oaths", "child care benefit", "universal child care", "canada child tax benefit", "income tax benefit", "harmonized sales tax", "social insurance number", "income tax refund", "child tax benefit", "territorial payments", "institution number", "deposit request", "banking information", "direct deposit"],
                        "formats": ["#####-###","0########"],
                        "similarentitiescount": 0,
                        "functionstosatisfy": []
                    },
                    {
                        "id": "canadadriverslicensenumber",
                        "generickeywords": [],
                        "specifickeywords": ["DL", "DLS", "CDL", "CDLS", "DriverLic", "DriverLics", "DriverLicense", "DriverLicenses", "DriverLicence", "DriverLicences", "Driver Lic", "Driver Lics", "Driver License", "Driver Licenses", "Driver Licence", "Driver Licences", "DriversLic", "DriversLics", "DriversLicence", "DriversLicences", "DriversLicense", "DriversLicenses", "Drivers Lic", "Drivers Lics", "Drivers License", "Drivers Licenses", "Drivers Licence", "Drivers Licences", "Driver'Lic", "Driver'Lics", "Driver'License", "Driver'Licenses", "Driver'Licence", "Driver'Licences", "Driver' Lic", "Driver' Lics", "Driver' License", "Driver' Licenses", "Driver' Licence", "Driver' Licences", "Driver'sLic", "Driver'sLics", "Driver'sLicense", "Driver'sLicenses", "Driver'sLicence", "Driver'sLicences", "Driver's Lic", "Driver's Lics", "Driver's License", "Driver's Licenses", "Driver's Licence", "Driver's Licences", "Permis de Conduire", "id", "ids", "idcard number", "idcard numbers", "idcard #", "idcard #s", "idcard card", "idcard cards", "idcard", "identification number", "identification numbers", "identification #", "identification #s", "identification card", "identification cards", "identification", "DL#", "DLS#", "CDL#", "CDLS#", "DriverLic#", "DriverLics#", "DriverLicense#", "DriverLicenses#", "DriverLicence#", "DriverLicences#", "Driver Lic#", "Driver Lics#", "Driver License#", "Driver Licenses#", "Driver License#", "Driver Licences#", "DriversLic#", "DriversLics#", "DriversLicense#", "DriversLicenses#", "DriversLicence#", "DriversLicences#", "Drivers Lic#", "Drivers Lics#", "Drivers License#", "Drivers Licenses#", "Drivers Licence#", "Drivers Licences#", "Driver'Lic#", "Driver'Lics#", "Driver'License#", "Driver'Licenses#", "Driver'Licence#", "Driver'Licences#", "Driver' Lic#", "Driver' Lics#", "Driver' License#", "Driver' Licenses#", "Driver' Licence#", "Driver' Licences#", "Driver'sLic#", "Driver'sLics#", "Driver'sLicense#", "Driver'sLicenses#", "Driver'sLicence#", "Driver'sLicences#", "Driver's Lic#", "Driver's Lics#", "Driver's License#", "Driver's Licenses#", "Driver's Licence#", "Driver's Licences#", "Permis de Conduire#", "id#", "ids#", "idcard card#", "idcard cards#", "idcard#", "identification card#", "identification cards#", "identification#"],
                        "formats": [],
                        "similarentitiescount": 0,
                        "functionstosatisfy": []
                    },
                    {
                        "id": "canadahealthservicenumber",
                        "generickeywords": [],
                        "specifickeywords": ["personal health number", "patient information", "health services", "speciality services", "automobile accident", "patient hospital", "psychiatrist", "workers compensation", "disability"],
                        "formats": ["##########"],
                        "similarentitiescount": 0,
                        "functionstosatisfy": []
                    },
                    {
                        "id": "canadapassportnumber",
                        "generickeywords": [],
                        "specifickeywords": ["canadian citizenship", "canadian passport", "passport application", "passport photos", "certified translator", "canadian citizens", "processing times", "renewal application", "Passport Number", "Passport No", "Passport #", "Passport#", "PassportID", "Passportno", "passportnumber", "パスポート", "パスポート番号", "パスポートのNum", "パスポート＃", "Numéro de passeport", "Passeport n °", "Passeport Non", "Passeport #", "Passeport#", "PasseportNon", "Passeportn °"],
                        "formats": [],
                        "similarentitiescount": 0,
                        "functionstosatisfy": []
                    },
                    {
                        "id": "canadapersonalhealthidnumber",
                        "generickeywords": [],
                        "specifickeywords": ["social insurance number", "health information act", "income tax information", "manitoba health", "health registration", "prescription purchases", "benefit eligibility", "personal health", "power of attorney", "registration number", "personal health number", "practitioner referral", "wellness professional", "patient referral", "health and wellness", "Nunavut", "Quebec", "Northwest Territories", "Ontario", "British Columbia", "Alberta", "Saskatchewan", "Manitoba", "Yukon", "Newfoundland and Labrador", "New Brunswick", "Nova Scotia", "Prince Edward Island", "Canada"],
                        "formats": ["#########"],
                        "similarentitiescount": 0,
                        "functionstosatisfy": []
                    },
                    {
                        "id": "canadasocialinsurancenumber",
                        "generickeywords": [],
                        "specifickeywords": ["sin", "social insurance", "numero d'assurance sociale", "sins", "ssn", "ssns", "social security", "numero d'assurance social", "national identification number", "national id", "sin#", "soc ins", "social ins", "driver's license", "drivers license", "driver's licence", "drivers licence", "DOB", "Birthdate", "Birthday", "Date of Birth"],
                        "formats": ["###-###-###","### ### ###","#########"],
                        "similarentitiescount": 0,
                        "functionstosatisfy": []
                    },
                    {
                        "id": "chileidcardnumber",
                        "generickeywords": [],
                        "specifickeywords": ["National Identification Number", "Identity card", "ID", "Identification", "Rol Único Nacional", "RUN", "Rol Único Tributario", "RUT", "Cédula de Identidad", "Número De Identificación Nacional", "Tarjeta de identificación", "Identificación"],
                        "formats": ["!#.###.###-^"],
                        "similarentitiescount": 0,
                        "functionstosatisfy": []
                    },
                    {
                        "id": "chinaresidentidcardnumber",
                        "generickeywords": [],
                        "specifickeywords": ["Resident Identity Card", "PRC", "National Identification Card", "身份证", "居民 身份证", "居民身份证", "鉴定", "身分證", "居民 身份證", "鑑定"],
                        "formats": [],
                        "similarentitiescount": 0,
                        "functionstosatisfy": []
                    },
                    {
                        "id": "chinacreditcardnumber",
                        "generickeywords": [],
                        "specifickeywords": ["card verification", "card identification number", "cvn", "cid", "cvc2", "cvv2", "pin block", "security code", "security number", "security no", "issue number", "issue no", "cryptogramme", "numéro de sécurité", "numero de securite", "kreditkartenprüfnummer", "kreditkartenprufnummer", "prüfziffer", "prufziffer", "sicherheits Kode", "sicherheitscode", "sicherheitsnummer", "verfalldatum", "codice di verifica", "cod. sicurezza", "cod sicurezza", "n autorizzazione", "código", "codigo", "cod. seg", "cod seg", "código de segurança", "codigo de seguranca", "codigo de segurança", "código de seguranca", "cód. segurança", "cod. seguranca cod. segurança", "cód. seguranca", "cód segurança", "cod seguranca cod segurança", "cód seguranca", "número de verificação", "numero de verificacao", "ablauf", "gültig bis", "gültigkeitsdatum", "gultig bis", "gultigkeitsdatum", "scadenza", "data scad", "fecha de expiracion", "fecha de venc", "vencimiento", "válido hasta", "valido hasta", "vto", "data de expiração", "data de expiracao", "data em que expira", "validade", "valor", "vencimento", "Venc", "amex", "american express", "americanexpress", "Visa", "mastercard", "master card", "mc", "mastercards", "master cards", "diner's Club", "diners club", "dinersclub", "discover card", "discovercard", "discover cards", "JCB", "japanese card bureau", "carte blanche", "carteblanche", "credit card", "cc#", "cc#:", "expiration date", "exp date", "expiry date", "date d'expiration", "date d'exp", "date expiration", "bank card", "bankcard", "card number", "card num", "cardnumber", "cardnumbers", "card numbers", "creditcard", "credit cards", "creditcards", "ccn", "card holder", "cardholder", "card holders", "cardholders", "check card", "checkcard", "check cards", "checkcards", "debit card", "debitcard", "debit cards", "debitcards", "atm card", "atmcard", "atm cards", "atmcards", "enroute", "en route", "card type", "carte bancaire", "carte de crédit", "carte de credit", "numéro de carte", "numero de carte", "nº de la carte", "nº de carte", "kreditkarte", "karte", "karteninhaber", "karteninhabers", "kreditkarteninhaber", "kreditkarteninstitut", "kreditkartentyp", "eigentümername", "kartennr", "kartennummer", "kreditkartennummer", "kreditkarten-nummer", "carta di credito", "carta credito", "carta", "n carta", "nr. carta", "nr carta", "numero carta", "numero della carta", "numero di carta", "tarjeta credito", "tarjeta de credito", "tarjeta crédito", "tarjeta de crédito", "tarjeta de atm", "tarjeta atm", "tarjeta debito", "tarjeta de debito", "tarjeta débito", "tarjeta de débito", "nº de tarjeta", "no. de tarjeta", "no de tarjeta", "numero de tarjeta", "número de tarjeta", "tarjeta no", "tarjetahabiente", "cartão de crédito", "cartão de credito", "cartao de crédito", "cartao de credito", "cartão de débito", "cartao de débito", "cartão de debito", "cartao de debito", "débito automático", "debito automatico", "número do cartão", "numero do cartão", "número do cartao", "numero do cartao", "número de cartão", "numero de cartão", "número de cartao", "numero de cartao", "nº do cartão", "nº do cartao", "nº. do cartão", "no do cartão", "no do cartao", "no. do cartão", "no. do cartao"],
                        "formats": ["##############^^","#############^^","############^^"],
                        "similarentitiescount": 0,
                        "functionstosatisfy": []
                    },
                    {
                        "id": "croatiadriverslicencenumber",
                        "generickeywords": [],
                        "specifickeywords": ["dl#", "driver license", "driver license number", "driver licence", "drivers lic.", "drivers license", "drivers licence", "driver's license", "driver's license number", "driver's licence number", "driving license number", "dlno#", "vozačka dozvola"],
                        "formats": ["########"],
                        "similarentitiescount": 0,
                        "functionstosatisfy": []
                    },
                    {
                        "id": "croatiaidcardnumber",
                        "generickeywords": [],
                        "specifickeywords": ["majstorski broj građana", "master citizen number", "nacionalni identifikacijski broj", "national identification number", "oib#", "oib", "osobna iskaznica", "osobni id", "osobni identifikacijski broj", "personal identification number", "porezni broj", "porezni identifikacijski broj", "tax id", "tax identification no", "tax identification number", "tax no#", "tax no", "tax number", "tax registration number", "taxid#", "taxidno#", "taxidnumber#", "taxno#", "taxnumber#", "taxnumber", "tin id", "tin no", "tin#"],
                        "formats": ["#########"],
                        "similarentitiescount": 0,
                        "functionstosatisfy": []
                    },
                    {
                        "id": "croatiapassportnumber",
                        "generickeywords": [],
                        "specifickeywords": ["passport number", "croatian passport number", "passport no", "broj putovnice"],
                        "formats": ["#########"],
                        "similarentitiescount": 0,
                        "functionstosatisfy": []
                    },
                    {
                        "id": "croatiapersonalidnumber",
                        "generickeywords": [],
                        "specifickeywords": ["Personal Identification Number", "Osobni identifikacijski broj", "OIB"],
                        "formats": ["##########^"],
                        "similarentitiescount": 0,
                        "functionstosatisfy": []
                    },
                    {
                        "id": "croatiassn",
                        "generickeywords": [],
                        "specifickeywords": ["personal identification number", "master citizen number", "national identification number", "social security number", "nationalnumber#", "ssn#", "ssn", "nationalnumber", "bnn#", "bnn", "personal id number", "personalidnumber#", "oib", "osobni identifikacijski broj"],
                        "formats": ["##########^"],
                        "similarentitiescount": 0,
                        "functionstosatisfy": []
                    },
                    {
                        "id": "croatiataxidnumber",
                        "generickeywords": [],
                        "specifickeywords": ["majstorski broj građana", "master citizen number", "nacionalni identifikacijski broj", "national identification number", "oib#", "oib", "osobna iskaznica", "osobni id", "osobni identifikacijski broj", "personal identification number", "porezni broj", "porezni identifikacijski broj", "tax id", "tax identification no", "tax identification number", "tax no#", "tax no", "tax number", "tax registration number", "taxid#", "taxidno#", "taxidnumber#", "taxno#", "taxnumber#", "taxnumber", "tin id", "tin no", "tin#"],
                        "formats": ["##########^"],
                        "similarentitiescount": 0,
                        "functionstosatisfy": []
                    },
                    {
                        "id": "cyprusdriverslicencenumber",
                        "generickeywords": [],
                        "specifickeywords": ["dl#", "driver license", "driver license number", "driver licence", "drivers lic.", "drivers license", "drivers licence", "driver's license number", "driver's licence number", "driving license number", "dlno#", "άδεια οδήγησης"],
                        "formats": ["############"],
                        "similarentitiescount": 0,
                        "functionstosatisfy": []
                    },
                    {
                        "id": "cyprusnationalidnumber",
                        "generickeywords": [],
                        "specifickeywords": ["id card number", "identity card number", "kimlik karti", "national identification number", "personal id number", "ταυτοτητασ"],
                        "formats": ["##########"],
                        "similarentitiescount": 0,
                        "functionstosatisfy": []
                    },
                    {
                        "id": "cypruspassportnumber",
                        "generickeywords": [],
                        "specifickeywords": ["passport number", "cyprus passport number", "passport no", "αριθμό διαβατηρίου"],
                        "formats": ["?######!","?#######!"],
                        "similarentitiescount": 0,
                        "functionstosatisfy": []
                    },
                    {
                        "id": "cyprustaxidnumber",
                        "generickeywords": [],
                        "specifickeywords": ["tax id", "tax identification code", "tax identification no", "tax identification number", "tax no#", "tax no", "tax number", "tax registration number", "taxid#", "taxidno#", "taxidnumber#", "taxno#", "taxnumber#", "taxnumber", "tic#", "tic", "tin id", "tin no", "tin#", "vergi kimlik kodu", "vergi kimlik numarası", "αριθμός φορολογικού μητρώου", "κωδικός φορολογικού μητρώου", "φορολογική ταυτότητα", "φορολογικού κωδικού", "tax number"],
                        "formats": ["0#######?"],
                        "similarentitiescount": 0,
                        "functionstosatisfy": []
                    },
                    {
                        "id": "czechdriverslicensenumber",
                        "generickeywords": [],
                        "specifickeywords": ["dl#", "driver license", "driver license number", "driver licence", "drivers lic.", "drivers license", "drivers licence", "driver's license", "driver's license number", "driver's license number", "driver's licence number", "driving license number", "dlno#", "řidičský prúkaz"],
                        "formats": ["?? ######","??######"],
                        "similarentitiescount": 0,
                        "functionstosatisfy": []
                    },
                    {
                        "id": "czechpassportnumber",
                        "generickeywords": [],
                        "specifickeywords": ["passport number", "czech passport number", "passport no", "cestovní pas", "pas"],
                        "formats": ["########"],
                        "similarentitiescount": 0,
                        "functionstosatisfy": []
                    },
                    {
                        "id": "czechpersonalidnumber",
                        "generickeywords": [],
                        "specifickeywords": ["czech personal identity number", "Rodné číslo"],
                        "formats": [],
                        "similarentitiescount": 0,
                        "functionstosatisfy": []
                    },
                    {
                        "id": "czechssn",
                        "generickeywords": [],
                        "specifickeywords": ["birth number", "national identification number", "personal identification number", "social security number", "nationalnumber#", "ssn#", "ssn", "national number", "personal id number", "personalidnumber#", "rč", "rodné číslo", "rodne cislo"],
                        "formats": [],
                        "similarentitiescount": 0,
                        "functionstosatisfy": []
                    },
                    {
                        "id": "czechtaxidnumber",
                        "generickeywords": [],
                        "specifickeywords": ["czech republic id", "czechidno#", "daňové číslo", "identifikační číslo", "identity no", "identity number", "identityno#", "identityno", "insurance number", "national identification number", "national number", "osobní číslo", "personal id number", "personal number", "pid#", "pid", "pojištění číslo", "rodné číslo", "tax id", "tax identification no", "tax identification number", "tax no#", "tax no", "tax number", "tax registration number", "taxid#", "taxidno#", "taxidnumber#", "taxno#", "taxnumber#", "taxnumber", "tin id", "tin no", "tin#", "unique identification number", "tax number"],
                        "formats": ["######/###!","#########!"],
                        "similarentitiescount": 0,
                        "functionstosatisfy": []
                    },
                    {
                        "id": "denmarkdriverslicensenumber",
                        "generickeywords": [],
                        "specifickeywords": ["|dl#", "driver license", "driver license number", "driver licence", "drivers lic.", "drivers license", "drivers licence", "driver's license", "driver's license number", "driver's licence number", "driving license number", "dlno#", "kørekort", "kørekortnummer"],
                        "formats": ["#######^"],
                        "similarentitiescount": 0,
                        "functionstosatisfy": []
                    },
                    {
                        "id": "denmarkpassportnumber",
                        "generickeywords": [],
                        "specifickeywords": ["passport number", "danish passport number", "passport no", "pas", "pasnummer"],
                        "formats": ["#########"],
                        "similarentitiescount": 0,
                        "functionstosatisfy": []
                    },
                    {
                        "id": "denmarkpersonalidnumber",
                        "generickeywords": [],
                        "specifickeywords": ["centrale personregister", "civilt registreringssystem", "cpr", "cpr#", "gesundheitskarte nummer", "gesundheitsversicherungkarte nummer", "health card", "health insurance card number", "health insurance number", "identification number", "identifikationsnummer", "identifikationsnummer#", "identity number", "krankenkassennummer", "nationalid#", "personalidentityno#", "personnummer", "personnummer#", "reisekrankenversicherungskartenummer", "rejsesygesikringskort", "skat id", "skat kode", "skat nummer", "skattenummer", "sundhedsforsikringskort", "sundhedsforsikringsnummer", "sundhedskort", "sundhedskortnummer", "sygesikring", "sygesikringkortnummer", "tax code", "travel health insurance card", "uniqueidentityno#", "tax number", "tax registration number", "tax id", "tax identification number", "taxid#", "taxnumber#", "tax no", "taxno#", "taxnumber", "tax identification no", "tin#", "taxidno#", "taxidnumber#", "tax no#", "tin id", "tin no"],
                        "formats": [],
                        "similarentitiescount": 0,
                        "functionstosatisfy": []
                    },
                    {
                        "id": "denmarkssn",
                        "generickeywords": [],
                        "specifickeywords": ["personal identification number", "national identification number", "social security number", "nationalnumber#", "ssn#", "ssn", "national number", "personal id number", "personalidnumber#", "cpr-nummer", "personnummer"],
                        "formats": [],
                        "similarentitiescount": 0,
                        "functionstosatisfy": []
                    },
                    {
                        "id": "denmarktaxidnumber",
                        "generickeywords": [],
                        "specifickeywords": ["centrale personregister", "civilt registreringssystem", "cpr", "cpr#", "gesundheitskarte nummer", "gesundheitsversicherungkarte nummer", "health card", "health insurance card number", "health insurance number", "identification number", "identifikationsnummer", "identifikationsnummer#", "identity number", "krankenkassennummer", "nationalid#", "personalidentityno#", "personnummer", "personnummer#", "reisekrankenversicherungskartenummer", "rejsesygesikringskort", "skat id", "skat kode", "skat nummer", "skattenummer", "sundhedsforsikringskort", "sundhedsforsikringsnummer", "sundhedskort", "sundhedskortnummer", "sygesikring", "sygesikringkortnummer", "tax code", "travel health insurance card", "uniqueidentityno#", "tax number", "tax registration number", "tax id", "tax identification number", "taxid#", "taxnumber#", "tax no", "taxno#", "taxnumber", "tax identification no", "tin#", "taxidno#", "taxidnumber#", "tax no#", "tin id", "tin no"],
                        "formats": [],
                        "similarentitiescount": 0,
                        "functionstosatisfy": []
                    },
                    {
                        "id": "drugenforcementagencynumber",
                        "generickeywords": [],
                        "specifickeywords": ["DEA number","drug enforcement agency number"],
                        "formats": [],
                        "similarentitiescount": 0,
                        "functionstosatisfy": []
                    },
                    {
                        "id": "estoniadriverslicensenumber",
                        "generickeywords": [],
                        "specifickeywords": ["dl#", "driver license", "driver license number", "driver license number", "driver licence", "drivers lic.", "drivers license", "drivers licence", "driver's license", "driver's license number", "driving license number", "dlno#", "permis de conduire"],
                        "formats": ["ET######"],
                        "similarentitiescount": 0,
                        "functionstosatisfy": []
                    },
                    {
                        "id": "estonianationalidnumber",
                        "generickeywords": [],
                        "specifickeywords": ["id-kaart", "ik", "isikukood#", "isikukood", "maksu id", "maksukohustuslase identifitseerimisnumber", "maksunumber", "national identification number", "national number", "personal code", "personal id number", "personal identification code", "personal identification number", "personalidnumber#", "tax id", "tax identification no", "tax identification number", "tax no#", "tax no", "tax number", "tax registration number", "taxid#", "taxidno#", "taxidnumber#", "taxno#", "taxnumber#", "taxnumber", "tin id", "tin no", "tin#"],
                        "formats": [],
                        "similarentitiescount": 0,
                        "functionstosatisfy": []
                    },
                    {
                        "id": "estoniapassportnumber",
                        "generickeywords": [],
                        "specifickeywords": ["passport number", "estonian passport number", "passport no", "eesti kodaniku pass"],
                        "formats": ["?#######"],
                        "similarentitiescount": 0,
                        "functionstosatisfy": []
                    },
                    {
                        "id": "estoniataxidnumber",
                        "generickeywords": [],
                        "specifickeywords": ["id-kaart", "ik", "isikukood#", "isikukood", "maksu id", "maksukohustuslase identifitseerimisnumber", "maksunumber", "national identification number", "national number", "personal code", "personal id number", "personal identification code", "personal identification number", "personalidnumber#", "tax id", "tax identification no", "tax identification number", "tax no#", "tax no", "tax number", "tax registration number", "taxid#", "taxidno#", "taxidnumber#", "taxno#", "taxnumber#", "taxnumber", "tin id", "tin no", "tin#"],
                        "formats": [],
                        "similarentitiescount": 0,
                        "functionstosatisfy": []
                    },
                    {
                        "id": "eudebitcardnumber",
                        "generickeywords": [],
                        "specifickeywords": ["account number", "card number", "card no.", "security number", "cc#", "acct nbr", "acct num", "acct no", "american express", "americanexpress", "americano espresso", "amex", "atm card", "atm cards", "atm kaart", "atmcard", "atmcards", "atmkaart", "atmkaarten", "bancontact", "bank card", "bankkaart", "card holder", "card holders", "card num", "card number", "card numbers", "card type", "cardano numerico", "cardholder", "cardholders", "cardnumber", "cardnumbers", "carta bianca", "carta credito", "carta di credito", "cartao de credito", "cartao de crédito", "cartao de debito", "cartao de débito", "carte bancaire", "carte blanche", "carte bleue", "carte de credit", "carte de crédit", "carte di credito", "carteblanche", "cartão de credito", "cartão de crédito", "cartão de debito", "cartão de débito", "cb", "ccn", "check card", "check cards", "checkcard", "checkcards", "chequekaart", "cirrus", "cirrus-edc-maestro", "controlekaart", "controlekaarten", "credit card", "credit cards", "creditcard", "creditcards", "debetkaart", "debetkaarten", "debit card", "debit cards", "debitcard", "debitcards", "debito automatico", "diners club", "dinersclub", "discover", "discover card", "discover cards", "discovercard", "discovercards", "débito automático", "edc", "eigentümername", "european debit card", "hoofdkaart", "hoofdkaarten", "in viaggio", "japanese card bureau", "japanse kaartdienst", "jcb", "kaart", "kaart num", "kaartaantal", "kaartaantallen", "kaarthouder", "kaarthouders", "karte", "karteninhaber", "karteninhabers", "kartennr", "kartennummer", "kreditkarte", "kreditkarten-nummer", "kreditkarteninhaber", "kreditkarteninstitut", "kreditkartennummer", "kreditkartentyp", "maestro", "master card", "master cards", "mastercard", "mastercards", "mc", "mister cash", "n carta", "carta", "no de tarjeta", "no do cartao", "no do cartão", "no. de tarjeta", "no. do cartao", "no. do cartão", "nr carta", "nr. carta", "numeri di scheda", "numero carta", "numero de cartao", "numero de carte", "numero de cartão", "numero de tarjeta", "numero della carta", "numero di carta", "numero di scheda", "numero do cartao", "numero do cartão", "numéro de carte", "nº carta", "nº de carte", "nº de la carte", "nº de tarjeta", "nº do cartao", "nº do cartão", "nº. do cartão", "número de cartao", "número de cartão", "número de tarjeta", "número do cartao", "scheda dell'assegno", "scheda dell'atmosfera", "scheda dell'atmosfera", "scheda della banca", "scheda di controllo", "scheda di debito", "scheda matrice", "schede dell'atmosfera", "schede di controllo", "schede di debito", "schede matrici", "scoprono la scheda", "scoprono le schede", "solo", "supporti di scheda", "supporto di scheda", "switch", "tarjeta atm", "tarjeta credito", "tarjeta de atm", "tarjeta de credito", "tarjeta de debito", "tarjeta debito", "tarjeta no", "tarjetahabiente", "tipo della scheda", "ufficio giapponese della", "scheda", "v pay", "v-pay", "visa", "visa plus", "visa electron", "visto", "visum", "vpay", "card identification number", "card verification", "cardi la verifica", "cid", "cod seg", "cod seguranca", "cod segurança", "cod sicurezza", "cod. seg", "cod. seguranca", "cod. segurança", "cod. sicurezza", "codice di sicurezza", "codice di verifica", "codigo", "codigo de seguranca", "codigo de segurança", "crittogramma", "cryptogram", "cryptogramme", "cv2", "cvc", "cvc2", "cvn", "cvv", "cvv2", "cód seguranca", "cód segurança", "cód. seguranca", "cód. segurança", "código", "código de seguranca", "código de segurança", "de kaart controle", "geeft nr uit", "issue no", "issue number", "kaartidentificatienummer", "kreditkartenprufnummer", "kreditkartenprüfnummer", "kwestieaantal", "no. dell'edizione", "no. di sicurezza", "numero de securite", "numero de verificacao", "numero dell'edizione", "numero di identificazione della", "scheda", "numero di sicurezza", "numero van veiligheid", "numéro de sécurité", "nº autorizzazione", "número de verificação", "perno il blocco", "pin block", "prufziffer", "prüfziffer", "security code", "security no", "security number", "sicherheits kode", "sicherheitscode", "sicherheitsnummer", "speldblok", "veiligheid nr", "veiligheidsaantal", "veiligheidscode", "veiligheidsnummer", "verfalldatum", "ablauf", "data de expiracao", "data de expiração", "data del exp", "data di exp", "data di scadenza", "data em que expira", "data scad", "data scadenza", "date de validité", "datum afloop", "datum van exp", "de afloop", "espira", "espira", "exp date", "exp datum", "expiration", "expire", "expires", "expiry", "fecha de expiracion", "fecha de venc", "gultig bis", "gultigkeitsdatum", "gültig bis", "gültigkeitsdatum", "la scadenza", "scadenza", "valable", "validade", "valido hasta", "valor", "venc", "vencimento", "vencimiento", "verloopt", "vervaldag", "vervaldatum", "vto", "válido hasta"],
                        "formats": ["###############^"],
                        "similarentitiescount": 0,
                        "functionstosatisfy": []
                    },
                    {
                        "id": "finlanddriverslicensenumber",
                        "generickeywords": [],
                        "specifickeywords": ["dl#", "driver license", "driver license number", "driver licence", "drivers lic.", "drivers license", "drivers licence", "driver's license", "driver's license number", "driver's licence number", "driving license number", "dlno#", "ajokortti"],
                        "formats": ["######-####"],
                        "similarentitiescount": 0,
                        "functionstosatisfy": []
                    },
                    {
                        "id": "finlandnationalidnumber",
                        "generickeywords": [],
                        "specifickeywords": ["ainutlaatuinen henkilökohtainen tunnus", "henkilökohtainen tunnus", "henkilötunnus", "henkilötunnusnumero#", "henkilötunnusnumero", "hetu", "id no", "id number", "identification number","identiteetti numero", "identity number", "idnumber", "kansallinen henkilötunnus", "kansallisen henkilökortin", "national id card", "national id no.", "personal id", "personal identity code", "personalidnumber#", "personbeteckning", "personnummer", "social security number", "sosiaaliturvatunnus", "tax id", "tax identification no", "tax identification number", "tax no#", "tax no", "tax number", "tax registration number", "taxid#", "taxidno#", "taxidnumber#", "taxno#", "taxnumber#", "taxnumber", "tin id", "tin no", "tin#", "tunnistenumero", "tunnus numero", "tunnusluku", "tunnusnumero", "verokortti", "veronumero", "verotunniste", "verotunnus"],
                        "formats": [],
                        "similarentitiescount": 0,
                        "functionstosatisfy": []
                    },
                    {
                        "id": "finlandpassportnumber",
                        "generickeywords": [],
                        "specifickeywords": ["Keyword_finland_passport_number", "Passport", "Passi"],
                        "formats": ["??#######"],
                        "similarentitiescount": 0,
                        "functionstosatisfy": []
                    },
                    {
                        "id": "finlandssn",
                        "generickeywords": [],
                        "specifickeywords": ["identification number", "personal id", "identity number", "finnish national id number", "personalidnumber#", "national identification number", "id number", "national id no.", "national id number", "id no", "tunnistenumero", "henkilötunnus", "yksilöllinen henkilökohtainen tunnistenumero", "ainutlaatuinen henkilökohtainen tunnus", "identiteetti numero", "suomen kansallinen henkilötunnus", "henkilötunnusnumero#", "kansallisen tunnistenumero", "tunnusnumero", "kansallinen tunnus numero", "hetu"],
                        "formats": [],
                        "similarentitiescount": 0,
                        "functionstosatisfy": []
                    },
                    {
                        "id": "finlandtaxidnumber",
                        "generickeywords": [],
                        "specifickeywords": ["ainutlaatuinen henkilökohtainen tunnus", "henkilökohtainen tunnus", "henkilötunnus", "henkilötunnusnumero#", "henkilötunnusnumero", "hetu", "id no", "id number", "identification number","identiteetti numero", "identity number", "idnumber", "kansallinen henkilötunnus", "kansallisen henkilökortin", "national id card", "national id no.", "personal id", "personal identity code", "personalidnumber#", "personbeteckning", "personnummer", "social security number", "sosiaaliturvatunnus", "suomen kansallinen henkilötunnus", "tax id", "tax identification no", "tax identification number", "tax no#", "tax no", "tax number", "tax registration number", "taxid#", "taxidno#", "taxidnumber#", "taxno#", "taxnumber#", "taxnumber", "tin id", "tin no", "tin#", "tunnistenumero", "tunnus numero", "tunnusluku", "tunnusnumero", "verokortti", "veronumero", "verotunniste", "verotunnus"],
                        "formats": [],
                        "similarentitiescount": 0,
                        "functionstosatisfy": []
                    },
                    {
                        "id": "francedriverslicensenumber",
                        "generickeywords": [],
                        "specifickeywords": ["drivers licence", "drivers license", "driving licence", "driving license", "permis de conduire", "licence number", "license number", "licence numbers", "license numbers"],
                        "formats": ["############"],
                        "similarentitiescount": 0,
                        "functionstosatisfy": []
                    },
                    {
                        "id": "francenationalidcardnumber",
                        "generickeywords": [],
                        "specifickeywords": ["card number", "carte nationale d’identité", "carte nationale d'idenite no", "cni#", "cni", "compte bancaire", "national identification number", "national identity", "nationalidno#", "numéro d'assurance maladie", "numéro de carte vitale"],
                        "formats": ["############"],
                        "similarentitiescount": 0,
                        "functionstosatisfy": []
                    },
                    {
                        "id": "francepassportnumber",
                        "generickeywords": [],
                        "specifickeywords": ["Passport Number", "Passport No", "Passport #", "Passport#", "PassportID", "Passportno", "passportnumber", "パスポート", "パスポート番号", "パスポートのNum", "パスポート ＃", "Numéro de passeport", "Passeport n °", "Passeport Non", "Passeport #", "Passeport#", "PasseportNon", "Passeportn °"],
                        "formats": ["##??#####"],
                        "similarentitiescount": 0,
                        "functionstosatisfy": []
                    },
                    {
                        "id": "francessn",
                        "generickeywords": [],
                        "specifickeywords": ["insee", "securité sociale", "securite sociale", "national id", "national identification", "numéro d'identité", "no d'identité", "no. d'identité", "numero d'identite", "no d'identite", "no. d'identite", "social security number", "social security code", "social insurance number", "le numéro d'identification nationale", "d'identité nationale", "numéro de sécurité sociale", "le code de la sécurité sociale", "numéro d'assurance sociale", "numéro de sécu", "code sécu"],
                        "formats": ["############# ^^","#############^^"],
                        "similarentitiescount": 0,
                        "functionstosatisfy": []
                    },
                    {
                        "id": "francetaxidnumber",
                        "generickeywords": [],
                        "specifickeywords": ["numéro d'identification fiscale", "tax id", "tax identification no", "tax identification number", "tax no#", "tax no", "tax number", "tax registration number", "taxid#", "taxidno#", "taxidnumber#", "taxno#", "taxnumber#", "taxnumber", "tin id", "tin no", "tin#"],
                        "formats": [],
                        "similarentitiescount": 0,
                        "functionstosatisfy": []
                    },
                    {
                        "id": "germanydriverslicensenumber",
                        "generickeywords": [],
                        "specifickeywords": ["Führerschein", "Fuhrerschein", "Fuehrerschein", "Führerscheinnummer", "Fuhrerscheinnummer", "Fuehrerscheinnummer", "Führerschein-", "Fuhrerschein-", "Fuehrerschein-", "FührerscheinnummerNr", "FuhrerscheinnummerNr", "FuehrerscheinnummerNr", "FührerscheinnummerKlasse", "FuhrerscheinnummerKlasse", "FuehrerscheinnummerKlasse", "Führerschein- Nr", "Fuhrerschein- Nr", "Fuehrerschein- Nr", "Führerschein- Klasse", "Fuhrerschein- Klasse", "Fuehrerschein- Klasse", "FührerscheinnummerNr", "FuhrerscheinnummerNr", "FuehrerscheinnummerNr", "FührerscheinnummerKlasse", "FuhrerscheinnummerKlasse", "FuehrerscheinnummerKlasse", "Führerschein- Nr", "Fuhrerschein- Nr", "Fuehrerschein- Nr", "Führerschein- Klasse", "Fuhrerschein- Klasse", "Fuehrerschein- Klasse", "DL", "DLS", "Driv Lic", "Driv Licen", "Driv License", "Driv Licenses", "Driv Licence", "Driv Licences", "Driv Lic", "Driver Licen", "Driver License", "Driver Licenses", "Driver Licence", "Driver Licences", "Drivers Lic", "Drivers Licen", "Drivers License", "Drivers Licenses", "Drivers Licence", "Drivers Licences", "Driver's Lic", "Driver's Licen", "Driver's License", "Driver's Licenses", "Driver's Licence", "Driver's Licences", "Driving Lic", "Driving Licen", "Driving License", "Driving Licenses", "Driving Licence", "Driving Licences", "Nr-Führerschein", "Nr-Fuhrerschein", "Nr-Fuehrerschein", "No-Führerschein", "No-Fuhrerschein", "No-Fuehrerschein", "N-Führerschein", "N-Fuhrerschein", "N-Fuehrerschein", "Nr-Führerschein", "Nr-Fuhrerschein", "Nr-Fuehrerschein", "No-Führerschein", "No-Fuhrerschein", "No-Fuehrerschein", "N-Führerschein", "N-Fuhrerschein", "N-Fuehrerschein", "ausstellungsdatum", "ausstellungsort", "ausstellende behöde", "ausstellende behorde", "ausstellende behoerde"],
                        "formats": [],
                        "similarentitiescount": 0,
                        "functionstosatisfy": []
                    },
                    {
                        "id": "germanyidcardnumber",
                        "generickeywords": [],
                        "specifickeywords": ["ausweis", "gpid", "identification", "identifikation", "identifizierungsnummer", "identity card", "identity number", "id-nummer", "personal id", "personalausweis", "persönliche id nummer","persönliche identifikationsnummer", "persönliche-id-nummer"],
                        "formats": ["?########","##########"],
                        "similarentitiescount": 0,
                        "functionstosatisfy": []
                    },
                    {
                        "id": "germanypassportnumber",
                        "generickeywords": [],
                        "specifickeywords": ["reisepass", "reisepasse", "reisepassnummer", "passport", "passports", "geburtsdatum", "ausstellungsdatum", "ausstellungsort", "No-Reisepass Nr-Reisepass", "Reisepass-Nr", "bnationalit.t"],
                        "formats": [],
                        "similarentitiescount": 0,
                        "functionstosatisfy": []
                    },
                    {
                        "id": "germanytaxidnumber",
                        "generickeywords": [],
                        "specifickeywords": ["identifikationsnummer", "steuer id", "steueridentifikationsnummer", "steuernummer", "tax id", "tax identification no", "tax identification number", "tax no#", "tax no", "tax number", "tax registration number", "taxid#", "taxidno#", "taxidnumber#", "taxno#", "taxnumber#", "taxnumber", "tin id", "tin no", "tin#", "zinn#", "zinn", "zinnnummer"],
                        "formats": ["##########^"],
                        "similarentitiescount": 0,
                        "functionstosatisfy": []
                    },
                    {
                        "id": "greecedriverslicensenumber",
                        "generickeywords": [],
                        "specifickeywords": ["dlL#", "driver license", "driver license number", "driver licence", "drivers lic.", "drivers license", "drivers licence", "driver's license", "driver's license number", "driver's licence number", "driving license number", "dlno#", "δεια οδήγησης", "Adeia odigisis"],
                        "formats": ["#########"],
                        "similarentitiescount": 0,
                        "functionstosatisfy": []
                    },
                    {
                        "id": "greecenationalidcard",
                        "generickeywords": [],
                        "specifickeywords": ["greek id", "greek national id", "greek personal id card", "greek police id", "identity card", "tautotita", "ταυτότητα", "ταυτότητας"],
                        "formats": [],
                        "similarentitiescount": 0,
                        "functionstosatisfy": []
                    },
                    {
                        "id": "greecepassportnumber",
                        "generickeywords": [],
                        "specifickeywords": ["passport number", "greek passport number", "passport no", "διαβατηριο"],
                        "formats": ["??#######"],
                        "similarentitiescount": 0,
                        "functionstosatisfy": []
                    },
                    {
                        "id": "greecetaxidnumber",
                        "generickeywords": [],
                        "specifickeywords": ["afm#", "afm", "aφμ|aφμ αριθμός", "aφμ", "tax id", "tax identification no", "tax identification number", "tax no#", "tax no", "tax number", "tax registration number", "tax registry no", "tax registry number", "taxid#", "taxidno#", "taxidnumber#", "taxno#", "taxnumber#", "taxnumber", "taxregistryno#", "tin id", "tin no", "tin#", "αριθμός φορολογικού μητρώου", "τον αριθμό φορολογικού μητρώου", "φορολογικού μητρώου νο"],
                        "formats": ["#########"],
                        "similarentitiescount": 0,
                        "functionstosatisfy": []
                    },
                    {
                        "id": "hongkongidcardnumber",
                        "generickeywords": [],
                        "specifickeywords": ["hkid", "hong kong identity card", "HKIDC", "id card", "identity card", "hk identity card", "hong kong id", "香港身份證", "香港永久性居民身份證", "身份證", "身份証", "身分證", "身分証", "香港身份証", "香港身分證", "香港身分証", "香港身份證", "香港居民身份證", "香港居民身份証", "香港居民身分證", "香港居民身分証", "香港永久性居民身份証", "香港永久性居民身分證", "香港永久性居民身分証", "香港永久性居民身份證", "香港非永久性居民身份證", "香港非永久性居民身份証", "香港非永久性居民身分證", "香港非永久性居民身分証", "香港特別行政區永久性居民身份證", "香港特別行政區永久性居民身份証", "香港特別行政區永久性居民身分證", "香港特別行政區永久性居民身分証", "香港特別行政區非永久性居民身份證", "香港特別行政區非永久性居民身份証", "香港特別行政區非永久性居民身分證", "香港特別行政區非永久性居民身分証"],
                        "formats": ["?######^","??######^"],
                        "similarentitiescount": 0,
                        "functionstosatisfy": []
                    },
                    {
                        "id": "hungarydriverslicensenumber",
                        "generickeywords": [],
                        "specifickeywords": ["dl#", "driver license", "driver license number", "driver licence", "drivers lic.", "drivers license", "drivers licence", "driver's license", "driver's license number", "driver's licence number", "driving license number", "dlno#", "vezetoi engedely"],
                        "formats": ["??######"],
                        "similarentitiescount": 0,
                        "functionstosatisfy": []
                    },
                    {
                        "id": "hungarynationalidnumber",
                        "generickeywords": [],
                        "specifickeywords": ["id number", "identification number", "sz ig", "sz. ig.", "sz.ig.", "személyazonosító igazolvány", "személyi igazolvány"],
                        "formats": [],
                        "similarentitiescount": 0,
                        "functionstosatisfy": []
                    },
                    {
                        "id": "hungarypassportnumber",
                        "generickeywords": [],
                        "specifickeywords": ["passport number", "hungarian passport number", "passport no", "útlevél száma"],
                        "formats": ["??######","??#######"],
                        "similarentitiescount": 0,
                        "functionstosatisfy": []
                    },
                    {
                        "id": "hungaryssn",
                        "generickeywords": [],
                        "specifickeywords": ["hungarian social security number", "social security number", "socialsecuritynumber#", "hssn#", "socialsecuritynno", "hssn", "taj", "taj#", "ssn", "ssn#", "social security no", "áfa", "közösségi adószám", "általános forgalmi adó szám", "hozzáadottérték adó", "áfa szám", "magyar áfa szám"],
                        "formats": ["########^"],
                        "similarentitiescount": 0,
                        "functionstosatisfy": []
                    },
                    {
                        "id": "hungarytaxidnumber",
                        "generickeywords": [],
                        "specifickeywords": ["adóazonosító szám", "adóhatóság szám", "adószám", "hungarian tin", "hungatiantin#", "tax authority no", "tax id", "tax identification no", "tax identification number", "tax no#", "tax no", "tax number", "tax registration number", "taxid#", "taxidno#", "taxidnumber#", "taxno#", "taxnumber#", "taxnumber", "tin id", "tin no", "tin#", "vat number"],
                        "formats": ["8########^"],
                        "similarentitiescount": 0,
                        "functionstosatisfy": []
                    },
                    {
                        "id": "indiapermanentaccnumber",
                        "generickeywords": [],
                        "specifickeywords": ["Permanent Account Number", "PAN"],
                        "formats": ["?????####^"],
                        "similarentitiescount": 0,
                        "functionstosatisfy": []
                    },
                    {
                        "id": "indiauniqueidnumber",
                        "generickeywords": [],
                        "specifickeywords": ["Aadhar", "Aadhaar", "UID", "आधार"],
                        "formats": ["#### #### ###^","###########^"],
                        "similarentitiescount": 0,
                        "functionstosatisfy": []
                    },
                    {
                        "id": "indonesiaidcardnumber",
                        "generickeywords": [],
                        "specifickeywords": ["KTP", "Kartu Tanda Penduduk", "Nomor Induk Kependudukan"],
                        "formats": [],
                        "similarentitiescount": 0,
                        "functionstosatisfy": []
                    },
                    {
                        "id": "irelanddriverslicensenumber",
                        "generickeywords": [],
                        "specifickeywords": ["dl#", "driver license", "driver license number", "driver licence", "drivers lic.", "drivers license", "drivers licence", "driver's license", "driver's license number", "driver's licence number", "driving license number", "dlno#", "ceadúnas tiomána"],
                        "formats": ["######????"],
                        "similarentitiescount": 0,
                        "functionstosatisfy": []
                    },
                    {
                        "id": "irelandnationalidnumber",
                        "generickeywords": [],
                        "specifickeywords": ["client identity service", "identification number", "personal id number", "personal public service number", "personal service no", "phearsanta seirbhíse poiblí", "pps no", "pps number", "pps service no", "pps uimh", "ppsn", "ppsno#", "ppsno", "public service no", "publicserviceno#", "publicserviceno", "revenue and social insurance number", "rsi no", "rsi number", "rsin", "seirbhís aitheantais cliant", "uimh. psp", "uimhir aitheantais chánach", "uimhir aitheantais phearsanta", "uimhir phearsanta seirbhíse poiblí"],
                        "formats": [],
                        "similarentitiescount": 0,
                        "functionstosatisfy": []
                    },
                    {
                        "id": "irelandpassportnumber",
                        "generickeywords": [],
                        "specifickeywords": ["passport number", "irish passport number", "passport no", "pas", "passport", "passeport", "passeport numero"],
                        "formats": ["##########","??#######"],
                        "similarentitiescount": 0,
                        "functionstosatisfy": []
                    },
                    {
                        "id": "irelandpersonalpublicservicenumber",
                        "generickeywords": [],
                        "specifickeywords": ["Personal Public Service Number", "PPS Number", "PPS Num", "PPS No.", "PPS #", "PPS#", "PPSN", "Public Services Card", "Uimhir Phearsanta Seirbhíse Poiblí", "Uimh. PSP", "PSP"],
                        "formats": [],
                        "similarentitiescount": 0,
                        "functionstosatisfy": []
                    },
                    {
                        "id": "irelandtaxidnumber",
                        "generickeywords": [],
                        "specifickeywords": ["client identity service", "identification number", "personal id number", "personal public service number", "personal service no", "phearsanta seirbhíse poiblí", "pps no", "pps number", "pps service no", "pps uimh", "ppsn", "ppsno#", "ppsno", "public service no", "publicserviceno#", "publicserviceno", "revenue and social insurance number", "rsi no", "rsi number", "rsin", "seirbhís aitheantais cliant", "uimh. psp", "uimhir aitheantais chánach", "uimhir aitheantais phearsanta", "uimhir phearsanta seirbhíse poiblí"],
                        "formats": ["#######?"],
                        "similarentitiescount": 0,
                        "functionstosatisfy": []
                    },
                    {
                        "id": "israelbankaccnumber",
                        "generickeywords": [],
                        "specifickeywords": ["Bank Account Number", "Bank Account", "Account Number", "מספר חשבון בנק"],
                        "formats": ["##-###-########","#############"],
                        "similarentitiescount": 0,
                        "functionstosatisfy": []
                    },
                    {
                        "id": "israelnationalidnumber",
                        "generickeywords": [],
                        "specifickeywords": ["מספר זהות", "National ID Number"],
                        "formats": ["#########"],
                        "similarentitiescount": 0,
                        "functionstosatisfy": []
                    },
                    {
                        "id": "italydriverslicensenumber",
                        "generickeywords": [],
                        "specifickeywords": ["numero di patente di guida", "patente di guida"],
                        "formats": [],
                        "similarentitiescount": 0,
                        "functionstosatisfy": []
                    },
                    {
                        "id": "italynationalidnumber",
                        "generickeywords": [],
                        "specifickeywords": ["codice fiscal", "codice fiscale", "codice id personale", "codice personale", "fiscal code", "numero certificato personale", "numero di identificazione fiscale", "numero id personale", "numero personale", "personal certificate number", "personal code", "personal id code", "personal id number", "personalcodeno#", "tax code", "tax id", "tax identification no", "tax identification number", "tax identity number", "tax no#", "tax no", "tax number", "tax registration number", "taxid#", "taxidno#", "taxidnumber#", "taxno#", "taxnumber#", "taxnumber", "tin id", "tin no", "tin#"],
                        "formats": [],
                        "similarentitiescount": 0,
                        "functionstosatisfy": []
                    },
                    {
                        "id": "itaypassportnumber",
                        "generickeywords": [],
                        "specifickeywords": ["italian passport number", "repubblica italiana passaporto", "passaporto", "passaporto italiana", "passport number", "italiana passaporto numero", "passaporto numero", "numéro passeport italien", "numéro passeport"],
                        "formats": ["#########","??#######"],
                        "similarentitiescount": 0,
                        "functionstosatisfy": []
                    },
                    {
                        "id": "italytaxidnumber",
                        "generickeywords": [],
                        "specifickeywords": ["codice fiscal", "codice fiscale", "codice id personale", "codice personale", "fiscal code", "numero certificato personale", "numero di identificazione fiscale", "numero id personale", "numero personale", "personal certificate number", "personal code", "personal id code", "personal id number", "personalcodeno#", "tax code", "tax id", "tax identification no", "tax identification number", "tax identity number", "tax no#", "tax no", "tax number", "tax registration number", "taxid#", "taxidno#", "taxidnumber#", "taxno#", "taxnumber#", "taxnumber", "tin id", "tin no", "tin#"],
                        "formats": [],
                        "similarentitiescount": 0,
                        "functionstosatisfy": []
                    },
                    {
                        "id": "japanbankaccnumber",
                        "generickeywords": [],
                        "specifickeywords": ["Checking Account Number", "Checking Account", "Checking Account #", "Checking Acct Number", "Checking Acct #", "Checking Acct No.", "Checking Account No.", "Bank Account Number", "Bank Account", "Bank Account #", "Bank Acct Number", "Bank Acct #", "Bank Acct No.", "Bank Account No.", "Savings Account Number", "Savings Account", "Savings Account #", "Savings Acct Number", "Savings Acct #", "Savings Acct No.", "Savings Account No.", "Debit Account Number", "Debit Account", "Debit Account #", "Debit Acct Number", "Debit Acct #", "Debit Acct No.", "Debit Account No.", "口座番号を当座預金口座の確認", "＃アカウントの確認、勘定番号の確認", "＃勘定の確認", "勘定番号の確認", "口座番号の確認", "銀行口座番号", "銀行口座", "銀行口座＃", "銀行の勘定番号", "銀行のacct＃", "銀行の勘定いいえ", "銀行口座番号", "普通預金口座番号", "預金口座", "貯蓄口座＃", "貯蓄勘定の数", "貯蓄勘定＃", "貯蓄勘定番号", "普通預金口座番号", "引き落とし口座番号", "口座番号", "口座番号＃", "デビットのacct番号", "デビット勘定＃", "デビットACCTの番号", "デビット口座番号", "Otemachi"],
                        "formats": ["#######","########"],
                        "similarentitiescount": 0,
                        "functionstosatisfy": []
                    },
                    {
                        "id": "japandriverslicensenumber",
                        "generickeywords": [],
                        "specifickeywords": ["dl#", "DL＃", "dls#", "DLS＃", "driver license", "driver licenses", "drivers license", "driver's license", "drivers licenses", "driver's licenses", "driving licence", "lic#", "LIC＃", "lics#", "state id", "state identification", "state identification number", "低所得国＃", "免許証", "状態ID", "状態の識別", "状態の識別番号", "運転免許", "運転免許証", "運転免許証番号"],
                        "formats": ["############"],
                        "similarentitiescount": 0,
                        "functionstosatisfy": []
                    },
                    {
                        "id": "japanpassportnumber",
                        "generickeywords": [],
                        "specifickeywords": ["パスポート", "パスポート番号", "パスポートのNum", "パスポート＃"],
                        "formats": ["??#######"],
                        "similarentitiescount": 0,
                        "functionstosatisfy": []
                    },
                    {
                        "id": "japanresidencecardnumber",
                        "generickeywords": [],
                        "specifickeywords": ["Residence card number", "Residence card no", "Residence card #", "在留カード番号"],
                        "formats": ["??########??"],
                        "similarentitiescount": 0,
                        "functionstosatisfy": []
                    },
                    {
                        "id": "japanresidentregistrationnumber",
                        "generickeywords": [],
                        "specifickeywords": ["Resident Registration Number", "Resident Register Number", "Residents Basic Registry Number", "Resident Registration No.", "Resident Register No.", "Residents Basic Registry No.", "Basic Resident Register No.", "住民登録番号、登録番号をレジデント", "住民基本登録番号、登録番号", "住民基本レジストリ番号を常駐", "登録番号を常駐住民基本台帳登録番号"],
                        "formats": ["###########"],
                        "similarentitiescount": 0,
                        "functionstosatisfy": []
                    },
                    {
                        "id": "japanssn",
                        "generickeywords": [],
                        "specifickeywords": ["Social Insurance No.", "Social Insurance Num", "Social Insurance Number", "社会保険のテンキー", "社会保険番号"],
                        "formats": [],
                        "similarentitiescount": 0,
                        "functionstosatisfy": []
                    },
                    {
                        "id": "latviadriverslicensenumber",
                        "generickeywords": [],
                        "specifickeywords": ["dl#", "driver license", "driver license number", "driver licence", "drivers lic.", "drivers license", "drivers licence", "driver's license", "driver's license number", "driver's licence number", "driving license number", "dlno#", "autovadītāja apliecība"],
                        "formats": ["???######"],
                        "similarentitiescount": 0,
                        "functionstosatisfy": []
                    },
                    {
                        "id": "lativianationalidnumber",
                        "generickeywords": [],
                        "specifickeywords": ["administrative number", "alvas nē", "birth number", "citizen number", "civil number", "electronic census number", "electronic number", "fiscal code", "healthcare user number", "id#", "id-code", "identification number", "identifikācijas numurs", "id-number", "individual number", "latvija alva", "nacionālais id", "national id", "national identifying number", "national identity number", "national insurance number", "national register number", "nodokļa numurs", "nodokļu id", "nodokļu identifikācija numurs", "personal certificate number", "personal code", "personal id code", "personal id number", "personal identification code", "personal identifier", "personal identity number", "personal number", "personal numeric code", "personalcodeno#", "personas kods", "population identification code", "public service number", "registration number", "revenue number", "social insurance number", "social security number", "state tax code", "tax file number", "tax id", "tax identification no", "tax identification number", "tax no#", "tax no", "tax number", "taxid#", "taxidno#", "taxidnumber#", "taxno#", "taxnumber#", "taxnumber", "tin id", "tin no", "tin#", "voter’s number"],
                        "formats": [],
                        "similarentitiescount": 0,
                        "functionstosatisfy": []
                    },
                    {
                        "id": "latviapassportnumber",
                        "generickeywords": [],
                        "specifickeywords": ["passport number", "latvian passport number", "passport no", "pase numurs"],
                        "formats": ["#########","??#######"],
                        "similarentitiescount": 0,
                        "functionstosatisfy": []
                    },
                    {
                        "id": "latviataxidnumber",
                        "generickeywords": [],
                        "specifickeywords": ["administrative number", "alvas nē", "birth number", "citizen number", "civil number", "electronic census number", "electronic number", "fiscal code", "healthcare user number", "id#", "id-code", "identification number", "identifikācijas numurs", "id-number", "individual number", "latvija alva", "nacionālais id", "national id", "national identifying number", "national identity number", "national insurance number", "national register number", "nodokļa numurs", "nodokļu id", "nodokļu identifikācija numurs", "personal certificate number", "personal code", "personal id code", "personal id number", "personal identification code", "personal identifier", "personal identity number", "personal number", "personal numeric code", "personalcodeno#", "personas kods", "population identification code", "public service number", "registration number", "revenue number", "social insurance number", "social security number", "state tax code", "tax file number", "tax id", "tax identification no", "tax identification number", "tax no#", "tax no", "tax number", "taxid#", "taxidno#", "taxidnumber#", "taxno#", "taxnumber#", "taxnumber", "tin id", "tin no", "tin#", "voter’s number"],
                        "formats": [],
                        "similarentitiescount": 0,
                        "functionstosatisfy": []
                    },
                    {
                        "id": "lithuaniadriverslicensenumber",
                        "generickeywords": [],
                        "specifickeywords": ["dl#", "driver license", "driver license number", "driver licence", "drivers lic.", "drivers license", "drivers licence", "driver's license", "driver's license number", "driver's licence number", "driving license number", "dlno#", "vairuotojo pažymėjimas"],
                        "formats": ["########"],
                        "similarentitiescount": 0,
                        "functionstosatisfy": []
                    },
                    {
                        "id": "lithuanianationalidnumber",
                        "generickeywords": [],
                        "specifickeywords": ["asmeninis skaitmeninis kodas", "asmens kodas", "citizen service number", "mokesčių id", "mokesčių identifikavimas numeris", "mokesčių identifikavimo numeris", "mokesčių numeris", "national identification number", "personal code", "personal numeric code", "piliečio paslaugos numeris", "tax id", "tax identification no", "tax identification number", "tax no#", "tax no", "tax number", "tax registration number", "taxid#", "taxidno#", "taxidnumber#", "taxno#", "taxnumber#", "taxnumber", "tin id", "tin no", "tin#", "unikalus identifikavimo kodas", "unikalus identifikavimo numeris", "unique identification number", "unique identity number", "uniqueidentityno#"],
                        "formats": [],
                        "similarentitiescount": 0,
                        "functionstosatisfy": []
                    },
                    {
                        "id": "lithuaniapassportnumber",
                        "generickeywords": [],
                        "specifickeywords": ["passport number lithunian passport number passport no paso numeris"],
                        "formats": [],
                        "similarentitiescount": 0,
                        "functionstosatisfy": []
                    },
                    {
                        "id": "lithuaniataxidnumber",
                        "generickeywords": [],
                        "specifickeywords": ["asmeninis skaitmeninis kodas", "asmens kodas", "citizen service number", "mokesčių id", "mokesčių identifikavimas numeris", "mokesčių identifikavimo numeris", "mokesčių numeris", "national identification number", "personal code", "piliečio paslaugos numeris", "tax id", "tax identification no", "tax identification number", "tax no#", "tax no", "tax number", "tax registration number", "taxid#", "taxidno#", "taxidnumber#", "taxno#", "taxnumber#", "taxnumber", "tin id", "tin no", "tin#", "unikalus identifikavimo kodas", "unikalus identifikavimo numeris", "unique identification number", "unique identity number", "uniqueidentityno#"],
                        "formats": ["###########"],
                        "similarentitiescount": 0,
                        "functionstosatisfy": []
                    },
                    {
                        "id": "luxemburgdriverslicensenumber",
                        "generickeywords": [],
                        "specifickeywords": ["dl#", "driver license", "driver license number", "driver licence", "drivers lic.", "drivers license", "drivers licence", "driver's license", "driver's license number", "driver's licence number", "driving license number", "dlno#", "fahrerlaubnis"],
                        "formats": ["######"],
                        "similarentitiescount": 0,
                        "functionstosatisfy": []
                    },
                    {
                        "id": "luxemburgnationalidnumber",
                        "generickeywords": [],
                        "specifickeywords": ["eindeutige id", "eindeutige id-nummer", "eindeutigeid#", "id personnelle", "idpersonnelle#", "idpersonnelle", "individual code", "individual id", "individual identification", "individual identity", "numéro d'identification personnel", "personal id", "personal identification", "personal identity", "personalidno#", "personalidnumber#", "persönliche identifikationsnummer", "unique id", "unique identity", "uniqueidkey#"],
                        "formats": [],
                        "similarentitiescount": 0,
                        "functionstosatisfy": []
                    },
                    {
                        "id": "luxemburgpassportnumber",
                        "generickeywords": [],
                        "specifickeywords": ["passport number latvian passport number passport no passnummer"],
                        "formats": [],
                        "similarentitiescount": 0,
                        "functionstosatisfy": []
                    },
                    {
                        "id": "luxemburgtaxidnumber",
                        "generickeywords": [],
                        "specifickeywords": ["carte de sécurité sociale", "étain non", "étain#", "identifiant d'impôt", "luxembourg tax identifikatiounsnummer", "numéro d'étain", "numéro d'identification fiscal luxembourgeois", "numéro d'identification fiscale", "social security", "sozialunterstützung", "sozialversécherung", "sozialversicherungsausweis", "steier id", "steier identifikatiounsnummer", "steier nummer", "steuer id", "steueridentifikationsnummer", "steuernummer", "tax id", "tax identification no", "tax identification number", "tax no#", "tax no", "tax number", "tax registration number", "taxid#", "taxidno#", "taxidnumber#", "taxno#", "taxnumber#", "taxnumber", "tin id", "tin no", "tin#", "zinn#", "zinn", "zinnzahl"],
                        "formats": ["###########^^"],
                        "similarentitiescount": 0,
                        "functionstosatisfy": []
                    },
                    {
                        "id": "malaysiaidcardnumber",
                        "generickeywords": [],
                        "specifickeywords": ["digital application card", "i/c", "i/c no", "ic", "ic no", "id card", "identification Card", "identity card", "k/p", "k/p no", "kad akuan diri", "kad aplikasi digital", "kad pengenalan malaysia", "kp", "kp no", "mykad", "mykas", "mykid", "mypr", "mytentera", "malaysia identity card", "malaysian identity card", "nric", "personal identification card"],
                        "formats": [],
                        "similarentitiescount": 0,
                        "functionstosatisfy": []
                    },
                    {
                        "id": "maltadriverslicensenumber",
                        "generickeywords": [],
                        "specifickeywords": ["dl#", "driver license", "driver license number", "driver licence", "drivers lic.", "drivers license", "drivers licence", "driver's license", "driver's license number", "driver's licence number", "driving license number", "dlno#", "liċenzja tas-sewqan"],
                        "formats": ["## ### ###","?? ### ###","########","??######"],
                        "similarentitiescount": 0,
                        "functionstosatisfy": []
                    },
                    {
                        "id": "maltanationalidnumber",
                        "generickeywords": [],
                        "specifickeywords": ["citizen service number", "id tat-taxxa", "identifika numru tal-biljett", "kodiċi numerali personali", "numru ta 'identifikazzjoni personali", "numru ta 'identifikazzjoni tat-taxxa", "numru ta 'identifikazzjoni uniku", "numru ta' identità uniku", "numru tas-servizz taċ-ċittadin", "numru tat-taxxa", "personal numeric code", "unique identification number", "unique identity number", "uniqueidentityno#"],
                        "formats": [],
                        "similarentitiescount": 0,
                        "functionstosatisfy": []
                    },
                    {
                        "id": "maltapassportnumber",
                        "generickeywords": [],
                        "specifickeywords": ["passport number", "maltese passport number", "passport no", "numru tal-passaport"],
                        "formats": ["#######"],
                        "similarentitiescount": 0,
                        "functionstosatisfy": []
                    },
                    {
                        "id": "maltataxidnumber",
                        "generickeywords": [],
                        "specifickeywords": ["citizen service number", "id tat-taxxa", "identifika numru tal-biljett", "kodiċi numerali personali", "numru ta 'identifikazzjoni personali", "numru ta 'identifikazzjoni tat-taxxa", "numru ta 'identifikazzjoni uniku", "numru ta' identità uniku", "numru tas-servizz taċ-ċittadin", "numru tat-taxxa", "personal numeric code", "tax id", "tax identification no", "tax identification number", "tax no#", "tax no", "tax number", "tax registration number", "taxid#", "taxidno#", "taxidnumber#", "taxno#", "taxnumber#", "taxnumber", "tin id", "tin no", "tin#", "unique identification number", "unique identity number", "uniqueidentityno#"],
                        "formats": ["#######?","#########"],
                        "similarentitiescount": 0,
                        "functionstosatisfy": []
                    },
                    {
                        "id": "netherlandscitizenservicenumber",
                        "generickeywords": [],
                        "specifickeywords": ["bsn#", "bsn", "burgerservicenummer", "citizen service number", "person number", "personal number", "personal numeric code", "person-related number", "persoonlijk nummer", "persoonlijke numerieke code", "persoonsgebonden", "persoonsnummer", "sociaal-fiscaal nummer", "social-fiscal number", "sofi", "sofinummer", "uniek identificatienummer", "uniek identiteitsnummer", "unique identification number", "unique identity number", "uniqueidentityno#"],
                        "formats": ["### ### ##!","########!"],
                        "similarentitiescount": 0,
                        "functionstosatisfy": []
                    },
                    {
                        "id": "netherlandsdriverslicensenumber",
                        "generickeywords": [],
                        "specifickeywords": ["dl#", "driver license", "driver license number", "driver licence", "drivers lic.", "drivers license", "drivers licence", "driver's license", "driver's license number", "driver's licence number", "driving license number", "dlno#", "permis de conduire", "rijbewijs", "rijbewijsnummer"],
                        "formats": ["##########"],
                        "similarentitiescount": 0,
                        "functionstosatisfy": []
                    },
                    {
                        "id": "netherlandsnationalidnumber",
                        "generickeywords": [],
                        "specifickeywords": ["bsn#", "bsn", "burgerservicenummer", "citizen service number", "person number", "personal number", "personal numeric code", "person-related number", "persoonlijk nummer", "persoonlijke numerieke code", "persoonsgebonden", "persoonsnummer", "sociaal-fiscaal nummer", "social-fiscal number", "sofi", "sofinummer", "uniek identificatienummer", "uniek identiteitsnummer", "unique identification number", "unique identity number", "uniqueidentityno#"],
                        "formats": ["########^"],
                        "similarentitiescount": 0,
                        "functionstosatisfy": []
                    },
                    {
                        "id": "netherlandspassportnumber",
                        "generickeywords": [],
                        "specifickeywords": ["dutch passport number", "passport number", "netherlands passport number", "nederlanden paspoort nummer", "paspoort", "nederlanden paspoortnummer", "paspoortnummer"],
                        "formats": [],
                        "similarentitiescount": 0,
                        "functionstosatisfy": []
                    },
                    {
                        "id": "netherlandstaxidnumber",
                        "generickeywords": [],
                        "specifickeywords": ["btw nummer", "hollânske tax identification", "hulandes impuesto id number", "hulandes impuesto identification", "identificatienummer belasting", "identificatienummer van belasting", "impuesto identification number", "impuesto number", "nederlands belasting id nummer", "nederlands belasting identificatie", "nederlands belasting identificatienummer", "nederlands belastingnummer", "nederlandse belasting identificatie", "netherlands tax identification", "netherland's tax identification", "netherlands tin", "netherland's tin", "tax id", "tax identification no", "tax identification number", "tax identification tal", "tax no#", "tax no", "tax number", "tax registration number", "tax tal", "taxid#", "taxidno#", "taxidnumber#", "taxno#", "taxnumber#", "taxnumber", "tin id", "tin no", "tin#"],
                        "formats": ["#########"],
                        "similarentitiescount": 0,
                        "functionstosatisfy": []
                    },
                    {
                        "id": "newzealandministryofhealthnumber",
                        "generickeywords": [],
                        "specifickeywords": ["NHI", "New Zealand", "Health", "treatment"],
                        "formats": ["??? ###^","???###^"],
                        "similarentitiescount": 0,
                        "functionstosatisfy": []
                    },
                    {
                        "id": "norwayidnumber",
                        "generickeywords": [],
                        "specifickeywords": ["Personal identification number", "Norwegian ID Number", "ID Number", "Identification", "Personnummer", "Fødselsnummer"],
                        "formats": [],
                        "similarentitiescount": 0,
                        "functionstosatisfy": []
                    },
                    {
                        "id": "philippinesunifiedmultipurposeidnumber",
                        "generickeywords": [],
                        "specifickeywords": ["Unified Multi-Purpose ID", "UMID", "Identity Card", "Pinag-isang Multi-Layunin ID"],
                        "formats": ["####-#######-#"],
                        "similarentitiescount": 0,
                        "functionstosatisfy": []
                    },
                    {
                        "id": "polanddriverslicensenumber",
                        "generickeywords": [],
                        "specifickeywords": ["dl#", "driver license", "driver license number", "driver licence", "drivers lic.", "drivers license", "drivers licence", "driver's license", "driver's license number", "driver's licence number", "driving license number", "dlno#", "prawo jazdy"],
                        "formats": ["#####\\\##\\\#######"],
                        "similarentitiescount": 0,
                        "functionstosatisfy": []
                    },
                    {
                        "id": "polandidcard",
                        "generickeywords": [],
                        "specifickeywords": ["Dowód osobisty", "Numer dowodu osobistego", "Nazwa i numer dowodu osobistego", "Nazwa i nr dowodu osobistego", "Nazwa i nr dowodu tożsamości", "Dowód Tożsamości", "dow. os."],
                        "formats": ["???#####^"],
                        "similarentitiescount": 0,
                        "functionstosatisfy": []
                    },
                    {
                        "id": "polandnationalid",
                        "generickeywords": [],
                        "specifickeywords": ["dowód osobisty", "dowódosobisty", "niepowtarzalny numer", "niepowtarzalnynumer", "nr.-pesel", "nr-pesel", "numer identyfikacyjny", "pesel", "tożsamości narodowej"],
                        "formats": ["##########^"],
                        "similarentitiescount": 0,
                        "functionstosatisfy": []
                    },
                    {
                        "id": "polandpassportnumber",
                        "generickeywords": [],
                        "specifickeywords": ["Numer paszportu", "Nr. Paszportu", "Paszport"],
                        "formats": ["??#######"],
                        "similarentitiescount": 0,
                        "functionstosatisfy": []
                    },
                    {
                        "id": "polandtaxidnumber",
                        "generickeywords": [],
                        "specifickeywords": ["nip", "numer identyfikacji podatkowej", "numeridentyfikacjipodatkowej#", "tax id", "tax identification no", "tax identification number", "tax no#", "tax no", "tax number", "tax registration number", "taxid#", "taxidno#", "taxidnumber#", "taxno#", "taxnumber#", "taxnumber", "tin id", "tin no", "tin#", "vat id#", "vat id", "vat no", "vat number", "vatid#", "vatid", "vatno#"],
                        "formats": ["##########^"],
                        "similarentitiescount": 0,
                        "functionstosatisfy": []
                    },
                    {
                        "id": "potugalcitizencardnumber",
                        "generickeywords": [],
                        "specifickeywords": ["bilhete de identidade", "cartão de cidadão", "citizen card", "document number", "documento de identificação", "id number", "identification no", "identification number", "identity card no", "identity card number", "national id card", "nic", "número bi de portugal", "número de identificação civil", "número de identificação fiscal", "número do documento", "portugal bi number"],
                        "formats": ["########"],
                        "similarentitiescount": 0,
                        "functionstosatisfy": []
                    },
                    {
                        "id": "potugaldriverslicensenumber",
                        "generickeywords": [],
                        "specifickeywords": ["dl#", "driver license", "driver license number", "driver licence", "drivers lic.", "drivers license", "drivers licence", "driver's license", "driver's license number", "driver's licence number", "driving license number", "dlno#", "carteira de motorista"],
                        "formats": ["??-###### #"],
                        "similarentitiescount": 0,
                        "functionstosatisfy": []
                    },
                    {
                        "id": "potugalpassportnumber",
                        "generickeywords": [],
                        "specifickeywords": ["passport number portuguese passport number passport no número do passaporte"],
                        "formats": ["?######"],
                        "similarentitiescount": 0,
                        "functionstosatisfy": []
                    },
                    {
                        "id": "potugaltaxidnumber",
                        "generickeywords": [],
                        "specifickeywords": ["cpf#", "cpf", "nif#", "nif", "número de identificação fisca", "numero fiscal", "tax id", "tax identification no", "tax identification number", "tax no#", "tax no", "tax number", "tax registration number", "taxid#", "taxidno#", "taxidnumber#", "taxno#", "taxnumber#", "taxnumber", "tin id", "tin no", "tin#"],
                        "formats": ["########^"],
                        "similarentitiescount": 0,
                        "functionstosatisfy": []
                    },
                    {
                        "id": "romaniadriverslicensenumber",
                        "generickeywords": [],
                        "specifickeywords": ["dl#", "driver license", "driver license number", "driver licence", "drivers lic.", "drivers license", "drivers licence", "driver's license", "driver's license number", "driver's licence number", "driving license number", "dlno#", "permis de conducere"],
                        "formats": ["?########","#########"],
                        "similarentitiescount": 0,
                        "functionstosatisfy": []
                    },
                    {
                        "id": "romanianationalid",
                        "generickeywords": [],
                        "specifickeywords": ["cnp#", "cnp", "cod identificare personal", "cod numeric personal", "cod unic identificare", "codnumericpersonal#", "codul fiscal nr.", "identificarea fiscală nr#", "id-ul taxei", "insurance number", "insurancenumber#", "national id#", "national id", "national identification number", "număr identificare personal", "număr identitate", "număr personal unic", "număridentitate#", "număridentitate", "numărpersonalunic#", "numărpersonalunic", "număru de identificare fiscală", "numărul de identificare fiscală", "personal numeric code", "pin#", "pin", "tax file no","tax file number", "tax id", "tax identification no", "tax identification number", "tax no#", "tax no", "tax number", "tax registration number", "taxid#", "taxidno#", "taxidnumber#", "taxno#", "taxnumber#", "taxnumber", "tin id", "tin no", "tin#", "unique identification number", "unique identity number", "uniqueidentityno#", "uniqueidentityno"],
                        "formats": ["############^"],
                        "similarentitiescount": 0,
                        "functionstosatisfy": []
                    },
                    {
                        "id": "romaniapassportnumber",
                        "generickeywords": [],
                        "specifickeywords": ["passport number", "romanian passport number", "passport no", "numărul pașaportului"],
                        "formats": ["########!"],
                        "similarentitiescount": 0,
                        "functionstosatisfy": []
                    },
                    {
                        "id": "romaniataxidnumber",
                        "generickeywords": [],
                        "specifickeywords": ["cnp#", "cnp", "cod identificare personal", "cod numeric personal", "cod unic identificare", "codnumericpersonal#", "codul fiscal nr.", "identificarea fiscală nr #", "id-ul taxei", "insurance number", "insurancenumber#", "national id#", "national id", "national identification number", "număr identificare personal", "număr identitate", "număr personal unic", "număridentitate#", "număridentitate", "numărpersonalunic#", "numărpersonalunic", "număru de identificare fiscală", "numărul de identificare fiscală", "personal numeric code", "pin#", "pin", "tax file no", "tax file number", "tax id", "tax identification no", "tax identification number", "tax no#", "tax no", "tax number", "tax registration number", "taxid#", "taxidno#", "taxidnumber#", "taxno#", "taxnumber#", "taxnumber", "tin id", "tin no", "tin#", "unique identification number", "unique identity number", "uniqueidentityno#", "uniqueidentityno"],
                        "formats": ["#############"],
                        "similarentitiescount": 0,
                        "functionstosatisfy": []
                    },
                    {
                        "id": "saudiarabianationalid",
                        "generickeywords": [],
                        "specifickeywords": ["Identification Card", "I card number", "ID number", "الوطنية الهوية بطاقة رقم"],
                        "formats": ["##########"],
                        "similarentitiescount": 0,
                        "functionstosatisfy": []
                    },
                    {
                        "id": "singaporenationalregistrationidcard",
                        "generickeywords": [],
                        "specifickeywords": ["National Registration Identity Card", "Identity Card Number", "NRIC", "IC", "Foreign Identification Number", "FIN", "身份证", "身份證"],
                        "formats": [],
                        "similarentitiescount": 0,
                        "functionstosatisfy": []
                    },
                    {
                        "id": "slovakiadriverslicensenumber",
                        "generickeywords": [],
                        "specifickeywords": ["dl# driver license driver license number driver licence drivers lic. drivers license drivers licence driver's license driver's license number driver's licence number driving license number dlno# vodičský preukaz"],
                        "formats": ["?#######","########"],
                        "similarentitiescount": 0,
                        "functionstosatisfy": []
                    },
                    {
                        "id": "slovakianationalid",
                        "generickeywords": [],
                        "specifickeywords": ["azonosító szám", "birth number", "číslo národnej identifikačnej karty", "číslo občianského preukazu", "daňové číslo", "id number", "identification no", "identification number", "identifikačná karta č", "identifikačné číslo", "identity card no", "identity card number", "národná identifikačná značka č", "national number", "nationalnumber#", "nemzeti személyazonosító igazolvány", "personalidnumber#", "rč", "rodne cislo", "rodné číslo", "social security number", "ssn#", "ssn", "személyi igazolvány szám", "személyi igazolvány száma", "személyigazolvány szám", "tax file no", "tax file number", "tax id", "tax identification no", "tax identification number", "tax no#", "tax no", "tax number", "tax registration number", "taxid#", "taxidno#", "taxidnumber#", "taxno#", "taxnumber#", "taxnumber", "tin id", "tin no", "tin#"],
                        "formats": ["######/###^"],
                        "similarentitiescount": 0,
                        "functionstosatisfy": []
                    },
                    {
                        "id": "slovakiapassportnumber",
                        "generickeywords": [],
                        "specifickeywords": ["passport number", "slovakian passport number", "passport no", "číslo pasu"],
                        "formats": ["?#######","########"],
                        "similarentitiescount": 0,
                        "functionstosatisfy": []
                    },
                    {
                        "id": "slovakiataxidnumber",
                        "generickeywords": [],
                        "specifickeywords": ["azonosító szám", "birth number", "číslo národnej identifikačnej karty", "číslo občianského preukazu", "daňové číslo", "id number", "identification no", "identification number", "identifikačná karta č", "identifikačné číslo", "identity card no", "identity card number", "národná identifikačná značka č", "national number", "nationalnumber#", "nemzeti személyazonosító igazolvány", "personalidnumber#", "rč", "rodne cislo", "rodné číslo", "social security number", "ssn#", "ssn", "személyi igazolvány szám", "személyi igazolvány száma", "személyigazolvány szám", "tax file no", "tax file number", "tax id", "tax identification no", "tax identification number", "tax no#", "tax no", "tax number", "tax registration number", "taxid#", "taxidno#", "taxidnumber#", "taxno#", "taxnumber#", "taxnumber", "tin id", "tin no", "tin#"],
                        "formats": ["##########"],
                        "similarentitiescount": 0,
                        "functionstosatisfy": []
                    },
                    {
                        "id": "sloveniadriverslicensenumber",
                        "generickeywords": [],
                        "specifickeywords": ["dl#", "driver license", "driver license number", "driver licence", "drivers lic.", "drivers license", "drivers licence", "driver's license", "driver's license number", "driver's licence number", "driving license number", "dlno#", "vozniško dovoljenje"],
                        "formats": ["#########"],
                        "similarentitiescount": 0,
                        "functionstosatisfy": []
                    },
                    {
                        "id": "slovenianationalid",
                        "generickeywords": [],
                        "specifickeywords": ["edinstvena številka glavnega državljana", "emšo", "enotna maticna številka obcana", "id card", "identification number", "identifikacijska številka", "identity card", "nacionalna id", "nacionalni potni list", "national id", "osebna izkaznica", "osebni koda", "osebni ne", "osebni številka", "personal code", "personal number", "personal numeric code", "številka državljana", "unique citizen number", "unique id number", "unique identity number", "unique master citizen number", "unique registration number", "uniqueidentityno #", "uniqueidentityno#"],
                        "formats": [],
                        "similarentitiescount": 0,
                        "functionstosatisfy": []
                    },
                    {
                        "id": "sloveniapassportnumber",
                        "generickeywords": [],
                        "specifickeywords": ["passport number slovenian passport number passport no številka potnega lista"],
                        "formats": [],
                        "similarentitiescount": 0,
                        "functionstosatisfy": []
                    },
                    {
                        "id": "sloveniataxidnumber",
                        "generickeywords": [],
                        "specifickeywords": ["davčna številka", "identifikacijska številka davka", "številka davčne datoteke", "tax file no", "tax file number", "tax id", "tax identification no", "tax identification number", "tax no#", "tax no", "tax number", "tax registration number", "taxid#", "taxidno#", "taxidnumber#", "taxno#", "taxnumber#", "taxnumber", "tin id", "tin no", "tin#"],
                        "formats": ["########"],
                        "similarentitiescount": 0,
                        "functionstosatisfy": []
                    },
                    {
                        "id": "southafricaidnumber",
                        "generickeywords": [],
                        "specifickeywords": ["Identity card", "ID", "Identification"],
                        "formats": [],
                        "similarentitiescount": 0,
                        "functionstosatisfy": []
                    },
                    {
                        "id": "southkorearesidentregistrationnumber",
                        "generickeywords": [],
                        "specifickeywords": ["National ID card", "Citizen's Registration Number", "Jumin deungnok beonho", "RRN", "주민등록번호"],
                        "formats": [],
                        "similarentitiescount": 0,
                        "functionstosatisfy": []
                    },
                    {
                        "id": "spaindriverslicensenumber",
                        "generickeywords": [],
                        "specifickeywords": ["dlno#", "dl#", "drivers lic.", "driver licence", "driver license", "drivers licence", "drivers license", "driver's licence", "driver's license", "driving licence", "driving license", "driver licence number", "driver license number", "drivers licence number", "drivers license number", "driver's licence number", "driver's license number", "driving licence number", "driving license number", "driving permit", "driving permit number", "permiso de conducción", "permiso conducción", "número licencia conducir", "número de carnet de conducir", "número carnet conducir", "licencia conducir", "número de permiso de conducir", "número de permiso conducir", "número permiso conducir", "permiso conducir", "licencia de manejo", "el carnet de conducir", "carnet conducir"],
                        "formats": ["#######^#","#######^?"],
                        "similarentitiescount": 0,
                        "functionstosatisfy": []
                    },
                    {
                        "id": "spainnationalid",
                        "generickeywords": [],
                        "specifickeywords": ["carné de identidad", "dni#", "dni", "dninúmero#", "documento nacional de identidad", "identidad único", "identidadúnico#", "insurance number", "national identification number", "national identity", "nationalid#", "nationalidno#", "nie#", "nie", "nienúmero#", "número de identificación", "número nacional identidad", "personal identification number", "personal identity no", "unique identity number", "uniqueid#"],
                        "formats": ["########","#######?"],
                        "similarentitiescount": 0,
                        "functionstosatisfy": []
                    },
                    {
                        "id": "spainpassportnumber",
                        "generickeywords": [],
                        "specifickeywords": ["passport", "spain passport", "passport book", "passport number", "passport no", "libreta pasaporte", "número pasaporte", "españa pasaporte", "pasaporte"],
                        "formats": [],
                        "similarentitiescount": 0,
                        "functionstosatisfy": []
                    },
                    {
                        "id": "spainssn",
                        "generickeywords": [],
                        "specifickeywords": [],
                        "formats": ["##\\\#######!\\\##"],
                        "similarentitiescount": 0,
                        "functionstosatisfy": []
                    },
                    {
                        "id": "spaintaxidnumber",
                        "generickeywords": [],
                        "specifickeywords": ["cif", "cifid#", "cifnúmero#", "número de contribuyente", "número de identificación fiscal", "número de impuesto corporativo", "spanishcifid#", "spanishcifid", "spanishcifno#", "spanishcifno", "tax file no", "tax file number", "tax id", "tax identification no", "tax identification number", "tax no#", "tax no", "tax number", "tax registration number", "taxid#", "taxidno#", "taxidnumber#", "taxno#", "taxnumber#", "taxnumber", "tin id", "tin no", "tin#"],
                        "formats": [],
                        "similarentitiescount": 0,
                        "functionstosatisfy": []
                    },
                    {
                        "id": "swedendriverslicensenumber",
                        "generickeywords": [],
                        "specifickeywords": ["dl#", "driver license", "driver license number", "driver licence", "drivers lic.", "drivers license", "drivers licence", "driver's license", "driver's license number", "driver's licence number", "driving license number", "dlno#", "körkort"],
                        "formats": ["######-####"],
                        "similarentitiescount": 0,
                        "functionstosatisfy": []    
                    },
                    {
                        "id": "swedennationalid",
                        "generickeywords": [],
                        "specifickeywords": ["sweden national id"],
                        "formats": [],
                        "similarentitiescount": 0,
                        "functionstosatisfy": []    
                    },
                    {
                        "id": "swedenpassportnumber",
                        "generickeywords": [],
                        "specifickeywords": ["visa requirements", "Alien Registration Card", "Schengen visas", "Schengen visa", "Visa Processing", "Visa Type", "Single Entry", "Multiple Entry", "G3 Processing Fees", "Passport Number", "Passport No", "Passport #", "Passport#", "PassportID", "Passportno", "passportnumber", "パスポート", "パスポート番号", "パスポートのNum", "パスポート＃", "Numéro de passeport", "Passeport n °", "Passeport Non", "Passeport #", "Passeport#", "PasseportNon", "Passeportn °"],
                        "formats": ["########"],
                        "similarentitiescount": 0,
                        "functionstosatisfy": []    
                    },
                    {
                        "id": "swedenssn",
                        "generickeywords": [],
                        "specifickeywords": ["personal id number", "identification number", "personal id no", "identity no", "identification no", "personal identification no", "personnummer id", "personligt id-nummer", "unikt id-nummer", "personnummer", "identifikationsnumret", "personnummer#", "identifikationsnumret#"],
                        "formats": [],
                        "similarentitiescount": 0,
                        "functionstosatisfy": []    
                    },
                    {
                        "id": "swedentaxidnumber",
                        "generickeywords": [],
                        "specifickeywords": ["personal id number", "personnummer", "skatt id nummer", "skatt identifikation", "skattebetalarens identifikationsnummer", "sverige tin", "tax file", "tax id", "tax identification no", "tax identification number", "tax no#", "tax no", "tax number", "tax registration number", "taxid#", "taxidno#", "taxidnumber#", "taxno#", "taxnumber#", "taxnumber", "tin id", "tin no", "tin#"],
                        "formats": [],
                        "similarentitiescount": 0,
                        "functionstosatisfy": []    
                    },
                    {
                        "id": "taiwannationalidnumber",
                        "generickeywords": [],
                        "specifickeywords": ["身份證字號", "身份證", "身份證號碼", "身份證號", "身分證字號", "身分證", "身分證號碼", "身份證號", "身分證統一編號", "國民身分證統一編號", "簽名", "蓋章", "簽名或蓋章", "簽章"],
                        "formats": ["?1#######^","?2#######^"],
                        "similarentitiescount": 0,
                        "functionstosatisfy": []    
                    },
                    {
                        "id": "taiwanpassportnumber",
                        "generickeywords": [],
                        "specifickeywords": ["ROC passport number", "Passport number", "Passport no", "Passport Num", "Passport #", "护照", "中華民國護照", "Zhōnghuá Mínguó hùzhào"],
                        "formats": ["3########","#########"],
                        "similarentitiescount": 0,
                        "functionstosatisfy": []    
                    },
                    {
                        "id": "taiwanresidentcertificationnumber",
                        "generickeywords": [],
                        "specifickeywords": ["Resident Certificate", "Resident Cert", "Resident Cert.", "Identification card", "Alien Resident Certificate", "ARC", "Taiwan Area Resident Certificate", "TARC", "居留證", "外僑居留證", " 台灣地區居留證"],
                        "formats": ["??########"],
                        "similarentitiescount": 0,
                        "functionstosatisfy": []    
                    },
                    {
                        "id": "thaipopulationidcode",
                        "generickeywords": [],
                        "specifickeywords": ["ID Number", "Identification Number", "บัตรประชาชน", "รหัสบัตรประชาชน", "บัตรประชาชน", "รหัสบัตรประชาชน"],
                        "formats": [],
                        "similarentitiescount": 0,
                        "functionstosatisfy": []    
                    },
                    {
                        "id": "turkishnationalidnumver",
                        "generickeywords": [],
                        "specifickeywords": ["TC Kimlik No", "TC Kimlik numarası", "Vatandaşlık numarası", "Vatandaşlık no"],
                        "formats": ["###########"],
                        "similarentitiescount": 0,
                        "functionstosatisfy": []    
                    },
                    {
                        "id": "ukdriverslicensenumber",
                        "generickeywords": [],
                        "specifickeywords": ["DVLA", "light vans", "quadbikes", "motor cars", "125cc", "sidecar", "tricycles", "motorcycles", "photocard licence", "learner drivers", "licence holder", "licence holders", "driving licences", "driving licence", "dual control car"],
                        "formats": [],
                        "similarentitiescount": 0,
                        "functionstosatisfy": []    
                    },
                    {
                        "id": "ukelectoralrollnumber",
                        "generickeywords": [],
                        "specifickeywords": ["council nomination", "nomination form", "electoral register", "electoral roll"],
                        "formats": [],
                        "similarentitiescount": 0,
                        "functionstosatisfy": []    
                    },
                    {
                        "id": "uknationalhealthservicenumber",
                        "generickeywords": [],
                        "specifickeywords": ["national health service", "nhs", "health services authority", "health authority", "patient id", "patient identification", "patient no", "patient number", "GP", "DOB", "D.O.B", "Date of Birth", "Birth Date"],
                        "formats": [],
                        "similarentitiescount": 0,
                        "functionstosatisfy": []    
                    },
                    {
                        "id": "uknationalinsurancenumber",
                        "generickeywords": [],
                        "specifickeywords": ["national insurance number", "national insurance contributions", "protection act", "insurance", "social security number", "insurance application", "medical application", "social insurance", "medical attention", "social security", "great britain", "insurance"],
                        "formats": [],
                        "similarentitiescount": 0,
                        "functionstosatisfy": []    
                    },
                    {
                        "id": "uktaxidnumber",
                        "generickeywords": [],
                        "specifickeywords": ["tax number", "tax file", "tax id", "tax identification no", "tax identification number", "tax no#", "tax no", "tax registration number", "taxid#", "taxidno#", "taxidnumber#", "taxno#", "taxnumber#", "taxnumber", "tin id", "tin no", "tin#"],
                        "formats": ["#########^"],
                        "similarentitiescount": 0,
                        "functionstosatisfy": []    
                    },
                    {
                        "id": "usbankaccnumber",
                        "generickeywords": [],
                        "specifickeywords": ["Checking Account Number", "Checking Account", "Checking Account #", "Checking Acct Number", "Checking Acct #", "Checking Acct No.", "Checking Account No.", "Bank Account Number", "Bank Account #", "Bank Acct Number", "Bank Acct #", "Bank Acct No.", "Bank Account No.", "Savings Account Number", "Savings Account.", "Savings Account #", "Savings Acct Number", "Savings Acct #", "Savings Acct No.", "Savings Account No.", "Debit Account Number", "Debit Account", "Debit Account #", "Debit Acct Number", "Debit Acct #", "Debit Acct No.", "Debit Account No."],
                        "formats": [],
                        "similarentitiescount": 0,
                        "functionstosatisfy": []    
                    },
                    {
                        "id": "usdriverslicensenumber",
                        "generickeywords": [],
                        "specifickeywords": ["DL", "DLS", "CDL", "CDLS", "ID", "IDs", "DL#", "DLS#", "CDL#", "CDLS#", "ID#", "IDs#", "ID number", "ID numbers", "LIC", "LIC#", "DriverLic", "DriverLics", "DriverLicense", "DriverLicenses", "Driver Lic", "Driver Lics", "Driver License", "Driver Licenses", "DriversLic", "DriversLics", "DriversLicense", "DriversLicenses", "Drivers Lic", "Drivers Lics", "Drivers License", "Drivers Licenses", "Driver'Lic", "Driver'Lics", "Driver'License", "Driver'Licenses", "Driver' Lic", "Driver' Lics", "Driver' License", "Driver' Licenses", "Driver'sLic", "Driver'sLics", "Driver'sLicense", "Driver'sLicenses", "Driver's Lic", "Driver's Lics", "Driver's License", "Driver's Licenses", "identification number", "identification numbers", "identification #", "id card", "id cards", "identification card", "identification cards", "DriverLic#", "DriverLics#", "DriverLicense#", "DriverLicenses#", "Driver Lic#", "Driver Lics#", "Driver License#", "Driver Licenses#", "DriversLic#", "DriversLics#", "DriversLicense#", "DriversLicenses#", "Drivers Lic#", "Drivers Lics#", "Drivers License#", "Drivers Licenses#", "Driver'Lic#", "Driver'Lics#", "Driver'License#", "Driver'Licenses#", "Driver' Lic#", "Driver' Lics#", "Driver' License#", "Driver' Licenses#", "Driver'sLic#", "Driver'sLics#", "Driver'sLicense#", "Driver'sLicenses#", "Driver's Lic#", "Driver's Lics#", "Driver's License#", "Driver's Licenses#", "id card#", "id cards#", "identification card#", "identification cards#", "State abbreviation (for example, 'NY')", "State name (for example, 'New York')"],
                        "formats": ["### ### ###"],
                        "similarentitiescount": 0,
                        "functionstosatisfy": []    
                    },
                    {
                        "id": "usindividualtaxidnumber",
                        "generickeywords": [],
                        "specifickeywords": ["taxpayer", "tax id", "tax identification", "itin", "ssn", "tin", "social security", "tax payer", "itins", "taxid", "individual taxpayer", "License", "DL", "DOB", "Birthdate", "Birthday", "Date of Birth"],
                        "formats": ["9## 7# ####","9## 8# ####","9##-7#-####","9##-8#-####"],
                        "similarentitiescount": 0,
                        "functionstosatisfy": []    
                    },
                    {
                        "id": "usssn",
                        "generickeywords": [],
                        "specifickeywords": ["Social Security", "Social Security#", "Soc Sec", "SSN", "SSNS", "SSN#", "SS#", "SSID"],
                        "formats": ["###-##-####","### ## ####","#########"],
                        "similarentitiescount": 0,
                        "functionstosatisfy": []    
                    },
                    {
                        "id": "usukpassportnumber",
                        "generickeywords": [],
                        "specifickeywords": ["Passport Number", "Passport No", "Passport #", "Passport#", "PassportID", "Passportno", "passportnumber", "パスポート", "パスポート番号", "パスポートのNum", "パスポート＃", "Numéro de passeport", "Passeport n °", "Passeport Non", "Passeport #", "Passeport#", "PasseportNon", "Passeportn °"],
                        "formats": ["#########"],
                        "similarentitiescount": 0,
                        "functionstosatisfy": []    
                    },
                    {
                        "id": "mpaaaorgid",
                        "generickeywords": [],
                        "specifickeywords": ["MPA Org Id", "MPAA #", "MPAA"],
                        "formats": ["###-##-####","### ## ####","#########"],
                        "similarentitiescount": 0,
                        "functionstosatisfy": []    
                    },
                    {
                        "id": "vendorid",
                        "generickeywords": [],
                        "specifickeywords": ["vendor #", "Vendor Number", "Vendor Id", "V Id"],
                        "formats": ["########", "#######?"],
                        "similarentitiescount": 0,
                        "functionstosatisfy": []    
                    },
                    {
                        "id": "customerid",
                        "generickeywords": [],
                        "specifickeywords": ["customer id", "Customer Number", "Customer Id #", "Cust Id", "Custo. No." , "CRN"],
                        "formats": ["9## 7# ####","9## 8# ####","9##-7#-####","9##-8#-####"],
                        "similarentitiescount": 0,
                        "functionstosatisfy": []    
                    },
                    {
                        "id": "companycode",
                        "generickeywords": [],
                        "specifickeywords": ["code comp.", "Company Code", "Co. code", "Code"],
                        "formats": ["###-###"],
                        "similarentitiescount": 0,
                        "functionstosatisfy": []    
                    }
                ]"""
    return json.loads(entities)

# generate_entites("abaroutingnumber",KeywordsType.Specific, 10)
# generate_entites("australiapassportnumber",KeywordsType.Specific, 10)
# generate_entites("australiamedicalaccnumber",KeywordsType.Specific, 10)
# generate_entites("abaroutingnumber",KeywordsType.Specific, 10)
# generate_entites("belgiumnationalnumber",KeywordsType.Specific, 10)
# generate_entites("brazillegalentitynumber",KeywordsType.Specific, 10)
# generate_entites("chinaresidentidcardnumber",KeywordsType.Specific, 10)
# generate_entites("denmarktaxidnumber",KeywordsType.Specific, 10)
# generate_entites("estonianationalidnumber",KeywordsType.Specific, 10)
# generate_entites("japanassn",KeywordsType.Specific, 10)
# generate_entites("luxemburgpassportnumber",KeywordsType.Specific, 10)
# generate_entites("usbankaccnumber",KeywordsType.Specific, 10)
# generate_entites("luxemburgpassportnumber",KeywordsType.Specific, 10)
# generate_entites("luxemburgpassportnumber",KeywordsType.Specific, 10)
        

