# coding: utf-8
from otrs_somconnexio.otrs_models.abstract_article import AbstractArticle


class MMCompletedOrderItemArticle(AbstractArticle):
    def __init__(self, order_item_completed):
        self.order_item_completed = order_item_completed
        self.subject = "Línia de mòbil donada d'alta a MasMóvil"
        self.body = self._body()

    def _body(self):
        body = ""

        for field in sorted(self.order_item_completed):
            value = self.order_item_completed[field]
            if value:
                body = u"{}{}: {}\n".format(body, field, value)

        return body
