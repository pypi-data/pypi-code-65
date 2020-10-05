from easyqueue.core.objects.ticket.schema import TicketSchema
from easyqueue.core.objects.base.eqobject import EQObject


class Ticket(EQObject):

    TICKET = 'ticket'

    _schema = TicketSchema()
    _args = {'user_id', 'user_identificator', 'region', 'queue_id', 'queue_identificator'}
    _hash_args = {'user_id', 'queue_id'}

    def __generate_identificator(self, region, user_identificator, queue_identificator):
        return '{ticket}_{region}_{user}_{queue}'.format(
            ticket=self.TICKET, region=region, user=user_identificator, queue=queue_identificator)

    def __init__(self,  user_id, user_identificator, region, queue_id, queue_identificator, is_active=True):
        self.user_id = user_id
        self.user_identificator = user_identificator
        self.region = region
        self.queue_id = queue_id
        self.queue_identificator = queue_identificator
        self.is_active = is_active
        super().__init__(identificator=self.__generate_identificator(
            region=region, user_identificator=user_identificator, queue_identificator=queue_identificator))
