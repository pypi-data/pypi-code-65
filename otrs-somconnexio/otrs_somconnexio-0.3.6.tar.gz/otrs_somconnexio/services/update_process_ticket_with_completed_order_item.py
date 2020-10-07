from pyotrs.lib import DynamicField
from otrs_somconnexio.client import OTRSClient
from otrs_somconnexio.otrs_models.mm_completed_order_item_article import MMCompletedOrderItemArticle


class UpdateProcessTicketWithCompletedOrderItem:
    """
    Update the ticket process with an article to inform that the order item has
    been completed in the MM platform, becoming an activated contract.

    Receives a ticket_id (str), the body (dict), a contract info as a dictionary,
    and new_phone_line (boolean), that checks if the order-item is from a new number
    registration (=non portability).
    """

    def __init__(self, ticket_id, body, new_phone_line=False):
        self.ticket_id = ticket_id
        self.body = body
        self.df = [DynamicField(name="contracteMobilActivat", value=1)]
        if new_phone_line:
            self.df.append(DynamicField(name="msisdn", value=body['phone']))

    def run(self):
        otrs_client = OTRSClient()

        article = MMCompletedOrderItemArticle(self.body).call()
        otrs_client.update_ticket(self.ticket_id, article, dynamic_fields=self.df)
