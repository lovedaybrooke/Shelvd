import logging
import sys
import os

from flask import request

from shelvd import app
from shelvd.messages import Instruction
from shelvd.models import MessageException

@app.route('/')
def index():
    return "Hello, World!"

@app.route('/webhook', methods=['POST'])
def webhook():
    if request.values.get('From') == app.config["RECIPIENT_NUMBER"]:
        received = Instruction.process_incoming(request.values.get('Text'))
        return received
    else:
        return 400