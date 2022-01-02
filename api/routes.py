from flask import Blueprint, Response, stream_with_context, request
from pip._vendor import requests

api = Blueprint('api', __name__, template_folder='templates')
