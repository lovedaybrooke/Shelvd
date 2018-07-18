from flask import request

from shelvd import app
from shelvd.messages import Instruction
from shelvd.models import MessageException

@app.route('/')
def index():
    return "Hello, World!"

@app.route('/webhook')
def webhook():
    message = request.args.get('message')
    if message:
        return Instruction.process_incoming(message)
    else:
        return "You need to give me something to work with"