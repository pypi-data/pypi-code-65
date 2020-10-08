from crawliexpress.exceptions import (
    CrawliexpressException,
    CrawliexpressCaptchaException,
)
from crawliexpress.item import Item
from crawliexpress.feedback_page import FeedbackPage
from crawliexpress.search_page import SearchPage

import requests
import urllib
from http.cookies import SimpleCookie


FEEDBACK_URL = "https://feedback.aliexpress.com/display/productEvaluation.htm"


class Client:

    """
    Exposes methods to fetch various resources.

    :param base_url: allows to change locale (not sure about this one)
    :param cookies:
        must be taken from your browser cookies, to avoid captcha and empty results. I usually login then copy as cURL a request made by my browser on a category or a text search. Make sure to remove the **Cookie:** prefix to keep only cookie values.
    """

    base_url = None
    cookies = None

    def __init__(self, base_url, cookies=None):

        self.base_url = base_url
        if cookies is not None:
            jar = SimpleCookie()
            jar.load(cookies)
            self.cookies = {key: morsel.value for key, morsel in jar.items()}

    def _analyze_response(self, response):
        if response.status_code != 200:
            raise CrawliexpressException(f"invalid status code {response.status_code}")
        if (
            not response.headers["Content-Type"].startswith("application/json")
            and "captcha" in response.text
        ):
            raise CrawliexpressCaptchaException()

    def get_item(self, item_id):

        """
        Fetches a product informations from its id

        :param item_id: id of the product to fetch, item id of https://www.aliexpress.com/item/20000001708485.html is 20000001708485
        :return: a product
        :rtype: Crawliexpress.Item
        :raises CrawliexpressException: if there was an error fetching the dataz
        """

        r = requests.get(f"{self.base_url}/item/{item_id}.html")
        self._analyze_response(r)
        item = Item()
        item.from_html(r.text)
        return item

    def get_feedbacks(
        self,
        product_id,
        owner_member_id,
        company_id=None,
        v=2,
        member_type="seller",
        page=1,
        with_picture=False,
    ):

        """
        Fetches a product feedback page

        :param product_id: id of the product, item id of https://www.aliexpress.com/item/20000001708485.html is 20000001708485
        :param owner_member_id: member id of the product owner, as stored in **Crawliexpress.Item.owner_member_id**
        :param page: page number
        :param with_picture: limit to feedbacks with a picture
        :return: a feedback page
        :rtype: Crawliexpress.FeedbackPage
        :raises CrawliexpressException: if there was an error fetching the dataz
        """

        params = urllib.parse.urlencode(
            {
                "productId": product_id,
                "ownerMemberId": owner_member_id,
                "companyId": company_id,
                "v": v,
                "memberType": member_type,
                "page": str(page),
                "withPictures": with_picture,
            }
        )
        url = f"{FEEDBACK_URL}?{params}"
        r = requests.get(url)
        self._analyze_response(r)
        feedback_page = FeedbackPage()
        feedback_page.from_html(r.text)
        return feedback_page

    def get_category(self, category_id, category_name, page=1, sort_by="default"):

        """
        Fetches a category page

        :param category_id: id of the category, category id of https://www.aliexpress.com/category/205000221/t-shirts.html is 205000220
        :param category_name: name of the category, category name of https://www.aliexpress.com/category/205000221/t-shirts.html is t-shirts
        :param page: page number
        :param sort_by: indeed
        :type sort_by:
            **default**: best match
            **total_tranpro_desc**: number of orders
        :return: a search page
        :rtype: Crawliexpress.SearchPage
        :raises CrawliexpressException: if there was an error fetching the dataz
        :raises CrawliexpressCaptchaException: if there is a captcha, make sure to use valid cookies to avoid this
        """

        url_params = {
            "CatId": category_id,
            "CatName": category_name,
            "SortType": sort_by,
            "page": page,
        }

        referer = f"{self.base_url}/category/{category_id}/{category_name}.html"

        return self._get_search(url_params, page, referer=referer)

    def get_search(self, text, page=1, sort_by="default"):

        """
        Fetches a search page

        :param text: text search
        :param page: page number
        :param sort_by: indeed
        :type sort_by:
            **default**: best match
            **total_tranpro_desc**: number of orders
        :return: a search page
        :rtype: Crawliexpress.SearchPage
        :raises CrawliexpressException: if there was an error fetching the dataz
        :raises CrawliexpressCaptchaException: if there is a captcha, make sure to use valid cookies to avoid this
        """

        referer = f"{self.base_url}/wholesale"

        return self._get_search(
            {
                "SearchText": text,
                "SortType": sort_by,
                "page": page,
            },
            page,
            referer=referer,
        )

    def _get_search(self, url_params, page, referer=None):

        # build url
        url_params = {
            **{
                "trafficChannel": "main",
                "d": "y",
                "ltype": "wholesale",
                "origin": "y",
                "isrefine": "y",
                "CatId": "0",
            },
            **url_params,
        }
        url_params = urllib.parse.urlencode(url_params)
        url = f"{self.base_url}/glosearch/api/product?{url_params}"

        # build headers
        headers = {
            "Accept": "application/json",
        }
        if referer is not None:
            headers["Referer"] = f"{referer}?{url_params}"

        r = requests.get(url, headers=headers, cookies=self.cookies)
        self._analyze_response(r)
        search_page = SearchPage()
        search_page.from_json(page, r.json())
        return search_page
