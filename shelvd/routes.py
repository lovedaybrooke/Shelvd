import logging
import sys
import os

from flask import request, render_template

from shelvd import app
from shelvd.messages import Instruction
from shelvd.models import MessageException, Reading
    

@app.route('/')
def unfinished():
    return render_template('unfinished.html', 
                           readings=Reading.get_reading_list(False, False))

@app.route('/webhook', methods=['POST'])
def webhook():
    if request.values.get('From') == app.config["RECIPIENT_NUMBER"]:
        received = Instruction.process_incoming(request.values.get('Text'))
        return received
    else:
        return 400