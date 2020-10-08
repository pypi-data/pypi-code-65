from subcaretin import guess
from subcaretin import providers
from subcaretin import filtros


def get(file, argenteam=True, subdivx=True, lista=False, array=0):
    # extraer información del archivo
    from_filename = guess.Video(file)
    # desde ahí, filtrar y conseguir keywords para buscar coincidencias
    keywords = from_filename.get_keywords()
    buscar = providers.Subtitles(from_filename.busqueda)
    buscar.get_subtitles(argenteam, subdivx, 30)
    movies = buscar.Subs
    filtrado = filtros.Filtro(movies["items"], keywords)
    if not lista:
        try:
            return filtrado.movies[array]
        except IndexError:
            return
    else:
        if filtrado.movies:
            return filtrado.movies
