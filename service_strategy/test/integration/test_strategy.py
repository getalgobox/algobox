import os
import copy
import json
import service

import pytest
import sqlalchemy

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from service.models import Strategy
from testcontainers.postgres import PostgresContainer

TEST_HEADER = {"TESTING": "True"}

@pytest.fixture
def client():
    service.stratapp.config["TESTING"] = True
    client = service.stratapp.test_client()
    return client

@pytest.fixture
def psql():
    """
    We need to modify the Flask Application to accept a seperate
    sessionmaker for testing. !TODO
    """
    psql_container = PostgresContainer("postgres:9.6")
    psql_container.POSTGRES_USER = "test"
    psql_container.POSTGRES_PASSWORD = "test"
    psql_container.POSTGRES_DB = "test"
    psql_container.start()

    engine = sqlalchemy.create_engine(
        psql_container.get_connection_url()
    )

    session = sessionmaker(bind=engine)()

    # alert webservice to port for this database
    port = psql_container.get_connection_url().split(":")[-1].split("/")[0]
    header = copy.copy(TEST_HEADER)
    header["port"] = port

    return {"container": psql_container, "session": session, "header": header}

def psql_stop(psql_container):
    psql_container.stop()

def test_create_strategy(client, psql):
    container = psql["container"]
    session = psql["session"]
    header = psql["header"]

    response = client.post("/strategy/", json={
        "name": "Lambo by Monday",
        "execution_code": "some python code",
        "data_format": "CANDLE",
        "subscribes_to": ["GDAX:BTC-USD:5M"],
        "lookback_period": 40
    }, headers=header)

    assert response.status_code == 201
    # pretty much always true until we actually implement testcontainers
    # properly here. !TODO (flask test client magic methods for replacing session?)
    assert len(json.loads(client.get("/strategy/", headers=header).data)) > 0

    psql_stop(container)

def test_create_strategy_missing_field(client, psql):
    container = psql["container"]
    session = psql["session"]
    header = psql["header"]

    response = client.post("/strategy/", json={
        "name": "Lambo by Monday",
        "execution_code": "some python code",
        "data_format": "CANDLE",
        "lookback_period": 40
    }, headers=header)

    assert response.status_code == 400
    assert b" key is required" in response.data
    assert len(json.loads(client.get("/strategy/", headers=header).data)) == 0

    psql_stop(container)

def test_run_algorithm(client, psql):
    header = psql["header"]

    strat_code = """
def initialise(self):
    pass

def on_data(self, context, update):
    return core.signal.random()
"""

    create_response = client.post("/strategy/", json={
        "name": "Lambo by Now",
        "execution_code": strat_code,
        "data_format": "CANDLE",
        "subscribes_to": ["GDAX:BTC-USD:5M"],
        "lookback_period": 0
    }, headers=header)

    created_dict = create_response.json
    print(created_dict)

    assert create_response.status_code == 201

    data = {"context": [], "update": {
            "datetime": 1551398400,
            "open": 100,
            "close": 101,
            "high": 102,
            "low": 98.20,
            "topic": "GDAX:BTC-USD:5M"
        }
    }

    call_response = client.post("/strategy/execute/{}".format(
            created_dict["id"]
        ),
        json=data,
        headers=header
    )

    assert "signal" in call_response.json
