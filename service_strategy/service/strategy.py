import json
import uuid
import collections

from flask import Blueprint, request, make_response, abort, jsonify
from flask import current_app

from service.models import Strategy
from service.models import give_session

strategy_bp = Blueprint('strategy', __name__)

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


@strategy_bp.route("/", methods=["GET"])
def get_all_strategy():
    """
    Returns a list of Strategies and their details. Probably don't need to
    paginate that, right?
    """
    db_session = give_session()
    all_strats = db_session.query(Strategy).all()

    return make_response(jsonify([strat.as_dict() for strat in all_strats]), 200)


@strategy_bp.route("/", methods=["POST"])
def strategy_create():
    """
    expects a json/application encoded request in the following format:
    {
        "name": "Really Great Strategy Maybe",
        "execution_code": "some python code",
        "data_format": "CANDLE" or "TICK",
        "subscribes_to": ["GDAX:BTC-USD:5M"],
        "lookback_period": 40
    }

    - `name` shall be a unique, user-defined name for the strategy
    - `execution_code` shall contain the code for executing the strategy
    - `data_format` shall specify whether the strategy listens to candles or ticks
    - `subscribes_to` specifies data sources this strategy will subscribe to
    - `lookback_period` optionally specifies the number of candles or
       ticks previous to this one which will be available to the strategy in
       its context upon execution, defaults to 30.

      Eventually subscribes_to will support regex or something more flexible.

      Returns a json object of the new record in full, including unique ID.
    """
    db_session = give_session()
    # force will attempt to read the json even if the client does not specify
    # application/json as the content type, It will fail with an exception.
    new_strategy = GetOrThrowDict(request.get_json(force=True))
    strategy_id = str(uuid.uuid4())

    strategy_instance = Strategy(
        id = strategy_id,
        name = new_strategy["name"],
        execution_code = new_strategy["execution_code"],
        data_format = new_strategy["data_format"],
        subscribes_to = new_strategy["subscribes_to"],
        lookback_period = new_strategy.get(
            "lookback_period"
        ) or 30
    )

    db_session.add(strategy_instance)
    try:
        db_session.commit()
    except Exception as e:
        return make_response(jsonify({
            "error": "We were unable to write your strategy to the database.",
            "exception": str(e)
        }), 500)

    return make_response(jsonify(strategy_instance.as_dict()), 201)


@strategy_bp.route("/execute/<strategy_id>", methods=["POST"])
def strategy_execute(strategy_id):
    """
    This is a bit like the observer pattern but with multiple services involved.
    Expects to receive the following from the data or backtesting service.

    {
        "update": {},
        "context": [],
        "topic": "GDAX:BTC-USD:5M",
    }
    """
    db_session = give_session()

    req = GetOrThrowDict(request.get_json(force=True))
    strategy_rec = db_session.query(Strategy).filter_by(id=strategy_id).one()

    UserStrat = type("UserStrat", core.strategy.ABStrategy, {
        "initialise": initialise,
        "on_data": on_data
    })

    context = req["context"]
    update = req["update"]

    context = [core.format.Candle.from_dict(c) for c in context]
    update = core.format.Candle.from_dict(c)

    signal = core.strategy.execute(UserStrat, req["context"], req["update"],
        lookback_period=strategy_rec.lookback_period
    )

    return make_response(jsonify(signal), 200)




















#
