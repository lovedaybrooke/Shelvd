import unittest
from unittest.mock import patch
import datetime

from flask import Flask
from flask_testing import TestCase
from flask_sqlalchemy import SQLAlchemy

from shelvd.models import Book, Reading, Author, MessageException
from shelvd import db
from shelvd.config import TestConfig
from . import factories


class TestBook(TestCase):

    def create_app(self):
        app = Flask(__name__)
        app.config.from_object(TestConfig)
        db = SQLAlchemy(app)
        return app

    def setUp(self):
        db.create_all()
        factories.create_objects_for_models_testing(db)

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_find_or_create_on_existing_book(self):
        all_books_with_this_isbn = Book.query.filter_by(
                                   isbn="9780111111113").all()
        self.assertEqual(len(all_books_with_this_isbn), 1)
        message = factories.FakeMessage()
        message.isbn = "9780111111113"
        book = Book.find_or_create(message)
        self.assertEqual(type(book), Book)
        self.assertEqual(book.isbn, "9780111111113")
        self.assertEqual(book.title, "Necronomicon (not a real book)")
        all_books_with_this_isbn = Book.query.filter_by(
                                   isbn="9780111111113").all()
        self.assertEqual(len(all_books_with_this_isbn), 1)

    @patch("shelvd.models.Book.get_amazon_data")
    def test_find_or_create_on_new_book(self, mock_get_amazon_data):
        message = factories.FakeMessage()
        message.isbn = "9780111111118"
        all_books_with_this_isbn = Book.query.filter_by(
                                   isbn="9780111111118").all()
        self.assertFalse(all_books_with_this_isbn)
        book = Book.find_or_create(message)
        all_books_with_this_isbn = Book.query.filter_by(
                                   isbn="9780111111118").all()
        self.assertEqual(len(all_books_with_this_isbn), 1)

    def test_find_unknown_book_using_nickname(self):
        message = factories.FakeMessage()
        message.nickname = "Dogs"
        message.isbn = False
        with self.assertRaises(MessageException):
            Book.find(message)

    def test_find_unknown_book_using_isbn(self):
        message = factories.FakeMessage()
        message.isbn = "9780111111119"
        book = Book.find(message)
        self.assertFalse(book)

    def test_find_existing_book_using_nickname(self):
        message = factories.FakeMessage()
        message.isbn = False
        message.nickname = "YKing"
        book = Book.find(message)
        self.assertTrue(book)
        self.assertEqual(type(book), Book)
        self.assertEqual(book.isbn, "9780111111114")

    def test_find_existing_book_using_isbn(self):
        message = factories.FakeMessage()
        message.isbn = "9780111111113"
        book = Book.find(message)
        self.assertTrue(book)
        self.assertEqual(type(book), Book)
        self.assertEqual(book.title, "Necronomicon (not a real book)")

    @patch("shelvd.models.AmazonAPI.lookup", factories.mock_amazon_lookup)
    def test_create(self):
        message = factories.FakeMessage()
        message.isbn = "9780241341629"
        book = Book.create(message)
        self.assertTrue(book)
        self.assertEqual(type(book), Book)
        self.assertEqual(book.title, "Not Ghost Stories")
        self.assertEqual(book.isbn, "9780241341629")

    def test_set_nickname_with_already_used_nickname(self):
        message = factories.FakeMessage()
        message.isbn = "9780111111113"
        message.nickname = "YKing"
        book = Book.query.filter_by(isbn="9780111111113").first()
        with self.assertRaises(MessageException):
            book.set_nickname(message)

    def test_set_nickname_with_a_new_nickname(self):
        message = factories.FakeMessage()
        message.isbn = "9780111111121"
        message.nickname = "YellowKing"
        book = Book.query.filter_by(isbn="9780111111113").first()
        book.set_nickname(message)
        all_books_with_this_nickname = Book.query.filter_by(
                                   nickname="YellowKing").all()
        self.assertEqual(len(all_books_with_this_nickname), 1)
        self.assertEqual(all_books_with_this_nickname[0].nickname,
                         "YellowKing")

    def test_set_nickname_with_unsaved_book(self):
        book = Book()
        book.isbn = '9780111111120'
        message = factories.FakeMessage()
        message.isbn = "9780111111120"
        message.nickname = "YellowKing"
        all_books_with_this_nickname = Book.query.filter_by(
                                   nickname="YellowKing").all()
        self.assertEqual(len(all_books_with_this_nickname), 0)
        book.set_nickname(message)
        all_books_with_this_nickname = Book.query.filter_by(
                                   nickname="YellowKing").all()
        self.assertEqual(len(all_books_with_this_nickname), 1)

    @patch("shelvd.models.AmazonAPI.lookup", factories.mock_amazon_lookup)
    def test_get_amazon_data_with_multiple_authors(self):
        book = Book()
        book.isbn = "9780000000666"
        book.get_amazon_data()
        self.assertEqual(book.title, "Especially Violent Fairytales")
        self.assertEqual(book.page_count, 620)
        self.assertEqual(sorted([author.name for author
                         in book.authors]),
                         ["D. Grimmer", "T. Grimmer"])

    @patch("shelvd.models.AmazonAPI.lookup", factories.mock_amazon_lookup)
    def test_get_amazon_data_with_one_author(self):
        book = Book()
        book.isbn = "9780000000777"
        book.get_amazon_data()
        self.assertEqual(book.title, "Mysterious Semi-known Book")
        self.assertEqual(book.page_count, 280)
        self.assertEqual([author.name for author in book.authors],
                         ["A. N. Author"])

    @patch("shelvd.models.AmazonAPI.lookup", factories.mock_amazon_lookup)
    def test_get_amazon_data_with_no_author(self):
        book = Book()
        book.isbn = "9780000000888"
        book.get_amazon_data()
        self.assertEqual(book.title, "Mysterious Unknown Book")
        self.assertEqual(book.page_count, 260)
        self.assertEqual([author for author in book.authors], [])

    @patch("shelvd.models.AmazonAPI.lookup", factories.mock_amazon_lookup)
    def test_get_amazon_data_with_many_to_many_author_book_relations(self):
        book_1 = Book()
        book_1.isbn = "9780241341629"
        book_1.get_amazon_data()
        book_2 = Book()
        book_2.isbn = "9780000000666"
        book_2.get_amazon_data()
        look_up_author = Author.query.filter_by(name="Ghost Author").all()
        self.assertEqual(len(look_up_author), 1)
        self.assertEqual(sorted([author.name for author in book_1.authors]),
                         ["Ghost Author", "R. M. James"])
        self.assertEqual(sorted([author.name for author in book_2.authors]),
                         ['D. Grimmer', 'Ghost Author'])
        
        

