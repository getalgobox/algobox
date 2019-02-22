import os
import json
import service
import unittest

import pytest
import sqlalchemy

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from service.models import Algorithm
from testcontainers.postgres import PostgresContainer

@pytest.fixture
def client():
    service.algoapp.config["TESTING"] = True
    client = service.algoapp.test_client()
    return client

@pytest.fixture
def psql():
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

def test_create_algorithm(client, psql):
    container = psql["container"]
    session = psql["session"]

    client.post("/algorithm/", json={
        "algorithm_name": "Lambo by Monday",
        "execution_code": "some python code",
        "data_format": "CANDLE" or "TICK",
        "subscribes_to": ["GDAX:BTC-USD:5M"],
        "historical_context_number": 40
    })
    
    assert len(json.loads(client.get("/algorithm/").data)) > 0

    psql_stop(container)
