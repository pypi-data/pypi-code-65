from pyotrs.lib import DynamicField
from otrs_somconnexio.client import OTRSClient
from otrs_somconnexio.otrs_models.mm_success_article import MMSuccessArticle


class UpdateProcessTicketWithMMSuccessAnswer:
    """
    Update the ticket process with an article to inform about that the success in
    entering the registration request to MM (order-item creation).

    Receives a ticket_id (str), a body, and an id for the order item created
    (orderItemId).
    """

    def __init__(self, ticket_id, body, orderItemId=None):
        self.ticket_id = ticket_id
        self.body = body
        self.df = [DynamicField(name="introPlataforma", value=1),
                   DynamicField(name="enviarProxy", value=0),
                   DynamicField(name="MMOrderItemId", value=orderItemId)]

    def run(self):
        otrs_client = OTRSClient()

        article = MMSuccessArticle(self.body).call()
        otrs_client.update_ticket(self.ticket_id, article, dynamic_fields=self.df)
