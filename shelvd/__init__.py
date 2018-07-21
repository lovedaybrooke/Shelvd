import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from shelvd.config import Config


app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)

from shelvd import routes, models
