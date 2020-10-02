from crawliexpress.exceptions import (
    CrawliexpressException,
    CrawliexpressCaptchaException,
)
from crawliexpress.item import Item
from crawliexpress.feedback_page import FeedbackPage
from crawliexpress.search_page import SearchPage

import requests
import urllib


FEEDBACK_URL = "https://feedback.aliexpress.com/display/productEvaluation.htm"


class Client:
    base_url = None

    # cookies to avoid capcha
    xman_t = None
    x5sec = None

    # cookies for category search
    aep_usuc_f = None

    def __init__(self, base_url, xman_t=None, x5sec=None, aep_usuc_f=None):
        self.base_url = base_url
        self.xman_t = xman_t
        self.x5sec = x5sec
        self.aep_usuc_f = aep_usuc_f

    def __analyze_response(self, response):
        if response.status_code != 200:
            raise CrawliexpressException(f"invalid status code {response.status_code}")
        elif (
            not response.headers["Content-Type"].startswith("application/json")
            and "captcha" in response.text
        ):
            raise CrawliexpressCaptchaException()

    def get_item(self, item_id):
        r = requests.get(f"{self.base_url}/item/{item_id}.html")
        self.__analyze_response(r)
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
        self.__analyze_response(r)
        feedback_page = FeedbackPage()
        feedback_page.from_html(r.text)
        return feedback_page

    def get_search(self, page_no, category_id=0, search_text=None, sort_by="default"):

        """
        sort_by can be:
        - default: best
        - orders: total_tranpro_desc
        """

        params = {
            "trafficChannel": "main",
            "d": "y",
            "CatId": category_id,
            "ltype": "wholesale",
            "SortType": sort_by,
            "page": page_no,
            "origin": "y",
            "isrefine": "y",
        }
        if search_text is not None:
            params["SearchText"] = search_text
        params = urllib.parse.urlencode(params)
        url = f"{self.base_url}/glosearch/api/product?{params}"
        headers = {"Accept": "application/json"}
        cookies = {
            "xman_t": self.xman_t,
            "x5sec": self.x5sec,
            "aep_usuc_f": self.aep_usuc_f,
        }
        r = requests.get(url, headers=headers, cookies=cookies)
        self.__analyze_response(r)
        search_page = SearchPage()
        search_page.from_json(page_no, r.json())
        return search_page
