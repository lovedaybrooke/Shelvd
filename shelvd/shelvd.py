import datetime
import os
import decimal
import traceback
import logging

from django.db import models
from django.db.models import fields
import requests
from pyparsing import *

import grammar
from models import *
import twitterhelper


class Request(object):

    def __init__(self, bkinput):
        try:
            exp = grammar.expression.parseString(bkinput, parseAll=True)
        except ParseException, message:
            logging.error(traceback.format_exc())
            raise BadThing("Sorry, I didn't understand your input.")

        self.nick = exp.nick
        self.initiator = exp.initiator
        self.terminator = exp.terminator
        self.help = exp.help
        self.currentlyreading = exp.currentlyreading
        self.addreadinglist = exp.addreadinglist
        self.isbn = self.convert_to_isbn_13(exp.isbn)

        if exp.percent:
            decimal_percent = decimal.Decimal(int(exp.percent[0]))
            self.percent = float(decimal_percent / decimal.Decimal(100))

        if exp.page:
            self.page = int(exp.page)

    def perform(self):
        if self.addreadinglist:
            Book.add_to_reading_list(self)
        elif self.currentlyreading:
            Book.tweet_books_currently_reading()
        elif self.help:
            self.tweet_help()
        elif self.initiator:
            self.validate_start_reading()
            book = Book.find_or_create(self)
            Reading.start(book, self)
        elif self.terminator:
            self.validate_end_reading()
            book = Book.find(self)
            reading = Reading.find(book, False)
            reading.end(self)
        elif self.isbn and self.nick:
            self.validate_create_nick()
            book = Book.find(self)
            book.create_nick(self.nick)
        elif 'page' in dir(self) or 'percent' in dir(self):
            self.validate_create_bookmark()
            book = Book.find_or_create(self)
            reading = Reading.find(book, False)
            Bookmark.create(self, reading)
        else:
            raise BadThing("Sorry, I don't understand your input")

    def convert_to_isbn_13(self, original_isbn):
        if len(original_isbn) == 10:
            google_api_key = os.environ['GOOGLE_API_KEY']
            url = ("https://www.googleapis.com/books/v1/volumes"
                "?key={0}&country=GB&userIp=86.184.229.225"
                "&q=isbn:{1}").format(google_api_key, original_isbn)
            bkdata = requests.get(url).json()
            volumedata = bkdata.get('items', [{}])[0].get('volumeInfo', {})
            isbns = bkdata['items'][0]['volumeInfo']['industryIdentifiers']
            for isbn in isbns:
                if isbn["type"] == 'ISBN_13':
                    return isbn['identifier']
        return original_isbn

    def validate_start_reading(self):
        # check there's actually an ISBN
        if not self.isbn:
            raise BadThing("You need to include a 10 or 13 digit ISBN to "
                "start a book.")
        # check reading not already started
        book = Book.find(self)
        if book:
            if Reading.find(book, False):
                raise BadThing("You've already started that book.")

    def validate_end_reading(self):
        # check that the book is in the DB
        book = Book.find(self)
        if not book:
            raise BadThing("You haven't started that book yet.")
        # check that there is an unfinished reading
        if not Reading.find(book, False):
            # if there's a finished or abandoned reading, adjust error message
            if Reading.find(book, True) or Reading.find(book, True, True):
                raise BadThing("You've already finished this book.")
            else:
                raise BadThing("You haven't started that book yet.")

    def validate_create_nick(self):
        # check this book already exists in the database
        if not Book.find(self):
            raise BadThing("You need to start reading this book before you "
                "can nickname it.")
        # check this nickname isn't already being used
        if Book.nick_already_used(self.nick):
            title = Book.nick_already_used(self.nick).title
            raise BadThing("You've already used this nickname for "
                "'{0}'.".format(title))

    def validate_create_bookmark(self):
        # check that book exists in the DB
        book = Book.find(self)
        if not book:
            raise BadThing("You need to start reading this book before you"
                "can log some reading")
        # check that there is an unfinished reading
        reading = Reading.find(book, False)
        if not reading:
            raise BadThing("You need to start reading this book before you "
                "can log some reading.")
        # check that the most recent bookmark is fewer pages than this new one
        else:
            last_bookmark = reading.get_most_recent_bookmark().page
            page = book.calculate_page(self)
            if last_bookmark > page:
                raise BadThing("You've already read this far.")

    def tweet_help(self):
        t = twitterhelper.TwitterHelper()
        t.send_response("To start a book:\n{isbn or nick} start\n{isbn or nick}"
            " begin\n\nTo end a book:\n{isbn or nick} end\n{isbn or nick}"
            " finish")
        t.send_response("To nickname a book:\n{isbn} {nickname}\n\nTo log "
            "reading:\n{isbn or nick} {page no. or %}\n\nTo see books "
            "currently being read:\ncurrently reading")

class BadThing(Exception):
    pass
