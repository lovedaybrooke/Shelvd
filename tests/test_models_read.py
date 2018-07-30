import collections
from flask import Flask
from flask_testing import TestCase
from flask_sqlalchemy import SQLAlchemy

from shelvd.models import Reading, Book
from shelvd.config import TestConfig
from shelvd import db
from . import factories


class TestReading(TestCase):

    def create_app(self):
        app = Flask(__name__)
        app.config.from_object(TestConfig)
        db = SQLAlchemy(app)
        return app

    def setUp(self):
        db.create_all()
        factories.create_objects_for_models_testing(db)

    def tearDown(all):
        db.session.remove()
        db.drop_all()

    def test_get_reading_list_unfinished(self):
        readings = Reading.get_reading_list(False, False)
        self.assertEqual(len(readings), 2)
        self.assertEqual(["{0} ({1})".format(
                         reading.book.title, reading.start_date)
                         for reading in readings],
                         ["The King in Yellow: various stories "
                            "(2017-02-01 00:00:00)",
                         "Ghost Stories of Antiquarians IE History Fans "
                            "(2016-04-01 00:00:00)"])

    def test_get_reading_list_finished(self):
        readings = Reading.get_reading_list(True, False)
        self.assertEqual(len(readings), 2)
        self.assertEqual(["{0} ({1})".format(
                         reading.book.title, reading.end_date)
                         for reading in readings],
                         ["Necronomicon (not a real book) "
                            "(2017-01-05 00:00:00)",
                          "Ghost Stories of Antiquarians IE History Fans "
                            "(2016-03-09 00:00:00)"])

    def test_get_reading_list_abandoned(self):
        readings = Reading.get_reading_list(True, True)
        self.assertEqual(["{0} ({1})".format(
                         reading.book.title, reading.end_date)
                         for reading in readings],
                         ["Necronomicon (not a real book) "
                            "(2016-01-10 00:00:00)"])

    def test_get_reading_list_finished_by_year(self):
        readings = Reading.get_reading_list(True, False, 2016)
        formatted_list = ["{0} ({1})".format(
                         reading.book.title, reading.end_date)
                         for reading in readings]
        self.assertEqual(formatted_list,
                         ["Ghost Stories of Antiquarians IE History Fans "
                            "(2016-03-09 00:00:00)"])

    def test_get_reading_list_year_by_year(self):
        reading_list = Reading.get_year_by_year_reading_list()
        self.assertEqual(len(reading_list), 3)
        self.assertEqual(reading_list[2018]["book_count"], 0)
        self.assertFalse(reading_list[2018]["books_read"])
        self.assertEqual(reading_list[2017]["book_count"], 1)
        self.assertEqual(len(reading_list[2017]["books_read"]), 1)
        self.assertEqual(
            [reading.book.isbn for reading in reading_list[2017]["books_read"]],
            ["9780111111113"])
        self.assertEqual(reading_list[2016]["book_count"], 1)
        self.assertEqual(len(reading_list[2016]["books_read"]), 1)
        self.assertEqual(
            [reading.book.isbn for reading in reading_list[2016]["books_read"]],
            ["9780111111333"])


class TestBook(TestCase):

    def create_app(self):
        app = Flask(__name__)
        app.config.from_object(TestConfig)
        db = SQLAlchemy(app)
        return app

    def setUp(self):
        db.create_all()
        factories.create_objects_for_models_testing(db)

    def tearDown(all):
        db.session.remove()
        db.drop_all()

    def test_curtail_title(self):
        books = [book.curtail_title() for book in Book.query.all()]
        self.assertEqual(sorted(books), 
                         ["Ghost Stories of Antiquarians IE...",
                         "Necronomicon",
                         "Oh, Whistle, and I'll Come Laddie...",
                         "The King in Yellow",
                         "The Yellow Wallpaper"])
