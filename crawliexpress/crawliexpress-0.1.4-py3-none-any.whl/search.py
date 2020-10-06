import itertools


class Search:

    """
    A search

    :param text: text search
    :param sort_by: indeed
    :type sort_by:
        **default**: best match
        **total_tranpro_desc**: number of orders
    """

    client = None
    text = None
    sort_by = None

    def __init__(self, client, text, sort_by="default"):
        self.client = client
        self.text = text
        self.sort_by = sort_by

    def __iter__(self):
        page = None
        for i in itertools.count(start=1):
            if page is not None and page.has_next_page() is False:
                # raise StopIteration()
                break
            page = self.get_page(page=i)
            yield page

    def get_page(self, page=1):
        return self.client.get_search(self.text, page=page, sort_by=self.sort_by)
