import unittest
from unittest.mock import Mock, patch
import datetime

from flask import Flask
from flask_testing import TestCase
from flask_sqlalchemy import SQLAlchemy

import shelvd.messages as messages
from shelvd.models import Book, Reading, Author
from shelvd import db
from shelvd.config import TestConfig

from . import factories as factories


class TestInstruction(TestCase):

    def create_app(self):
        app = Flask(__name__)
        app.config.from_object(TestConfig)
        db = SQLAlchemy(app)
        return app

    def setUp(self):
        db.create_all()
        factories.create_objects_for_message_testing(db)

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    @patch("shelvd.messages.Reply.send_reply")
    @patch("shelvd.models.Book.get_api_data")
    def test_parse_creates_new_book(self, mock_send_reply,
                                    mock_get_api_data):  
        messages.Instruction.process_incoming("9780111111111 start")
        look_up_book = Book.query.filter_by(isbn="9780111111111").all()
        self.assertTrue(len(look_up_book) == 1)

    @patch("shelvd.messages.Reply.send_reply")
    @patch("shelvd.models.Book.call_bookdata_api", factories.mock_api_lookup)
    def test_parse_assigns_attributes_to_new_book(self, mock_send_reply):
        messages.Instruction.process_incoming("9780241341629 start")
        book = Book.query.filter_by(isbn="9780241341629").first()
        self.assertTrue(hasattr(book, "title"))
        self.assertEqual(book.title, "Not Ghost Stories")
        self.assertTrue(hasattr(book, "page_count"))
        self.assertEqual(book.page_count, 380)
        self.assertTrue(hasattr(book, "authors"))
        author_names = [author.name for author in book.authors]
        self.assertEqual(sorted(author_names), ["Ghost Author", "R. M. James"])
        # check the author that needed to be created was created
        newly_created_author = Author.query.filter_by(name="Ghost Author").all()
        self.assertEqual(len(newly_created_author), 1)

    @patch("shelvd.messages.Reply.send_reply")
    @patch("shelvd.models.Book.call_bookdata_api", factories.mock_api_lookup)
    def test_parse_on_muany_to_many_relationships(self, mock_send_reply):
        messages.Instruction.process_incoming("9780241341629 start")
        messages.Instruction.process_incoming("9780000000666 start")
        book_1 = Book.query.filter_by(isbn="9780241341629").first()
        book_2 = Book.query.filter_by(isbn="9780000000666").first()
        self.assertEqual(sorted([author.name for author in book_1.authors]),
                         ["Ghost Author", "R. M. James"])
        self.assertEqual(sorted([author.name for author in book_2.authors]),
                         ['D. Grimmer', 'Ghost Author'])

    @patch("shelvd.messages.Reply.send_reply")
    @patch("shelvd.models.Book.call_bookdata_api", factories.mock_api_lookup)
    def test_parse_handles_books_amazon_doesnt_know_about(self, mock_send_reply):
        messages.Instruction.process_incoming("0879111111111 start")
        book = Book.query.filter_by(isbn="0879111111111").first()
        self.assertTrue(hasattr(book, "title"))
        self.assertEqual(book.title, "Unknown")
        self.assertTrue(hasattr(book, "page_count"))
        self.assertEqual(book.page_count, 350)
        author_names = [author.name for author in book.authors]
        self.assertEqual(author_names, ["Unknown"])

    @patch("shelvd.messages.Reply.send_reply")
    def test_parse_doesnt_create_existing_book(self, mock_send_reply):
        # this book should have been created by Factory Boy
        look_up_book = Book.query.filter_by(isbn="9780111111113").all()
        self.assertTrue(len(look_up_book) == 1)
        # Now when a reading is started, no new book should be created
        messages.Instruction.process_incoming("9780111111113 start")
        look_up_book = Book.query.filter_by(isbn="9780111111113").all()
        self.assertTrue(len(look_up_book) == 1)

    @patch("shelvd.messages.Reply.send_reply")
    def test_parse_attempting_to_create_book_with_nickname(self,
                                                           mock_send_reply):
        mock_send_reply.return_value = ("This nickname doesn't match a book "
            "that I know about already. Use an ISBN to start reading a brand "
            "new book.", 400)
        r1 = messages.Instruction.process_incoming("Namenick start")
        look_up_book = Book.query.filter_by(nickname="Namenick").all()
        self.assertFalse(look_up_book)
        self.assertEqual(r1, ("This nickname doesn't match a book "
            "that I know about already. Use an ISBN to start reading a brand "
            "new book.", 400))

    @patch("shelvd.messages.Reply.send_reply")
    @patch("shelvd.models.Book.get_api_data")
    def test_parse_creates_reading_for_new_book(self, mock_send_reply,
                                                mock_get_api_data):
        look_up_book = Book.query.filter_by(isbn="9780111111115").all()
        self.assertTrue(len(look_up_book) == 0)
        messages.Instruction.process_incoming("9780111111115 start")
        look_up_readings = Reading.query.filter_by(book_isbn="9780111111115"
                                                   ).all()
        self.assertTrue(len(look_up_readings) == 1)
        self.assertFalse(look_up_readings[0].ended)
        self.assertFalse(look_up_readings[0].abandoned)
        self.assertFalse(look_up_readings[0].end_date)

    @patch("shelvd.messages.Reply.send_reply")
    def test_parse_creates_readings_for_existing_book(self, mock_send_reply):
        # this book should have been created by Factory Boy
        look_up_book = Book.query.filter_by(isbn="9780111111113").all()
        self.assertTrue(len(look_up_book) == 1)
        messages.Instruction.process_incoming("9780111111113 start")
        look_up_readings = Reading.query.filter_by(book_isbn="9780111111113"
                           ).order_by(Reading.start_date.asc()).all()
        self.assertTrue(len(look_up_readings) == 2)
        self.assertTrue(look_up_readings[0].ended)
        self.assertTrue(look_up_readings[0].end_date)
        self.assertFalse(look_up_readings[1].ended)
        self.assertFalse(look_up_readings[1].end_date)

    @patch("shelvd.messages.Reply.send_reply")
    @patch("shelvd.models.Book.get_api_data")
    def test_parse_creates_only_one_unfinished_reading(self, mock_send_reply,
                                                       mock_get_api_data):
        r1 = messages.Instruction.process_incoming("9780111111115 start")
        r2 = messages.Instruction.process_incoming("9780111111115 start")
        look_up_readings = Reading.query.filter_by(book_isbn="9780111111115"
                           ).order_by(Reading.start_date.asc()).all()
        self.assertTrue(len(look_up_readings) == 1)
        self.assertEqual(r2, ("You've already started reading this book", 400))

    @patch("shelvd.messages.Reply.send_reply")
    def test_parse_doesnt_end_reading_that_isnt_started(self, mock_send_reply):
        r = messages.Instruction.process_incoming("9780111111115 end")
        look_up_readings = Reading.query.filter_by(book_isbn="9780111111115"
                           ).order_by(Reading.start_date.asc()).all()
        self.assertFalse(look_up_readings)
        self.assertEqual(r, ("You're not currently reading this book. You "
            "need to start reading this book before you finish it.", 400))

    @patch("shelvd.messages.Reply.send_reply")
    @patch("shelvd.models.Book.get_api_data")
    def test_parse_sets_reading_dates_correctly(self, mock_send_reply,
                                                mock_get_api_data):
        messages.Instruction.process_incoming("9780111111116 start")

        reading = Reading.query.filter_by(book_isbn="9780111111116"
                  ).first()
        self.assertTrue(hasattr(reading, "start_date"))
        book = Book.query.filter_by(isbn="9780111111116").first()
        self.assertTrue(hasattr(book, "last_action_date"))
        self.assertEqual(book.last_action_date, reading.start_date)

        messages.Instruction.process_incoming("9780111111116 end")
        reading = Reading.query.filter_by(book_isbn="9780111111116"
                  ).first()
        book = Book.query.filter_by(isbn="9780111111116").first()
        self.assertTrue(hasattr(reading, "end_date"))
        self.assertTrue(reading.end_date > reading.start_date)
        self.assertEqual(book.last_action_date, reading.end_date)

    @patch("shelvd.messages.Reply.send_reply")
    def test_setting_nickname(self, mock_send_reply):
        messages.Instruction.process_incoming("9780111111113 Necro")
        look_up_book = Book.query.filter_by(nickname="Necro").all()
        self.assertTrue(len(look_up_book) == 1)

    @patch("shelvd.messages.Reply.send_reply")
    def test_setting_nickname_of_multiple_words(self, mock_send_reply):
        r = messages.Instruction.process_incoming("9780111111113 Necro book")
        look_up_book_1 = Book.query.filter_by(nickname="Necro book").all()
        self.assertFalse(look_up_book_1)
        look_up_book_2 = Book.query.filter_by(nickname="Necro").all()
        self.assertFalse(look_up_book_2)
        self.assertEqual(r, ("Sorry, your message is too long. Remember that "
            "nicknames cannot include spaces", 400))

    @patch("shelvd.messages.Reply.send_reply")
    def test_setting_existing_nickname(self, mock_send_reply):
        look_up_book = Book.query.filter_by(nickname="YKing").all()
        self.assertTrue(len(look_up_book) == 1)

        r = messages.Instruction.process_incoming("9780111111113 YKing")
        self.assertEqual(r,
            ("This nickname has already been used. Try another.", 400))

        look_up_book = Book.query.filter_by(nickname="YKing").all()
        self.assertTrue(len(look_up_book) == 1)

    @patch("shelvd.messages.Reply.send_reply")
    def test_setting_nickname_for_unstarted_book(self, mock_send_reply):
        r = messages.Instruction.process_incoming("9780888888888 YKing")
        self.assertEqual(r,
                         ("You haven't started reading this book yet. You "
                          "need to start it before nicknaming it.", 400))
        look_up_book = Book.query.filter_by(isbn="9780888888888").all()
        self.assertEqual(len(look_up_book), 0)


if __name__ == "__main__":
    unittest.main()
