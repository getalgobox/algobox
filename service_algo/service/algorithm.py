import json
import uuid
import collections

from flask import Blueprint, request, make_response, abort, jsonify
from flask import current_app

from service.models import Algorithm
from service.models import give_session

algorithm_bp = Blueprint('algorithm', __name__)

class GetOrThrowDict(collections.UserDict):
    """
    Used to wrap dictionaries which should always have keys we request with
    __getitem__.

    If a key is not present the user has made a mistake, and should
    be informed that they are missing a required key.

    If a key is optional, the get method should be used as this is unchanged.
    """

    def __getitem__(self, key):
        try:
            return self.data[key]
        except KeyError as e:
            abort(make_response(jsonify({
                "error": "the '{}' key is required but was was not found in\
                the object you provided.".format(key).replace("\n", "")
            }), 400))


@algorithm_bp.route("/", methods=["GET"])
def get_all_algorithm():
    """
    Returns a list of algorithms and their details. Probably don't need to
    paginate that, right?
    """
    db_session = give_session()
    all_algorithms = db_session.query(Algorithm).all()

    return make_response(jsonify([algo.as_dict() for algo in all_algorithms]), 200)


@algorithm_bp.route("/", methods=["POST"])
def algorithm_post():
    """
    expects a json/application encoded request in the following format:
    {
        "algorithm_name": "Really Great Algorithm Maybe",
        "execution_code": "some python code",
        "data_format": "CANDLE" or "TICK",
        "subscribes_to": ["GDAX:BTC-USD:5M"],
        "historical_context_number": 40
    }

    - `algorithm_name` shall be a unique, user-defined name for the algorithm
    - `execution_code` shall contain the code for executing the strategy.
    - `data_format` shall specify whether the algorithm listens to candles or ticks
    - `subscribes_to` specifies data sources this strategy will subscribe to
    - `historical_context_number` optionally specifies the number of candles or
       ticks previous to this one which will be available to the algorithm in
       its context upon execution, defaults to 30.

      Eventually subscribes_to will support regex or something more flexible.

      Returns a json object of the new record in full, including unique ID.
    """
    db_session = give_session()
    # force will attempt to read the json even if the client does not specify
    # application/json as the content type, It will fail with an exception.
    new_algorithm = GetOrThrowDict(request.get_json(force=True))
    algorithm_id = str(uuid.uuid4())

    algorithm_instance = Algorithm(
        id = algorithm_id,
        name = new_algorithm["name"],
        execution_code = new_algorithm["execution_code"],
        data_format = new_algorithm["data_format"],
        subscribes_to = new_algorithm["subscribes_to"],
        historical_context_number = new_algorithm.get(
            "historical_context_number"
        ) or 30
    )

    db_session.add(algorithm_instance)
    try:
        db_session.commit()
    except Exception as e:
        return make_response(jsonify({
            "error": "We were unable to write your algorithm to the database.",
            "exception": str(e)
        }), 500)

    return make_response(jsonify(algorithm_instance.as_dict()), 201)


@algorithm_bp.route("/execute/<algorithm_id>/", methods=["POST"])
def algorithm_execute(algorithm_id):
    """
    This is a bit like the observer pattern but with multiple services involved.
    Expects to receive the following from the data or backtesting service.

    {
        "update": {},
        "context": [],
        "topic": "GDAX:BTC-USD:5M",
        "format": "CANDLE"
    }
    """
