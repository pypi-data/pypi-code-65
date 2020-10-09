import itertools


class Category:

    """
    A category

    :param category_id: id of the category, category id of https://www.aliexpress.com/category/205000221/t-shirts.html is 205000220
    :param category_name: name of the category, category name of https://www.aliexpress.com/category/205000221/t-shirts.html is t-shirts
    :param sort_by: indeed
    :type sort_by:
        **default**: best match
        **total_tranpro_desc**: number of orders
    """

    client = None
    category_id = None
    category_name = None
    sort_by = None

    def __init__(self, client, category_id, category_name, sort_by="default"):
        self.client = client
        self.category_id = category_id
        self.category_name = category_name
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
        return self.client.get_category(
            self.category_id,
            self.category_name,
            page=page,
            sort_by=self.sort_by,
        )
