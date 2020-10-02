'''The MIT License (MIT)

Copyright (c) 2020 Raj Sharma

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.'''
from .exceptions import *
from ._http import http

class aiodagpiclient:
    """The main aiodagpi client

    Args:
        token (str): Your dagpi.tk authorization token
    """
    def __init__(self, token:str):
        self.token = token
        self.base_url = "https://dagpi.tk/api/"
        self.base_headers = {
            "token": self.token
        }
        self.http = http()

    async def closesession(self):
        """Closes the aiohttp client session
        """
        self.http.closesession()

    async def get(self, option:str):
        """Perform a GET request for one of the specified options

        Args:
            option (str): The option, possibles: 'wtp', 'logogame'

        Raises:
            InvalidOption: Invalid option provided

        Returns:
            str: The dictionary response to the GET request
        """
        options = [
            'wtp',
            'logogame'
        ]
        if option not in options:
            raise InvalidOption()
        resp = await self.http.get(url=f'{self.base_url}{option}', headers=self.base_headers)
        if type(resp) == bytes:
            resp = resp.decode()
        return resp

    async def simple(self, option:str, image:str):
        options = [
            'sobel',
            'hitler',
            'triggered',
            'angel',
            'obama',
            'satan',
            'ascii',
            'colors',
            'bad',
            'rgbdata',
            'evil',
            'trash',
            'wanted',
            'hog'
        ]
        if option not in options:
            raise InvalidOption()
        headers = self.base_headers
        headers['url'] = image
        resp = await self.http.post(url=f'{self.base_url}{option}', headers=headers)
        if type(resp) == bytes:
            resp = resp.decode()
        return resp
