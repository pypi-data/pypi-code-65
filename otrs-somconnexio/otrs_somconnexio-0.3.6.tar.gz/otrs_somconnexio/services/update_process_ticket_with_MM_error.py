from pyotrs.lib import DynamicField
from otrs_somconnexio.client import OTRSClient
from otrs_somconnexio.otrs_models.mm_error_article import MMErrorArticle


class UpdateProcessTicketWithMMError:
    """
    Update the ticket process adding articles with the MM error data.

    Receives a ticket_id (str), the HTTP response error (as dict) provided by the MM API,
    and an object, a string indicating which MM class building object failed (ex: account).
    When an error happens trying to build an account or an order-item into the MM system,
    this process creates an article with the information about how the process failed
    and it sends it to OTRS as an article.
    """

    def __init__(self, ticket_id, error, action, object_type):
        self.ticket_id = ticket_id
        self.error = error
        self.action = action
        self.object_type = object_type
        self.df = [DynamicField(name="enviarProxy", value=0)]

        if self.object_type == "Asset":
            self.df.append(DynamicField(name="errorActivacio", value=1))
        else:
            self.df.append(DynamicField(name="errorPeticio", value=1))

    def run(self):
        otrs_client = OTRSClient()

        article = MMErrorArticle(self.error, self.action, self.object_type).call()
        otrs_client.update_ticket(self.ticket_id, article, dynamic_fields=self.df)
