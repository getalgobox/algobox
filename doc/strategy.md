# Creating an Strategy

An strategy in AlgoBox is a child class of `core.strategy.ABStrategy`.
It must implement two methods. `initialise` and `on_data`.

`initialise` will be called upon instantiation of the class, this happens
every time there is some new data to analyse.

`on_data` will be called when there is a new update your strategy cares about. The update and historical context will be provided.

If you are creating your strategy via the web interface, you must simply define
`initialise` and `on_data` as in this example below:

```
def initialise(self):
    print("I'm called each time there is some data to analyse!")


def on_update(self, context, update):
    print("I perform analysis on data and decide which action to take.")
    return core.signal.random()
```

If you are using the library, you must define a class with these methods. It's nasty that we have to include 'self', but unavoidable
for now.

```
import core
from core.strategy import ABStrategy

class MyStrat(core.strategy.ABStrategy):

    def initialise(self):
        print("I'm called each time there is some data to analyse!")


    def on_update(self, context, update):
        print("I perform analysis on data and decide which action to take.")
        return core.signal.random()
```

Now your strategy is ready for use.
