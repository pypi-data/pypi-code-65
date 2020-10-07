from pytryfi.const import *
import requests

def getUserDetail(sessionId):
    qString = QUERY_CURRENT_USER + FRAGMENT_USER_DETAILS
    response = query(sessionId, qString)
    return response['data']['currentUser']

def getPetList(sessionId):
    qString = QUERY_CURRENT_USER_FULL_DETAIL + FRAGMENT_USER_DETAILS \
        + FRAGMENT_USER_FULL_DETAILS + FRAGMENT_PET_PROFILE + FRAGEMENT_BASE_PET_PROFILE \
        + FRAGMENT_BASE_DETAILS + FRAGMENT_POSITION_COORDINATES + FRAGMENT_BREED_DETAILS \
        + FRAGMENT_PHOTO_DETAILS + FRAGMENT_DEVICE_DETAILS + FRAGMENT_LED_DETAILS + FRAGMENT_OPERATIONAL_DETAILS \
        + FRAGMENT_CONNECTION_STATE_DETAILS
    response = query(sessionId, qString)
    return response['data']['currentUser']['userHouseholds'][0]['household']['pets']

def getBaseList(sessionId):
    qString = QUERY_CURRENT_USER_FULL_DETAIL + FRAGMENT_USER_DETAILS \
        + FRAGMENT_USER_FULL_DETAILS + FRAGMENT_PET_PROFILE + FRAGEMENT_BASE_PET_PROFILE \
        + FRAGMENT_BASE_DETAILS + FRAGMENT_POSITION_COORDINATES + FRAGMENT_BREED_DETAILS \
        + FRAGMENT_PHOTO_DETAILS + FRAGMENT_DEVICE_DETAILS + FRAGMENT_LED_DETAILS + FRAGMENT_OPERATIONAL_DETAILS \
        + FRAGMENT_CONNECTION_STATE_DETAILS
    response = query(sessionId, qString)
    return response['data']['currentUser']['userHouseholds'][0]['household']['bases']

def getCurrentPetLocation(sessionId, petId):
    qString = QUERY_PET_CURRENT_LOCATION.replace(VAR_PET_ID, petId) + FRAGMENT_ONGOING_ACTIVITY_DETAILS \
        + FRAGMENT_UNCERTAINTY_DETAILS + FRAGMENT_CIRCLE_DETAILS + FRAGMENT_LOCATION_POINT \
        + FRAGMENT_PLACE_DETAILS + FRAGMENT_USER_DETAILS + FRAGMENT_POSITION_COORDINATES
    response = query(sessionId, qString)
    return response['data']['pet']['ongoingActivity']

def getCurrentPetStats(sessionId, petId):
    qString = QUERY_PET_ACTIVITY.replace(VAR_PET_ID, petId) + FRAGMENT_ACTIVITY_SUMMARY_DETAILS
    response = query(sessionId, qString)
    return response['data']['pet']

def getGraphqlURL():
    return API_HOST_URL_BASE + API_GRAPHQL

def query(sessionId, qString):
    jsonObject = None
    url = getGraphqlURL()
    params={'query': qString}
    jsonObject = execute(url, sessionId, params=params).json()
    return jsonObject

def execute(url, sessionId, method='GET', params=None, cookies=None):
    response = None
    if method == 'GET':
        response = sessionId.get(url, params=params)
    elif method == 'POST':
        response = sessionId.post(url, data=params)
    else:
        ##LOG.error("Invalid request method '%s'", method)
        return None
    return response
    