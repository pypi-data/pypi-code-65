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
SOFTWARE.
'''
class AiodagpiException(Exception):
    pass

class InvalidToken(AiodagpiException):
    """Raised when token is invalid
    """
    def __init__(self, error='Improper or invalid token passed.'):
        self.error = error
    def __str__(self):
        return self.error

class InvalidOption(AiodagpiException):
    """Raised when option is invalid
    """
    def __init__(self, error='Invalid option provided.'):
        self.error = error
    def __str__(self):
        return self.error

class InvalidURLProvided(AiodagpiException):
    """Raised when URL provided is invalid
    """
    def __init__(self, error='Improperly built or invalid URL passed.'):
        self.error = error
    def __str__(self):
        return self.error

class PageNotfound(AiodagpiException):
    """Raised when requested URL is not found
    """
    def __init__(self, error='Endpoint could not be found, try again later.'):
        self.error = error
    def __str__(self):
        return self.error

class MethodNotAllowed(AiodagpiException):
    """Raised when wrong method is used
    """
    def __init__(self, error='This method (GET / POST) is not permitted here. Try swapping.'):
        self.error = error
    def __str__(self):
        return self.error

class UnCaughtError(AiodagpiException):
    """Raised when an error not specifically excepted is raised
    """
    def __init__(self, error, code):
        self.error = f'Received code {code} : {error}'
    def __str__(self):
        return self.error
