import requests


def buscar_avatar(usuario):
    """Busca o avatar do usuário no Github

    :param usuario:str com o nome de usuário no Github
    :return: str com o link do avatar
    """
    url = f'https://api.github.com/users/{usuario}'
    requests
    resp = requests.get(url)
    return resp.json()['avatar_url']


if __name__ == '__main__':
    print(buscar_avatar('renzo'))
