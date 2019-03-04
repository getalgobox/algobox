import os
import json
import service

import pytest
import sqlalchemy

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from service.models import Strategy
from testcontainers.postgres import PostgresContainer

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

    return {"container": psql_container, "session": session}

def psql_stop(psql_container):
    psql_container.stop()

def test_create_strategy(client, psql):
    container = psql["container"]
    session = psql["session"]

    response = client.post("/strategy/", json={
        "name": "Lambo by Monday",
        "execution_code": "some python code",
        "data_format": "CANDLE",
        "subscribes_to": ["GDAX:BTC-USD:5M"],
        "lookback_period": 40
    })

    assert response.status_code == 201
    # pretty much always true until we actually implement testcontainers
    # properly here. !TODO (flask test client magic methods for replacing session?)
    assert len(json.loads(client.get("/strategy/").data)) > 0

    psql_stop(container)

def test_create_strategy_missing_field(client, psql):
    container = psql["container"]
    session = psql["session"]

    response = client.post("/strategy/", json={
        "name": "Lambo by Monday",
        "execution_code": "some python code",
        "data_format": "CANDLE",
        "lookback_period": 40
    })

    assert response.status_code == 400
    assert b" key is required" in response.data
    assert len(json.loads(client.get("/strategy/").data)) > 0

    psql_stop(container)

def test_run_algorithm(client, psql):
    strat_code = """
def initialise(self):
    pass

def on_data(self, context, update):
    return {"signal": core.signal.random()}
"""

    create_response = client.post("/strategy/", json={
        "name": "Lambo by Now",
        "execution_code": strat_code,
        "data_format": "CANDLE",
        "subscribes_to": ["GDAX:BTC-USD:5M"],
        "lookback_period": 0
    })

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

    call_response = client.post("/strategy/execute/{}".format(created_dict["id"]),
    json=data)
    import pdb; pdb.set_trace()

    assert "signal" in call_response.json
