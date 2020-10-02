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

import aiohttp
from aiodagpi.exceptions import *

class http:
    def __init__(self):
        self.codes = {
            401:InvalidToken,
            404:PageNotfound,
            405:MethodNotAllowed
        }
        self.session = None

    async def makesession(self):
        """Creates client aiohttp session if one does not already exist
        """
        if not self.session:
            self.session = aiohttp.ClientSession()

    async def closesession(self):
        """Closes client aiohttp session if one already exists
        """
        if self.session:
            await self.session.close()
            self.session = None

    async def get(self, url, headers=None):
        """Performs a GET request with a URL and optional headers

        Args:
            url (str): The URL to perform the specified GET 
            headers (dict, optional): The headers to use in the GET request. Defaults to None.

        Raises:
            exception: Any pre-caught exceptions
            UnCaughtError: Any un-caught exceptions

        Returns:
            dict: A JSON dictionary of the GET response
        """
        await self.makesession()
        async with self.session.get(url=url, headers=headers) as cs:
            if cs.status == 200:
                try:
                    return await cs.json()
                except aiohttp.ContentTypeError:
                    return await cs.text()
            await self.closesession()
            if cs.status in self.codes:
                exception = self.codes[cs.status]
                raise exception()
            else:
                raise UnCaughtError(code=cs.status, error=cs.reason)

    async def post(self, url, headers=None):
        """Performs a POST request with a URL and optional headers

        Args:
            url (str): The URL to perform the specified POST
            headers (dict, optional): The headers to use in the POST request. Defaults to None.

        Raises:
            exception: Any pre-caught exceptions
            UnCaughtError: Any un-caught exceptions

        Returns:
            dict: A JSON dictionary of the POST response
        """
        await self.makesession()
        async with self.session.post(url=url, headers=headers) as cs:
            if cs.status == 200:
                try:
                    return await cs.json()
                except aiohttp.ContentTypeError:
                    return await cs.text()
            await self.closesession()
            if cs.status in self.codes:
                exception = self.codes[cs.status]
                raise exception()
            else:
                raise UnCaughtError(code=cs.status, error=cs.reason)
