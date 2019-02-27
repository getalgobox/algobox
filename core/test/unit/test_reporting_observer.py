import pytest

import core
from core.reporting.observer import ABObserver
from core.event import ABEvent


@pytest.fixture
def observer():
    return ABObserver()

def test_observer(observer):

    events = [ABEvent(
            type=core.const.Event.PRICE_UPDATE,
            data=12.42
        ),
        ABEvent(
            type=core.const.Event.PRICE_UPDATE,
            data=12.38
        ),
        ABEvent(
            type=core.const.Event.SIGNAL_BUY,
        ),
        ABEvent(
            type=core.const.Event.ORDER_PLACED,
        ),
        ABEvent(
            type=core.const.Event.EQUITY_UPDATE,
            data=10000
        ),
        ABEvent(
            type=core.const.Event.EQUITY_UPDATE,
            data=9983.25
        ),
    ]

    for e in events:
        observer.update(e)

    assert len(observer.equity_series) == 2
    assert len(observer.asset_price_series) == 2
    assert len(observer.event_series) == 2
