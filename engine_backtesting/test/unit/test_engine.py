import os
import json
import service
import random
import uuid

import datetime as dt

import pytest

from backtest.engine import Backtest
import core

def test_run_backtest():
    dt_from = dt.datetime(year=2018, month=10, day=1)
    dt_to = dt.datetime(year=2019, month=2, day=1)

    bt = Backtest("GDAX:BTC-USD:5M", )

def test_no_look_forward():
    pass
