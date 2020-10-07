# coding: utf-8
from otrs_somconnexio.otrs_models.abstract_article import AbstractArticle


class ProvisionArticle(AbstractArticle):
    def __init__(self, service_type, order_id):
        self.subject = "Sol·licitud {} {}".format(
            service_type,
            order_id
        )
