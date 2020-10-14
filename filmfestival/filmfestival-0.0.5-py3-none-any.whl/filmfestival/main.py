from flask import Flask
import requests
from google.cloud import firestore

app = Flask(__name__)

appkey = "9ea40129"

client_firestore = firestore.Client()


@app.route('/search/<film>', methods=['GET'])
def search(film):
    return search_film(film)


@app.route('/delete/<title>', methods=['DELETE'])
def delete(title):
    return delete_content(title)


@app.route('/query/<title>', methods=['GET'])
def query(title):
    return query_firestore_len(title)


def search_film(title):
    title = format_title(title)
    r = requests.get(compose_url(title))
    response = r.json()
    save_film(response)
    return response


def compose_url(title):
    url = "http://www.omdbapi.com/?apikey="+appkey+"&t="+title
    return url


def format_title(title):
    title = title.strip()
    title = title.lower()
    title = title.replace(" ", "+")
    return title


def save_film(film):
    film_dict = {
        "Title": film["Title"],
        "Duration": film["Runtime"],
        "Year": film["Year"],
        "Genre": film["Genre"],
        "Description": film["Plot"],
        "Language": film["Language"],
        "Country": film["Country"],
        "Director": film["Director"],
        "Awards": film["Awards"]
    }

    query = client_firestore.collection("FILM").where("Title", "==", film_dict["Title"])
    query = query.where("Year", "==", film_dict["Year"])
    results = list(query.stream())
    if not results:
        client_firestore.collection("FILM").document().set(film_dict)
    else:
        print("Il film era già presente nel database")
        return False

    return True


def query_firestore(title, year):
    query = client_firestore.collection("FILM").where("Title", "==", title)
    query = query.where("Year", "==", year)
    results = list(query.stream())
    film = ""
    film_risultato = ""
    if results:
        film = results[0]
        film_risultato = film.to_dict()
    else:
        print("Non ci sono film")

    return film_risultato["Director"]


def query_firestore_len(title):
    query = client_firestore.collection("FILM").where("Title", "==", title)
    results = list(query.stream())
    film = ""
    film_risultato = ""
    if results:
        film = results[0]
        film_risultato = film.to_dict()
    else:
        print("Non ci sono film")

    return film_risultato["Language"]


def delete_content(title):
    query = client_firestore.collection("FILM").where("Title", "==", title)
    results = list(query.stream())
    film = ""
    film_id = ""
    if results:
        film = results[0]
        film_id = film.id
        client_firestore.collection("FILM").document(film_id).delete()
        return True
    return False


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=False)
