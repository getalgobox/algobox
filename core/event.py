import core

class ABEvent(object):
    """AlgoBox event object"""
    def __init__(self, type, details):
        pass

class TransactionEvent(ABEvent):
    def __init__(self, event, topic, dt_occured, quantity, price):

        pass

    @classmethod
    def give_child(cls, direction):
        if direction = core.const.Event.TRANSACTION_BUY:
            return

class TransactionBuy(TransactionEvent):

    def __init__(self):
        pass

class TransactionSell(TransactionEvent):
    pass
