import json
import uuid
import collections
import traceback

from flask import Blueprint, request, make_response, abort, jsonify
from flask import current_app

import core

from service.models import Strategy
from service.models import give_session, give_test_session
from service.utils import GetOrThrowDict

strategy_bp = Blueprint('strategy', __name__)

def give_db_session(request):
    """
    Check if we're testing, if so return test session to use test psql server.
    Otherwise; return normal session.

    Possibly exploitable or at least weird for a public API. If we ever envision
    AlgoBox being used on a multi-user, platform we should obviously add
    authentication preventing POTENTIAL exploitation of this.

    If we try and run multiple tests at once, this will probably break.
    """

    if "TESTING" in request.headers:
        return give_test_session(request.headers["port"])
    else:
        return give_session()

@strategy_bp.route("/", methods=["GET"])
def get_all_strategy():
    """
    Returns a list of Strategies and their details. Probably don't need to
    paginate that, right?
    """
    db_session = give_db_session(request)
    all_strats = db_session.query(Strategy).all()
    db_session.remove()
    return make_response(jsonify([strat.as_dict() for strat in all_strats]), 200)

@strategy_bp.route("/<id>", methods=["GET"])
def get_single_strategy(id):
    db_session = give_db_session(request)
    strategy_rec = db_session.query(Strategy).filter_by(id=strategy_id).one()
    db_session.remove()
    return make_response(jsonify(strategy_rec.as_dict()), 200)

@strategy_bp.route("/subscribed", methods=["GET"])
def strategy_get_subscribed():
    """
    Return a map of strategies and topics they subscribe to.
    """
    db_session = give_db_session()

    subscriber_map = collections.defaultict(list)

    strategies = db_session.query(Strategy).filter_by(active=True).all()

    db_session.remove()
    for strat in strategy:
        subscriber_map[strat.id] = strat.subscribes_to

    # filter out strategies subscribed to nothing, probably..
    subscriber_map = {k: v for k, v in subscriber_map.items() if v}

    return make_response(jsonify(subscriber_map), 200)

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
    db_session = give_db_session(request)
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
        db_session.remove()
    except Exception as e:
        db_session.remove()
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
    db_session = give_db_session(request)

    req = GetOrThrowDict(request.get_json(force=True))
    strategy_rec = db_session.query(Strategy).filter_by(id=strategy_id).one()

    # try:

    initialise, on_data = core.strategy.define_and_return(strategy_rec.execution_code)

    db_session.remove()

    print(dir())
    UserStrat = type("UserStrat", (core.strategy.ABStrategy, ), {
        "initialise": initialise,
        "on_data": on_data
    })

    # except Exception as e:
    #     return make_response(jsonify({"error": """
    #     There was an error executing the strategy code you provided.
    #     Exception: {}
    #     Traceback:
    #     {}
    #
    #     """.format(
    #         str(e), traceback.format_exc()
    #     )}), 400)


    context = req["context"]
    update = req["update"]

    context = [core.format.Candle.from_dict(c) for c in context]
    update = core.format.Candle.from_dict(update)

    signal = core.strategy.execute(UserStrat, req["context"], req["update"],
        lookback_period=strategy_rec.lookback_period
    )

    return make_response(jsonify(signal), 200)


@strategy_bp.route("/<id>", methods=["PATCH"])
@strategy_bp.route("/<id>", methods=["PUT"])
def strategy_update(id):
    """
    accepts patch like requests or full objects
    """
    db_session = give_db_session(request)
    strategy_rec = db_session.query(Strategy).filter_by(id=strategy_id).one()

    for k, v in request.get_json(force=True):
        setattr(strategy_rec, k, v)

    try:
        db_session.add(strategy_rec)
        db_session.commit()
        db_session.remove()
    except Exception as e:
        db_session.remove()
        return make_response(
            jsonify(
                {"error": "An error occured: {}".format(str(e))}
            ), 400
        )

    return make_response(jsonify(strategy_rec.to_dict()), 201)
























#
