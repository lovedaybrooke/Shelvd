import unittest
from unittest.mock import Mock, patch
import datetime

from flask import Flask
from flask_testing import TestCase
from flask_sqlalchemy import SQLAlchemy

import shelvd.messages as messages
from shelvd.models import Book, Reading
from shelvd import db
from shelvd.config import TestConfig

from . import factories


def create_objects(db):
    b1 = factories.BookFactory(
        isbn="9780111111113",
        title="Necronomicon"
    )
    r1 = factories.ReadingFactory(
        book_isbn=b1.isbn,
        start_date=datetime.datetime(2017, 1, 1),
        ended=True
    )
    db.session.add(b1)
    db.session.add(r1)
    db.session.commit()

class TestInstruction(TestCase):

    def create_app(self):
        app = Flask(__name__)
        app.config.from_object(TestConfig)
        db = SQLAlchemy(app)
        return app

    def setUp(self):
        db.create_all()
        create_objects(db)

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    @patch("shelvd.messages.Reply.send_reply")
    def test_parse_creates_new_book(self, mock_send_reply):
        messages.Instruction.process_incoming("9780111111111 start")
        look_up_book = Book.query.filter_by(isbn="9780111111111").all()
        self.assertTrue(len(look_up_book) == 1)

    @patch("shelvd.messages.Reply.send_reply")
    def test_parse_creates_new_book_with_uppercase_initiator(self, mock_send_reply):
        mock_send_reply.return_value.ok = True
        messages.Instruction.process_incoming("9780111111112 Start")
        look_up_book = Book.query.filter_by(isbn="9780111111112").all()
        self.assertTrue(len(look_up_book) == 1)
    
    @patch("shelvd.messages.Reply.send_reply")
    def test_parse_doesnt_create_existing_book(self, mock_send_reply):
        mock_send_reply.return_value.ok = True
        # this book should have been created by Factory Boy
        look_up_book = Book.query.filter_by(isbn="9780111111113").all()
        self.assertTrue(len(look_up_book) == 1)
        # Now when a reading is started, no new book should be created
        messages.Instruction.process_incoming("9780111111113 start")
        look_up_book = Book.query.filter_by(isbn="9780111111113").all()
        self.assertTrue(len(look_up_book) == 1)

    @patch("shelvd.messages.Reply.send_reply")
    def test_parse_attempting_to_create_book_with_nickname(self, mock_send_reply):
        mock_send_reply.return_value.ok = ("This nickname doesn't match a book "
            "that I know about already. Use an ISBN to start reading a brand "
            "new book.", 400)
        r1 = messages.Instruction.process_incoming("Namenick start")
        look_up_book = Book.query.filter_by(nickname="Namenick").all()
        self.assertFalse(look_up_book)
        self.assertEqual(r1, ("This nickname doesn't match a book "
            "that I know about already. Use an ISBN to start reading a brand "
            "new book.", 400))

    @patch("shelvd.messages.Reply.send_reply")
    def test_parse_creates_readings_for_existing_book(self, mock_send_reply):
        mock_send_reply.return_value.ok = True
        # this book should have been created by Factory Boy
        look_up_book = Book.query.filter_by(isbn="9780111111113").all()
        self.assertTrue(len(look_up_book) == 1)
        messages.Instruction.process_incoming("9780111111113 start")
        look_up_readings = Reading.query.filter_by(book_isbn="9780111111113"
            ).order_by(Reading.start_date.asc()).all()
        self.assertTrue(len(look_up_readings) == 2)
        self.assertTrue(look_up_readings[0].ended)
        self.assertFalse(look_up_readings[1].ended)

    @patch("shelvd.messages.Reply.send_reply")
    def test_parse_creates_only_one_unfinished_reading(self, mock_send_reply):
        mock_send_reply.return_value.ok = True
        r1 = messages.Instruction.process_incoming("9780111111115 start")
        r2 = messages.Instruction.process_incoming("9780111111115 start")
        look_up_readings = Reading.query.filter_by(book_isbn="9780111111115"
            ).order_by(Reading.start_date.asc()).all()
        self.assertTrue(len(look_up_readings) == 1)
        self.assertEqual(r2, ("You've already started reading this book", 400))

    @patch("shelvd.messages.Reply.send_reply")
    def test_parse_sets_reading_dates_correctly(self, mock_send_reply):
        mock_send_reply.return_value.ok = True
        messages.Instruction.process_incoming("9780111111116 start")
        
        reading = Reading.query.filter_by(book_isbn="9780111111116"
            ).first()
        self.assertTrue(hasattr(reading, "start_date"))
        reading.start_date

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
        mock_send_reply.return_value.ok = True
        messages.Instruction.process_incoming("9780111111113 Necro")
        look_up_book = Book.query.filter_by(nickname="Necro").all()
        self.assertTrue(len(look_up_book) == 1)

    @patch("shelvd.messages.Reply.send_reply")
    def test_setting_nickname_of_multiple_words(self, mock_send_reply):
        mock_send_reply.return_value.ok = True
        r = messages.Instruction.process_incoming("9780111111113 Necro book")
        look_up_book_1 = Book.query.filter_by(nickname="Necro book").all()
        self.assertFalse(look_up_book_1)
        look_up_book_2 = Book.query.filter_by(nickname="Necro").all()
        self.assertFalse(look_up_book_2)
        self.assertEqual(r, ("Sorry, your message is too long. Remember that "
            "nicknames cannot include spaces", 400))



if __name__ == "__main__":
    unittest.main()
