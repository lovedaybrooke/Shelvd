import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from shelvd.config import Config


app = Flask(__name__)
app.config.from_object(Config)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

from shelvd import routes, models
