from crawliexpress.exceptions import CrawliexpressException

import re
import json
import _jsonnet


RUN_PARAMS_RE = re.compile(r"window\.runParams = ({.+?});$", re.MULTILINE | re.DOTALL)


class Item:
    run_params = None
    product_id = None
    owner_member_id = None
    company_id = None
    title = None
    description = None
    image = None

    def from_html(self, html):

        matches = RUN_PARAMS_RE.search(html)
        if matches is None:
            raise CrawliexpressException("could not find runParams")

        self.run_params = run_params = json.loads(
            _jsonnet.evaluate_snippet("snippet", matches.group(1))
        )
        if "data" not in run_params:
            raise CrawliexpressException("unknown runParams structure")

        data = run_params["data"]

        if "feedbackModule" not in run_params["data"]:
            raise CrawliexpressException("unknown runParams structure")

        feedback_module = data["feedbackModule"]

        self.product_id = feedback_module["productId"]
        self.owner_member_id = feedback_module["sellerAdminSeq"]
        self.company_id = feedback_module["companyId"]

        if "pageModule" not in run_params["data"]:
            raise CrawliexpressException("unknown runParams structure")

        page_module = data["pageModule"]

        self.title = page_module["title"]
        self.description = page_module["description"]
        self.image = page_module["imagePath"]

    def __iter__(self):
        yield "product_id", self.product_id
        yield "owner_member_id", self.owner_member_id
        yield "company_id", self.company_id
        yield "title", self.title
        yield "description", self.description
        yield "image", self.image
