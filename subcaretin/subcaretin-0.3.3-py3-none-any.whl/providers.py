import requests
import json
from bs4 import BeautifulSoup as bso

api_search = "http://argenteam.net/api/v1/search"
api_episode = "http://argenteam.net/api/v1/episode"
api_movie = "http://argenteam.net/api/v1/movie"
subdivx_base = "http://www.subdivx.com/index.php?q="
subdivx_query = "&accion=5&masdesc=&subtitulos=1&realiza_b=1"


class Subtitles:
    def __init__(self, query):
        self.query = query
        self.Items = []
        self.Subs = {"items": self.Items}

    def appendSubs(self, title, desc, url, provider):
        self.Items.append(
            {"title": title, "description": desc, "url": url, "provider": provider}
        )

    def get_subdivx(self):
        subdivx = "{}{}{}".format(subdivx_base, self.query, subdivx_query)
        page = requests.get(subdivx)
        soup = bso(page.content, "html.parser")
        title = soup.find_all(id="menu_titulo_buscador")
        desc = soup.find_all(id="buscador_detalle_sub")
        url = soup.find_all("a", class_="titulo_menu_izq")

        for t, d, u in zip(title, desc, url):
            self.appendSubs(
                t.text.replace("Subtitulos de ", ""),
                d.text,
                u.get("href"),
                "subdivx.com",
            )
        if not title:
            print("Sin resultados en Subdivx")

    def get_argenteam(self):
        argenteam_search = "%s?q=%s" % (api_search, self.query)
        page = requests.get(argenteam_search)
        soup = bso(page.content, "html.parser")
        arg_json = json.loads(soup.text)

        def get_arg_links(moviePag):
            moviePag = requests.get("%s?id=%s" % (api_movie, arg_id))
            movieSop = bso(moviePag.content, "html.parser")
            movieJson = json.loads(movieSop.text)
            movieTitle = movieJson["title"]
            try:
                for rele in movieJson["releases"]:
                    if rele["subtitles"]:
                        for uri in rele["subtitles"]:
                            self.appendSubs(
                                movieTitle,
                                uri["uri"].rsplit("/", 1)[-1],
                                uri["uri"],
                                "argenteam.net",
                            )
            except KeyError:
                pass

        for tipo in arg_json["results"]:
            mov_o_tv = tipo["type"]
            arg_id = tipo["id"]
            try:
                if mov_o_tv == "movie":
                    moviePag = requests.get("{}?id={}".format(api_movie, arg_id))
                    get_arg_links(moviePag)
                else:
                    moviePag = requests.get("{}?id={}".format(api_episode, arg_id))
                    get_arg_links(moviePag)
            except AttributeError:
                print("Sin resultados en Argenteam")

    def get_subtitles(self, argenteam, subdivx, limit):
        if argenteam and not subdivx:
            self.get_argenteam()
        elif subdivx and not argenteam:
            self.get_subdivx()
        else:
            self.get_argenteam()
            self.get_subdivx()
        del self.Items[limit:]
