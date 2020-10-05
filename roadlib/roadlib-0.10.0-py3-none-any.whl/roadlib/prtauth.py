import requests
import uuid
import adal
from urllib.parse import urlparse, parse_qs
from roadtools.roadlib.auth import Authentication

def auth_with_prt_cookie(cookie, authobject):
    ses = requests.session()
    params = {
        'resource': authobject.resource_uri,
        'client_id': authobject.client_id,
        'response_type': 'code',
        'haschrome': '1',
        'redirect_uri': 'urn:ietf:wg:oauth:2.0:oob',
        'client-request-id': str(uuid.uuid4()),
        'x-client-SKU': 'PCL.Desktop',
        'x-client-Ver': '3.19.7.16602',
        'x-client-CPU': 'x64',
        'x-client-OS': 'Microsoft Windows NT 10.0.19569.0',
        'site_id': 501358,
        'sso_nonce': str(uuid.uuid4()),
        'mscrid': str(uuid.uuid4())
    }
    headers = {
        'User-Agent': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 10.0; Win64; x64; Trident/7.0; .NET4.0C; .NET4.0E)',
        'UA-CPU': 'AMD64',

    }
    cookies = {
        'x-ms-RefreshTokenCredential': cookie
    }
    res = ses.get('https://login.microsoftonline.com/Common/oauth2/authorize', params=params, headers=headers, cookies=cookies, allow_redirects=False)
    authobject.proxies = {
      'http': 'http://10.117.8.116:8080',
      'https': 'http://10.117.8.116:8080',
    }
    authobject.verify = False
    if res.status_code == 302 and params['redirect_uri'] in res.headers['Location']:
        ups = urlparse(res.headers['Location'])
        qdata = parse_qs(ups.query)
        print(authobject.authenticate_with_code(qdata['code'][0], params['redirect_uri']))
    print(res.headers)
    # print(res.content)

def test():
    auth = Authentication()
    cookie = 'eyJhbGciOiJIUzI1NiIsICJjdHgiOiJYMkVjcFA5MUVmblcwZlFXSDZNcFQrU3NLOVR4MmVycyJ9.eyJyZWZyZXNoX3Rva2VuIjoiQVFBQkFBQUFBQUFHVl9idjIxb1FRNFJPcWgwXzEtdEE4dWJwTXEtX3FOUWVBTkpONXhlV3FqeWZJeDRkYVBIOTlLZEhqaUN5RkRUYVR4ci1fUGIya2VXQ293dVFuOFJEYUtaQ2RlaFQzUUZ5cDlqYnJKUW5MREN1a1Mwc096WUJRbHNwVkNSWmFHcGw0bV9NcnJQaWNuRUcxdWYta3BYRzZmQVNvcTZKdDRES3VQMmdzaGNkOEdJWEVWTHVNa2IzV2NuLVJSdUt2VFJuaFRIZUg4U1VySTFzY045X21uak16N2I4czdYNmd0dlVrX3VtY0kzbEhnN0wtUnFkZlBmcmVPQkZEVTVYS2JDLWJQdXIzaHJwXzFoZ1IyYzVyN0NmTkFFb3pxZG1iMDNHNXVuMGZmY2lCR3VNdUVhRjhwdlhOd196QVZPNGZLa2JYY3JtYTdwblJKdF9aZG9tVUktM3Jla0l4cFhFQUplaUNlX3JhQXBfdE5CYWk1d0JSWkVlUGx3WW1DTU9ZUjROZFZLMmZwV2dtMGpYR01oN1FfTWt0MGVGVVJ0YjlNOFFGOFBOWGU4YmhHaWMtVFB1RlZMQnNjQTRITUZXVjlpVWhwNjl4dWNxajA1VGpYMEdOUEVIZlJJRmZUaFVlZUN1b1hHZGV0NkdrNzZjRkJjSUpuVEd5eXB6d3VHX1l0ak5sMWVDTDVJdmFudEM5NjZzaW9wdkZweXdVZHBzT1RrLVFqSTRCd0MxTnFWckdiTDhJb0ZsRWI2TFhLcFNyUXFwbW41SHBKLUFDbGZISnFKdkx2Ulk5R1JGSjBhUEtxV1NKZWRBZVNQcGZ3M2IxX05zWUx1SUlUMXFkX1J1SGN6R3pJaTBiVnNJZTBRbllXSEphUHdHUmprV290NGNKUUJRbnRaSjNjcVA2UE1XXzB2R1JtVVNHZHhEcUxDM0ItcWZpV1pXaHZLZ1FzVWROMHJZYjdSV2ppYTNjR1M2Vm9wbEU0Y0pscUVLQWZEdzZBRm1YejZBMmd6VlFHNWdNakc1aDgxbHlvWkcxRkhuRGJrOFI2M21kSURLb2FxTlVaMXB6SWFPeVEtMlhoVkJmcFBSdWZ4cWNZOHpacXBLMkhTc1EwcHpyaGVab2psQ1ZDZlo1dWNBQ0pUOVdMbTdZSGVhbi1CbWxzQjVaM3B5Z1MybUxUYUo2V0doNWszVGZtaWZfOHJzazhjc2RaeDNyUmVuRl9mYThfYlY5UEpmcVQ0Qjlkb002T21iRGNYODVWVTBaZExYRWFva0J5eXVTeHgtQWxEenFpNXhkMGhPWnFYNkhFd3hEaHFBLUxNRXhKN3VpVm1LX1R0UjFjM0JUWXlOazJaa042S0JSMEI3bHRfRUhuMEZQN0pRa0hoS2lIdTJnU1dzd1F1V05ZZjJGdnY5ZkFyUkJZdFVvVW1nWUNYbmdnWW1WaTR4SGpvQnQ1LVhnRng0cDFRV0hkaGwwRXVUclJCQkJkcG1TRnMwSVNrSm5QbnljblBXdFJmOG4zbnZ3SWxEcmlxeHE4dEhaMGhNamdUdk1ZdE5DZTVUVlNydmZpUzA4NVdRTzY0SUlldDFGMkFFMmFnbGY4R2ExN2ljTmNrbkZUYkZLeDZLLTdJNFUzYzl0QjNOQWg4ZnpqR1RPNFprQnNQeU5zVnJoV193N3RpeEtkeGNGU0FBIiwgImlzX3ByaW1hcnkiOiJ0cnVlIiwgImlhdCI6IjE1OTUxODA2NzEifQ.nIgVti-bAUxWpjZ2muycNKAcwc25vl9Xt_hXMUDYa-0'
    print(auth_with_prt_cookie(cookie, auth))

if __name__ == '__main__':
    test()
