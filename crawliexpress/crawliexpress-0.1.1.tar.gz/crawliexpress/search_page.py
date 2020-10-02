from crawliexpress.exceptions import CrawliexpressException


class SearchPage:
    page = None
    result_count = None
    size_per_page = None
    items = None

    def from_json(self, page, json):
        self.page = page
        self.result_count = json["resultCount"]
        self.size_per_page = json["resultSizePerPage"]
        self.items = json["items"]

    def has_next_page(self):
        return len(self.items) == self.size_per_page

    def __iter__(self):
        yield "page", self.page
        yield "result_count", self.result_count
        yield "size_per_page", self.size_per_page
        yield "items", self.items
        yield "has_next_page", self.has_next_page()
