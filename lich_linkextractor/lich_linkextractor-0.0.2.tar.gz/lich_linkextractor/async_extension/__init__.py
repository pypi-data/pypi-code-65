import logging
import asyncio
import base64
import json
from aiohttp import ClientSession
from scrapy.utils.misc import load_object
from lich_linkextractor.utils import as_deferred
from scrapy.utils.python import to_unicode
logger = logging.getLogger(__name__)

DEPTH_LIMIT_KEY = "extractor.depth_limit"
DROP_ANCHOR_KEY = "extractor.drop_anchor"
key_map = {
    "allow":"AllowedURLFilters",
    "deny":"DisallowedURLFilters",
    "allow_domains":"AllowedDomains",
    "deny_domains":"DisallowedDomains",
    "restrict_xpaths":"XPathQuerys",
    "restrict_css":"CSSSelectors",
}

class AyncExtractor:
    def __init__(self, depth_limit=None,server_addr=None):
        self.depth_limit = depth_limit
        self.server_addr = server_addr
        self.client=ClientSession()
    
    @classmethod
    def from_crawler(cls, crawler):
        settings = crawler.settings
        depth_limit = crawler.settings.get("DEPTH_LIMIT")
        depth_limit = int(depth_limit) if depth_limit else None
        server_addr = crawler.settings.get("EXTRACTOR_ADDR")
        return cls(depth_limit=depth_limit, server_addr=server_addr)
    
    def process_response(self, response):
        d = as_deferred(self.extract_links(response))
        def _on_success(link_dict):
            if len(link_dict) > 0:
                assert "extractor.links" not in response.meta
                response.meta["extractor.links"] = link_dict
        d.addCallback(_on_success)
        d.addBoth(lambda _: response)
        return d
    
    async def get_links(self, rules, response):
        res={}
        base_ex_req={
            "URL":response.url,
            "Content":to_unicode(base64.encodebytes(response.body)),
            "ContentType":to_unicode(response.headers.get("Content-Type"))
        }        
        for rule in rules :
            ex_req=base_ex_req
            for key in [
                "allow",
                "deny",
                "allow_domains",
                "deny_domains",
                "restrict_xpaths",
                "restrict_css",
            ]:
                tag_name = rule.get("tag_name", "default_tag")
                v = rule.get(key, None)
                if v is not None and (
                    isinstance(v, str)
                    or (isinstance(v, (list, tuple)) and all(isinstance(i, str) for i in v))
                ):
                    ex_req[key_map[key]] = v
            resp = await self.send(self.server_addr,json.dumps(ex_req),3)
            s = set()
            for value in resp.values():
                for link in value:
                    s.add(link)
            res[tag_name] = res[tag_name]+list(s) if tag_name in res else list(s)
        return res

    def _get_max_depth(self, req_depth_limit):
        if self.depth_limit is None:
            return req_depth_limit
        if req_depth_limit is None:
            return self.depth_limit
        return min(self.depth_limit, req_depth_limit)

    async def extract_links(self, response):
        rules = response.request.meta.get("extractor.rules", None)
        if rules is None or not isinstance(rules, list):
            return {}
        meta = response.request.meta
        # check depth limit
        depth = int(meta["depth"]) if "depth" in meta else None
        req_depth_limit = (
            int(meta[DEPTH_LIMIT_KEY]) if DEPTH_LIMIT_KEY in meta else None
        )
        max_depth = self._get_max_depth(req_depth_limit)
        if max_depth and depth and depth >= max_depth:
            return {}
        links = await self.get_links(rules, response)
        return links

    async def send(self,addr,data,num_retries):
        if addr!=None and data!=None:
            async with self.client.post(addr, data=data) as response:
                if response.status == 200:
                    return await response.json()
                if response.status == 404:
                    if num_retries>0:
                        return await self.send(addr, data, num_retries-1)
                response.raise_for_status()
                    
    async def spider_closed(self):
        return await self.client.close()