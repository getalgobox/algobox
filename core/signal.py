import numpy as np

import core
from core.event import ABEvent


class Signal(ABEvent):
    def __init__(self, *args, **kwargs):
        raise NotImplementedError("May be removed unless we require additional \
        logic which ABEvent does not support.")


def random(p=[0.15,0.15,0.70]):
    """
    return a random signal

    Arguments:
        * p (list) a numpy probability distribution for buy, sell, no_action
            in that order.
    """

    return {"signal": np.random.choice([
        core.const.Event.SIGNAL_BUY,
        core.const.Event.SIGNAL_SELL,
        core.const.Event.SIGNAL_NO_ACTION
    ])}
