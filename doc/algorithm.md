# Creating an Algorithm

An algorithm in AlgoBox is a child class of `core.algorithm.ABAlgorithm`.
It must implement two methods. `initialise` and `on_data`.

`on_data` will be called when there is a new update your algorithm cares about. The update and historical context will be provided.

## Execution

The algorithm is executed with "exec" where a context will be provided.
It is important that the algorithm is defined with `class MyAlgorithm(ABAlgorithm):`
and that it implements the above mentioned methods.

The code you submit will be ran with `exec` in the execution environment, defining
your class for our use.

`exec` is not secure, no measures are taken to sandbox your code. This is
because this is not a public system and is expected to be run on a secure network used privately
by an individual or organisation.
