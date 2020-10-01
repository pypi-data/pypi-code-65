

class TransactionSide(object):
    BUY = 0
    SELL = 1
    BUY_LIMIT = 2
    SELL_LIMIT = 3
    BUY_STOP = 4
    SELL_STOP = 5


class TransactionType(object):
    ORDER_OPEN = 0
    ORDER_PENDING = 1
    ORDER_CLOSE = 2
    ORDER_MODIFY = 3
    ORDER_DELETE = 4


class TransactionStatus(object):
    ERROR = 0
    PENDING = 1
    ACCEPTED = 2
    REJECTED = 4
