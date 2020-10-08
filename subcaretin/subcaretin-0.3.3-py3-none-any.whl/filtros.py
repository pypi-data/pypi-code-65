from operator import itemgetter

# SubFiltro devuelve cinco listas. Todas son filtradas para evitar que
# subcaretin descargue archivos no deseados o perjudiciales en el modo
# automático. Al pasar por el primer filtro procede a calcular el puntaje.

# Aunque todaviía hayan varias palabras clave por agregar a ambos filtros,
# los resultados son efectivos.


filtroList = [
    "dvds",
    "pack",
    "Pack",
    "PACK",
    "DVDS",
    "DVDs",
    "partes",
    "PARTES",
    "Partes",
    "cds",
    "archivos",
    "ARCHIVOS",
    "Archivos",
    "tres partes",
    "3 partes",
    "2 partes",
    "dos partes",
    "CD",
    "3 dvd",
    "2 dvd",
    "discos",
    "se pueden mejorar",
    "faltan mejora",
    "incomplet",
    "mula ",
    "falta mejora",
    "dvd1",
    "dvd2",
    "cd1",
    "cd2",
    "CD2",
    "CD3",
    "CD1",
    "DVD1",
    "DVD2",
    "Spa2",
    "spa2",
    "spa1",
    "Spa1",
    "SPA1",
    "SPA2",
    "Esp2",
    "Esp1",
    "esp2",
    "temporada completa",
    "TEMPORADA COMPLETA",
    "esp1",
    "2 Cds",
    "2cds",
    "2CDs",
    "2CDS",
    " Cds ",
    "Temporada completa",
    "part1",
    "part2",
    "CDS",
    "Parte 4",
    "Parte 3",
    "Parte 2",
]


class Filtro:
    def __init__(self, movies, attrs):
        self.movies = movies
        self.attrs = attrs

        # Las descripciones de Subdivx vienen en minúsuclas por defecto, pero
        # las de Argenteam no
        for each in self.movies:
            each["description"] = each["description"].lower()
            if any(x in each["description"] for x in filtroList):
                self.movies.remove(each)

        for cada in range(len(self.movies)):
            scoreSource = 0
            scoreCodec = 0
            scoreAudio = 0
            scoreResolution = 0
            score = 0

            if any(y in self.movies[cada]["description"] for y in self.attrs["source"]):
                scoreSource = 7
            if any(y in self.movies[cada]["description"] for y in self.attrs["codec"]):
                scoreCodec = 3
            if any(y in self.movies[cada]["description"] for y in self.attrs["audio"]):
                scoreAudio = 3
            if any(y in self.movies[cada]["description"] for y in attrs["resol"]):
                scoreResolution = 2
            if any(y in self.movies[cada]["title"] for y in attrs["year"]):
                scoreResolution = 2

            score = scoreSource + scoreCodec + scoreAudio + scoreResolution
            self.movies[cada]["score"] = score

        self.movies = sorted(self.movies, key=itemgetter("score"), reverse=True)
