import datetime as dt

import core

class ABEvent(object):
    """
    AlgoBox event object

    Attributes:
        * type (String) the type of event, one of core.const.Event.*
        * data (Object) some sort of payload attached to the event
        * datetime (datetime.datetime) pass the datetime the event occured here,
            alternatively will default to the datetime on initialisation.
    """
    def __init__(self, type, data=None, datetime=None):
        self.type = type
        self.data = data
        self.datetime = datetime or dt.datetime.utcnow()
