# Import the blueprint.
from flask import Blueprint

api = Blueprint('api', __name__)

from . import tasks, authentication, users
