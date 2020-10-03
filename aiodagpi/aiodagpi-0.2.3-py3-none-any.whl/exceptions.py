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
    def __init__(self, error='Improper or invalid token passed to client instance.'):
        self.error = error
    def __str__(self):
        return self.error

class InvalidOption(AiodagpiException):
    """Raised when option is invalid
    """
    def __init__(self, error='Invalid option provided. Check the list.'):
        self.error = error
    def __str__(self):
        return self.error
    
class InternalServerError(AiodagpiException):
    """Raised when internal server error is preached
    """
    def __init__(self, error='An internal server error occured. This means we cannot be more specific on the error, check your URL.'):
        self.error = error
    def __str__(self):
        return self.error

class RateLimitation(AiodagpiException):
    """Raised when you are being ratelimited
    """
    def __init__(self, error='Your IP address is being ratelimited, try making less requests or your IP may be permanently blocked.'):
        self.error = error
    def __str__(self):
        return self.error

class ImageTooLarge(AiodagpiException):
    """Raised when your image is too large
    """
    def __init__(self, error='Image provided is too large to be processed, try compressing it.'):
        self.error = error
    def __str__(self):
        return self.error

class NoContent(AiodagpiException):
    """Raised when there is no content to be displayed
    """
    def __init__(self, error='Server decided no content should be displayed, check your URL or check back later.'):
        self.error = error
    def __str__(self):
        return self.error

class ResetContent(AiodagpiException):
    """Raised when dagpi tells you to retry
    """
    def __init__(self, error='Request received reset content command, try retrying. If this persists, contact Daggy.'):
        self.error = error
    def __str__(self):
        return self.error

class URLMoved(AiodagpiException):
    """Raised when the URL has been moved
    """
    def __init__(self, error='Endpoint has been relocated temporarily or permanently. Contact Daggy or I.'):
        self.error = error
    def __str__(self):
        return self.error

class RequestTimeout(AiodagpiException):
    """Raised when your request timed out
    """
    def __init__(self, error='Request timed out or connection broken. Try again and check your image URL.'):
        self.error = error
    def __str__(self):
        return self.error

class URLTooLong(AiodagpiException):
    """Raised when your image URL is too long
    """
    def __init__(self, error='Image URL provided is too long to be processed.'):
        self.error = error
    def __str__(self):
        return self.error

class ImageNotFound(AiodagpiException):
    """Raised when image cannot be found
    """
    def __init__(self, error='Invalid image url provided, no image found at specified link.'):
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
    def __init__(self, error='Endpoint could not be found, try again later. If this persists, contact Daggy or I.'):
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
