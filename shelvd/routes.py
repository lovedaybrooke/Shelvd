import logging
import sys
import os
import json
import datetime

from flask import request, render_template, jsonify, redirect

from shelvd import app
from shelvd.messages import Instruction
from shelvd.models import MessageException, Reading, Author, Book


@app.route('/')
def unfinished():
    return render_template('unfinished.html',
                           readings=Reading.get_reading_list(False, False))


@app.route('/finished/all')
def finished_all():
    return render_template('finished.html',
                           readings=Reading.get_year_by_year_reading_list())


@app.route('/finished/')
def finished():
    year = datetime.datetime.now().year
    return redirect("/finished/{0}".format(year), code=302)


@app.route('/finished/<year>')
def finished_by_year(year):
    year, last_year, next_year = Reading.available_years(int(year))
    return render_template('finished_year.html',
                           readings=Reading.get_year_reading_list(year),
                           year=year,
                           last_year=last_year,
                           next_year=next_year)



@app.route('/abandoned')
def abandoned():
    return render_template('abandoned.html',
                           readings=Reading.get_reading_list(True, True))


@app.route('/stats')
def stats():
    year = datetime.datetime.now().year
    return redirect("/stats/{0}".format(year), code=302)


@app.route('/stats/<year>')
def stats_for_year(year):
    year, last_year, next_year = Reading.available_years(int(year))
    return render_template('stats.html',
                           author_data=Author.get_years_author_data(
                              year, 'nationality'),
                           year=year,
                           last_year=last_year,
                           next_year=next_year)


@app.route('/bookinfo/<isbn>', methods=['POST', 'GET'])
def bookinfo(isbn):
    book = Book.query.filter_by(isbn=isbn).first()
    if request.method == 'GET':
        return render_template('bookinfo.html',
                               book=book)
    if request.method == 'POST':
        outcome = book.update_info(request.form)
        return render_template('bookinfo.html',
                               book=book,
                               success=outcome["success"],
                               error=outcome["error"],
                               input_data=request.form)


@app.route('/log', methods=['POST', 'GET'])
def logreading():
    if request.method == 'GET':
        return render_template('webform.html')
    if request.method == 'POST':
        outcome = Instruction.process_from_web(request.form)
        return render_template('webform.html', success=outcome["success"],
                               error=outcome["error"])


@app.route('/data')
def data():
    year = int(request.values.get('year'))
    if request.values.get('type') in ('nationality', 'ethnicity', 'gender'):
        data = json.dumps(Author.get_years_author_data(
            year, request.values.get('type')))
    else:
        data = json.dumps({})
    return jsonify(data)


@app.route('/webhook', methods=['POST'])
def webhook():
    if request.values.get('From') == app.config["RECIPIENT_NUMBER"]:
        received = Instruction.process_incoming(request.values.get('Text'))
        return received
    else:
        return "Unauthorized", 401
