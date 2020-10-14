import requests
import webbrowser
import os
import json
from os import path
from uuid import uuid4
from webbrowser import open_new
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.request import urlopen, HTTPError
from urllib.parse import urlparse, parse_qs
from requests.auth import HTTPBasicAuth
from flask import jsonify

class S(BaseHTTPRequestHandler):
    def _set_response(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        self._set_response()
        self.wfile.write("All done. You can close the window now.".encode())
        try:
            code = urlparse(self.path).query.split("=")[1]
        except Exception as e:
            print('Resolving Issue')
        print(code)
        if code:
            try:
                data = {
                    'grant_type':'authorization_code',
                    'code':code
                    }
                print('HERE')
                print("Client_ID")
                
                with open('/opt/alectio/client_info.json') as f:
                    client_info = json.load(f)
                print(client_info['client_id'])
                response = requests.post('https://auth.alectio.com/oauth/token', 
                                        auth=HTTPBasicAuth(client_info['client_id'], client_info['client_secret']), data=data)
                print(response.json())
                with open('/opt/alectio/client_token.json', 'w') as fp:
                    json.dump(response.json(), fp)
                print('Your Auth token has been save into /opt/alectio/client_token.json')
                print('Your Token is: \n' + str(response.json()['access_token']))

            except:
                print("SDK Setp Failed")

            raise KeyboardInterrupt


    def do_POST(self):
        content_length = int(self.headers['Content-Length']) # <--- Gets the size of data
        post_data = self.rfile.read(content_length) # <--- Gets the data itself
        self._set_response()
        self.wfile.write("POST request for {}".format(self.path).encode('utf-8'))



def run(ACCESS_URI, server_class=HTTPServer, handler_class=S, port=5001):
    open_new(ACCESS_URI)
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()


def main():
    client_info = None
    if path.exists("/opt/alectio/client_info.json"):
        with open('/opt/alectio/client_info.json') as json_file: 
            client_info = json.load(json_file) 
    else:
        print('Please Open: https://auth.alectio.com and get you Clinet ID and Clinet Secret.')
        client_id = input('Please enter Client ID: ')
        client_secret = input('Please enter Client Secret: ')

        client_info = {
            'client_id': client_id,
            'client_secret':client_secret
        }

        if not os.path.exists('/opt/alectio'):
            os.makedirs('/opt/alectio')

        with open('/opt/alectio/client_info.json', 'w', encoding='utf-8') as f:
            json.dump(client_info, f, ensure_ascii=False, indent=2)

        os.environ['sdk_client_id'] = client_id
        os.environ['client_secret'] = client_secret
    print('You Client info has been save at: /opt/alectio/client_info.json with: \n' + str(client_info))
    print('Fetching you Auth Token, please follow instruction on your screen')
    ACCESS_URI = ('https://auth.alectio.com/' 
            + 'oauth/authorize?client_id=' + client_info['client_id'] + '&scope=openid+profile&response_type=code&nonce=abc')
    run(ACCESS_URI)



if __name__ == '__main__':
    main()
    



