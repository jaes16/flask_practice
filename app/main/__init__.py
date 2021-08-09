from flask import Blueprint

bp = Blueprint('main', __name__)

# import the handlers.py module, so that the error handlers in it are registered with the blueprint
from app.main import forms, routes
