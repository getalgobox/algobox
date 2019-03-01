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
