from typing import Optional

from django.contrib.sites.shortcuts import get_current_site
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse
from django.views import View

from defusedxml import minidom
from dicttoxml import dicttoxml

from ..api.bigbluebutton import BigBlueButton as _BigBlueButton
from .models import APIToken


class APIView(View):
    # Use a matching HTTP status for each error case
    # The BBB reference implementation always returns 200, we deliberately violate that
    # Set to False to mimic the reference implementation more closely
    _fix_status = True

    def dispatch(self, request: HttpRequest, method: str) -> HttpResponse:
        # Find API tokens to allow for this request
        site = get_current_site(request)
        api_tokens = APIToken.objects.filter(server_group__site=site)

        api_token = self._find_token(request, method, api_tokens)
        if not api_token:
            # We did not find a token who's salt verifies the request (or none at all)
            return self._error(498, "checksumError", "You did not pass the checksum security check")

        # Verify we got a valid HTTP method
        if request.method not in ("GET", "POST"):
            return self._error(
                405,
                "xInfraBlueMethodNotAllowed",
                "The HTTP method {request.method} ist now allowed",
            )

        # Determine token scope and build metadata filter
        if api_token.scope == "global":
            filter_meta = {}
        elif api_token.scope == "user":
            filter_meta = {"infrablue-user": api_token.user.bbb_user_id}
        elif api_token.scope == "token":
            filter_meta = {"infrablue-token": api_token.guid}
        else:
            raise TypeError("API token has unexpected scope")

        # Proprietary extension for test purposes
        if method == "ping":
            return self._success(
                "xInfraBluePong", "The API is working correctly and your request was valid."
            )

        # Create mutable copy of request args without checksum
        attrs = request.GET.copy()
        del attrs["checksum"]

        try:
            # Hand off handling to python-bigbluebutton2
            res = api_token.server_group.api_group.handle_from_data(
                method, attrs, request.body, filter_meta
            )
            return self._success("", res)
        except TypeError:
            return self._error(
                404, "xInfraBlueUnknownAPICall", "The API call {method} is not known"
            )

    def _xml_response(
        self,
        status: int,
        return_code: str,
        message_key: str,
        message: str,
        attrs: Optional[dict] = None,
    ) -> HttpResponse:
        # Inject mandatory attributes
        res = attrs.copy() if attrs else {}
        res.update(dict(reurncode=return_code, messageKey=message_key, message=message))

        # Generate XML and prettify
        xml = dicttoxml(res, attr_type=False, custom_root="response")
        xml = minidom.parseString(xml).toprettyxml()

        return HttpResponse(xml, status=status, content_type="text/xml")

    def _error(self, status: int, message_key: str, message: str) -> HttpResponse:
        return self._xml_response(status, "FAILED", message_key, message)

    def _success(
        self, message_key: str, message: str, attrs: Optional[dict] = None
    ) -> HttpResponse:
        return self._xml_response(200, "SUCCESS", message_key, message, attrs)

    def _find_token(
        self, request: HttpRequest, method: str, api_tokens: QuerySet
    ) -> Optional[APIToken]:
        for api_token in api_tokens:
            # Try authenticating the request with each token candiate
            ret = self._auth_request(request, method, api_token)
            if ret:
                # We found a valid token
                return api_token
        return None

    def _auth_request(self, request: HttpRequest, method: str, api_token: APIToken) -> bool:
        # Extract signed part of query string
        query = request.META["QUERY_STRING"]
        if query.startswith("checksum="):
            query = ""
        elif "&checksum=" in query:
            query = query[: query.index("&checksum=")]
        else:
            # Request is unauthenticated if no checksum present
            return False

        # Calculate checksum and compare
        checksum = _BigBlueButton.request_checksum(method, query, api_token.salt)
        return checksum == request.GET.get("checksum", "")
