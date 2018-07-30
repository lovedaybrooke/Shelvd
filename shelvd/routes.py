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

@app.route('/finished')
def finished():
    return render_template('finished.html', 
        readings=Reading.get_year_by_year_reading_list())

@app.route('/abandoned')
def abandoned():
    return render_template('abandoned.html', 
        readings=Reading.get_reading_list(True, True))

@app.route('/webhook', methods=['POST'])
def webhook():
    if request.values.get('From') == app.config["RECIPIENT_NUMBER"]:
        received = Instruction.process_incoming(request.values.get('Text'))
        return received
    else:
        return 400