class TestReading(TestCase):

    def create_app(self):
        app = Flask(__name__)
        app.config.from_object(TestConfig)
        db = SQLAlchemy(app)
        return app

    def setUp(self):
        db.create_all()
        factories.create_objects_for_models_testing(db)

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    @patch("shelvd.models.Book.get_amazon_data")
    def test_start_reading_of_new_book(self, mock_get_amazon_data):
        message = factories.FakeMessage()
        message.isbn = "9780111111121"
        reading = Reading.start_reading(message)
        look_up_reading = Reading.query.filter_by(
                          book_isbn="9780111111121").all()
        self.assertEqual(len(look_up_reading), 1)
        self.assertEqual(look_up_reading[0].book_isbn, "9780111111121")
        self.assertTrue(look_up_reading[0].start_date)
        self.assertFalse(look_up_reading[0].end_date)
        self.assertFalse(look_up_reading[0].ended)
        self.assertFalse(look_up_reading[0].abandoned)

    @patch("shelvd.models.Book.get_amazon_data")
    def test_start_reading_of_existing_book(self, mock_get_amazon_data):
        message = factories.FakeMessage()
        message.isbn = "9780111111188"
        reading = Reading.start_reading(message)
        look_up_reading = Reading.query.filter_by(
                          book_isbn="9780111111188").all()
        self.assertEqual(len(look_up_reading), 1)
        self.assertEqual(look_up_reading[0].book_isbn, "9780111111188")
        self.assertTrue(look_up_reading[0].start_date)
        self.assertFalse(look_up_reading[0].end_date)
        self.assertFalse(look_up_reading[0].ended)
        self.assertFalse(look_up_reading[0].abandoned)

    @patch("shelvd.models.Book.get_amazon_data")
    def test_start_reading_when_unfinished_reading_exists(self,
                                                          mock_get_amazon_data):
        look_up_reading = Reading.query.filter_by(
                          book_isbn="9780111111114").filter_by(
                          ended=False).all()
        self.assertEqual(len(look_up_reading), 1)
        message = factories.FakeMessage()
        message.isbn = "9780111111114"
        with self.assertRaises(MessageException):
            Reading.start_reading(message)
        look_up_reading = Reading.query.filter_by(
                          book_isbn="9780111111114").filter_by(
                          ended=False).all()
        self.assertEqual(len(look_up_reading), 1)

    @patch("shelvd.models.Book.get_amazon_data")
    def test_start_reading_when_ended_reading_exists(self,
                                                     mock_get_amazon_data):
        look_up_reading = Reading.query.filter_by(
                          book_isbn="9780111111113").filter_by(
                          ended=True).all()
        self.assertEqual(len(look_up_reading), 2)
        message = factories.FakeMessage()
        message.isbn = "9780111111113"
        Reading.start_reading(message)
        look_up_reading = Reading.query.filter_by(
                          book_isbn="9780111111113").order_by(
                          Reading.start_date.asc()).all()
        self.assertEqual(len(look_up_reading), 3)
        self.assertTrue(look_up_reading[0].ended)
        self.assertTrue(look_up_reading[1].ended)
        self.assertFalse(look_up_reading[2].ended)

    def test_end_reading_of_existing_book(self):
        message = factories.FakeMessage()
        message.isbn = "9780111111114"
        message.terminator = "end"
        reading_response = Reading.end_reading(message)
        self.assertEqual(reading_response, "Finished reading The King in "
                         "Yellow: various stories (ISBN 9780111111114)")
        look_up_reading = Reading.query.filter_by(
                          book_isbn="9780111111114").all()
        self.assertEqual(len(look_up_reading), 1)
        self.assertTrue(look_up_reading[0].ended)

    def test_end_reading_of_new_book(self):
        message = factories.FakeMessage()
        message.isbn = "9780111111122"
        message.terminator = "end"
        with self.assertRaises(MessageException):
            Reading.end_reading(message)
        look_up_reading = Reading.query.filter_by(
                          book_isbn="9780111111122").all()
        self.assertEqual(len(look_up_reading), 0)

    def test_end_reading_when_no_unended_reading(self):
        look_up_reading = Reading.query.filter_by(
                          book_isbn="9780111111113").all()
        self.assertEqual(len(look_up_reading), 2)
        self.assertTrue(look_up_reading[0].ended)
        message = factories.FakeMessage()
        message.isbn = "9780111111113"
        message.terminator = "end"
        with self.assertRaises(MessageException):
            Reading.end_reading(message)
        look_up_reading = Reading.query.filter_by(
                          book_isbn="9780111111113").all()
        self.assertEqual(len(look_up_reading), 2)
        self.assertTrue(look_up_reading[0].ended)


