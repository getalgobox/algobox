import core
import pandas as pd
import numpy as np
import datetime as dt

dt_from = dt.datetime(year=2000, month=1, day=1)
dt_to = dt.datetime(year=2018, month=12, day=1)

data = core.ts_generator.CandleTimeSeriesGenerator(
    dt_from,
    dt_to,
    core.time.FTSE(),
    interval="1d",
    topic="IG:LLOY:1D"
)

bt = core.backtest.manager.BacktestManager(
    topic="IG:LLOY:1D",
    dt_from=dt_from,
    dt_to=dt_to,
    algo_id=1,
    data=data
)
bt.push_update = bt._dry_push_random_signal

for context, update in bt:
    pass

perf = bt.finalise()
print(perf["equity"].stats)
import pdb; pdb.set_trace()
