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

        :rtype: bool
        """

        return (self.page - 1) * size_per_page + len(items) < self.result_count