class TestAuthor(TestCase):

    def create_app(self):
        app = Flask(__name__)
        app.config.from_object(TestConfig)
        db = SQLAlchemy(app)
        return app

    def setUp(self):
        db.create_all()
        factories.create_objects_for_models_testing(db)

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_find_or_create_existing_author_by_name(self):
        look_up_author = Author.query.filter_by(name="R. M. James").all()
        self.assertEqual(len(look_up_author), 1)
        author = Author.find_or_create("R. M. James")
        look_up_author = Author.query.filter_by(name="R. M. James").all()
        self.assertEqual(len(look_up_author), 1)
        self.assertEqual(author.id, 1001)

    def test_find_or_create_existing_author_by_id(self):
        look_up_author = Author.query.filter_by(id=1001).all()
        self.assertEqual(len(look_up_author), 1)
        author = Author.find_or_create(1001)
        look_up_author = Author.query.filter_by(id=1001).all()
        self.assertEqual(len(look_up_author), 1)
        self.assertEqual(author.id, 1001)

    def test_find_or_create_new_author_by_name(self):
        look_up_author = Author.query.filter_by(name="Mary Shelley").all()
        self.assertEqual(len(look_up_author), 0)
        Author.find_or_create("Mary Shelley")
        look_up_author = Author.query.filter_by(name="Mary Shelley").all()
        self.assertEqual(len(look_up_author), 1)

    def test_create_from_amazon_data_with_multiple_authors(self):
        fake_book_object = factories.mock_amazon_lookup(ItemId="9780000000666")
        Author.create_from_amazon_data(fake_book_object)
        look_up_author = Author.query.filter_by(name="D. Grimmer").all()
        self.assertEqual(len(look_up_author), 1)
        look_up_author = Author.query.filter_by(name="T. Grimmer").all()
        self.assertEqual(len(look_up_author), 1)

    def test_create_from_amazon_data_with_one_author(self):
        fake_book_object = factories.mock_amazon_lookup(ItemId="9780000000777")
        Author.create_from_amazon_data(fake_book_object)
        look_up_author = Author.query.filter_by(name="A. N. Author").all()
        self.assertEqual(len(look_up_author), 1)

    def test_create_from_amazon_data_with_no_authors(self):
        fake_book_object = factories.mock_amazon_lookup(ItemId="9780000000888")
        authors = Author.create_from_amazon_data(fake_book_object)
        self.assertFalse(authors)
