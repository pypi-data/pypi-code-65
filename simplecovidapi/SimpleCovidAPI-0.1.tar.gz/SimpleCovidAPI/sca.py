import requests
from json import loads

def req():
    return loads(requests.get('https://simplecovidapi.herokuapp.com/').text)

def deaths():
    return req()['deaths']

def cases():
    return req()['cases']
    
def recoveries():
    return req()['recoveries']
