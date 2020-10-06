from crawliexpress.exceptions import CrawliexpressException


class SearchPage:

    """
    A search page
    """

    page = None
    """page number"""
    result_count = None
    """Number of result for the whole search"""
    size_per_page = None
    """Number of result per page"""
    items = None
    """List of products, raw from JS parsing"""

    def from_json(self, page, json):
        self.page = page
        self.result_count = json["resultCount"]
        self.size_per_page = json["resultSizePerPage"]
        self.items = json["items"]

    def has_next_page(self):

        """
        Returns true if there is a following page, useful for crawling

        :rtype bool:
        """

        return len(self.items) == self.size_per_page

    def __iter__(self):
        yield "page", self.page
        yield "result_count", self.result_count
        yield "size_per_page", self.size_per_page
        yield "items", self.items
        yield "has_next_page", self.has_next_page()
