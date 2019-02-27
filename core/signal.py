#  signal class

from core.event import ABEvent

class Signal(ABEvent):
    def __init__(self, *args, **kwargs):
        raise NotImplementedError("May be removed unless we require additional \
        logic which ABEvent does not support.")
