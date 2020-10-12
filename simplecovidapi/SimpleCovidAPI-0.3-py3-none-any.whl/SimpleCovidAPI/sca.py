import requests

def req():
    return requests.get('https://simplecovidapi.herokuapp.com/').json()

def deaths():
    return req()['deaths']

def cases():
    return req()['cases']
    
def recoveries():
    return req()['recoveries']
