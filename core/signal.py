#  signal class
from datetime import dt

from core.event import ABEvent

class Signal(ABEvent):
    raise NotImplementedError("May be removed unless we require additional logic \
    which ABEvent does not support.")
