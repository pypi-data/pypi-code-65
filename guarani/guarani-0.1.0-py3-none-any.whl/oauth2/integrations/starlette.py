from starlette.requests import Request
from starlette.responses import Response

from guarani.oauth2.models import OAuth2Request, OAuth2Response
from guarani.oauth2.provider import Provider


class StarletteProvider(Provider):
    async def create_request(self, request: Request) -> OAuth2Request:
        return OAuth2Request(
            method=request.method,
            url=str(request.url),
            headers=dict(request.headers),
            body=await request.body(),
            user=request.user,
        )

    async def create_response(self, response: OAuth2Response) -> Response:
        return Response(response.body, response.status, response.headers)
