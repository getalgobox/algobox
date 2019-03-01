from flask import Flask
from service.strategy import strategy_bp
from config import Config

stratapp = Flask(__name__)
stratapp.config.from_object = Config

stratapp.register_blueprint(strategy_bp, url_prefix="/strategy")
