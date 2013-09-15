import datetime

from django.db import models
from django.db.models import fields
import logging
import decimal
import traceback

import requests
from pyparsing import *

import grammar
from models import *


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
        self.readinglist = exp.readinglist
        self.ISBN = self.convert_to_ISBN_13(exp.ISBN)

        if exp.percent:
            decimal_percent = decimal.Decimal(int(exp.percent[0]))
            self.percent = float(decimal_percent / decimal.Decimal(100))

        if exp.page:
            self.page = int(exp.page)

    def perform(self):
        if self.readinglist:
            Book.add_to_reading_list(self)
        elif self.initiator:
            self.validate_start_reading()
            book = Book.find_or_create(self)
            Reading.start(book)
        elif self.terminator:
            self.validate_end_reading()
            book = Book.find(self)
            Reading.end(book)
        elif self.ISBN and self.nick:
            self.validate_create_nick()
            Book.create_nick(self.nick)
        elif 'page' in dir(self) or 'percent' in dir(self):
            self.validate_create_bookmark()
            book = Book.find_or_create(self)
            reading = Reading.find(book, False)
            Bookmark.create_bookmark(reading, self.page_count)
        else:
            raise BadThing("Sorry, I don't understand your input")

    def convert_to_ISBN_13(self, original_ISBN):
        if len(original_ISBN) == 10:
            google_api_key = os.environ['GOOGLE_API_KEY']
            url = ("https://www.googleapis.com/books/v1/volumes"
                "?key={0}&country=GB&userIp=86.184.229.225"
                "&q=isbn:{1}").format(google_api_key, original_ISBN)
            bkdata = requests.get(url).json()
            volumedata = bkdata.get('items', [{}])[0].get('volumeInfo', {})
            ISBNs = bkdata['items'][0]['volumeInfo']['industryIdentifiers']
            for ISBN in ISBNs:
                if ISBN["type"] == 'ISBN_13':
                    return ISBN['identifier']
        return original_ISBN

    def validate_start_reading(self):
        # check there's actually an ISBN
        if not self.ISBN:
            raise BadThing("You need to include a 10 or 13 digit ISBN to "
                "start a book.")
        # check reading not already started
        book = Book.find(self)
        if Reading.find(book, False):
            raise BadThing("You've already started that book.")

    def validate_end_reading(self):
        # check that the book is in the DB
        book = Book.find(self)
        if not book:
            raise BadThing("You haven't started that book yet.")
        # check that there is an unfinished reading
        if not Reading.find(book, False):
            # if there's a finished reading, adjust error message
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
            last_bookmark = Bookmark.get_most_recent(reading).page
            page = Bookmark.get_pages(self, book)
            if last_bookmark > page:
                raise BadThing("You've already read this far.")


class BadThing(Exception):
    pass
