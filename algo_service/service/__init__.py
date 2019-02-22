from flask import Flask
from service.algorithm import algorithm_bp
from config import Config

algoapp = Flask(__name__)
algoapp.config.from_object = Config

algoapp.register_blueprint(algorithm_bp, url_prefix="/algorithm")
