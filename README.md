![AlgoBox](algobox.png)

Algobox is an open source framework for writing, managing and running trading
strategies. It provides an interface and infrastructure for developing, deploying
and running algorithmic trading bots. It allows users to self-host these bots
on their own infrastructure, at home or in the cloud.

Think QuantConnect or Quantopian but self hosted.

The decision has been taken to implement necessary code from scratch,
as a learning experience. The project is not yet ready for general use,
though if you would like to contribute this would be welcome.

We have a trello board where we track todo's, bugs and more [here](https://trello.com/b/a4PSkfDs/algobox).

![](https://i.imgur.com/2HAoR3F.jpg)


# Scope

This is a large project. It will probably never be feature complete.

These are some of my ambitions for this project:

  - To provide a suite of tools for managing, normalising and validating data
     from within the UI.
  - To provide an extensible framework for data collection and storage.
  - To provide live, paper and backtest execution capabilities for strategies
     across stocks, equities, forex & crypto.
  - To provide excellent reporting and visualisation for all strategies
  - To provide a UI to manage deployment of algorithms, their configuration,
     parameters and performance.

# Current Functionality
 - AlgoBox has a Backtesting and Reporting engine built on ffn.
    Documentation can be found [here](doc/backtest.md) & [here](core/backtest/manager.py). There are Jupyter notebooks showing usage in the examples folder [here](examples/).


# Workflow

Committing straight to master isn't really a crime when you're working alone and have no features or releases to break.. right?
