import requests


def buscar_avatar(usuario):
    """
    Busca o avatar de um usuario no github
    :param usuario: str com o nome do usuario no github
    :return: str com o link do avatar e repositorio do usuario
    """

    url = f'https://api.github.com/users/{usuario}'
    resp = requests.get(url)
    resp2 = requests.get(url)
    return resp.json()['avatar_url'], resp2.json()['html_url']


if __name__ == '__main__':
    print(buscar_avatar(input('Digite um usuario github para exibir seu avatar: ')))
