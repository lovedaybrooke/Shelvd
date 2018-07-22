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


class TestInstruction(TestCase):

    def create_app(self):
        app = Flask(__name__)
        app.config.from_object(TestConfig)
        db = SQLAlchemy(app)
        return app

    def setUp(self):
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    @patch('shelvd.messages.Reply.send_reply')
    def test_parse_creates_new_book(self, mock_send_reply):
        messages.Instruction.process_incoming("9780111111111 start")
        look_up_book = Book.query.filter_by(isbn="9780111111111").all()
        self.assertTrue(len(look_up_book) == 1)
        self.assertEqual(look_up_book[0].isbn, "9780111111111")

    @patch('shelvd.messages.Reply.send_reply')
    def test_parse_creates_new_book_with_uppercase_initiator(self, mock_send_reply):
        mock_send_reply.return_value.ok = True
        messages.Instruction.process_incoming("9780111111112 Start")
        look_up_book = Book.query.filter_by(isbn="9780111111112").all()
        self.assertTrue(len(look_up_book) == 1)
        self.assertEqual(look_up_book[0].isbn, "9780111111112")
    
    @patch('shelvd.messages.Reply.send_reply')
    def test_parse_doesnt_create_existing_book(self, mock_send_reply):
        mock_send_reply.return_value.ok = True
        messages.Instruction.process_incoming("9780111111113 start")
        messages.Instruction.process_incoming("9780111111113 end")
        messages.Instruction.process_incoming("9780111111113 start")
        look_up_book = Book.query.filter_by(isbn="9780111111113").all()
        self.assertTrue(len(look_up_book) == 1)
        self.assertEqual(look_up_book[0].isbn, "9780111111113")

    # def test_finds_book_by_nickname(self):
        

    @patch('shelvd.messages.Reply.send_reply')
    def test_parse_creates_readings_for_existing_book(self, mock_send_reply):
        mock_send_reply.return_value.ok = True
        messages.Instruction.process_incoming("9780111111114 start")
        messages.Instruction.process_incoming("9780111111114 end")
        messages.Instruction.process_incoming("9780111111114 start")
        look_up_readings = Reading.query.filter_by(book_isbn="9780111111114"
            ).order_by(Reading.start_date.asc()).all()
        self.assertTrue(len(look_up_readings) == 2)
        self.assertEqual(look_up_readings[0].book_isbn, "9780111111114")
        self.assertEqual(look_up_readings[1].book_isbn, "9780111111114")
        self.assertTrue(look_up_readings[0].ended)
        self.assertFalse(look_up_readings[1].ended)

    @patch('shelvd.messages.Reply.send_reply')
    def test_parse_creates_only_one_unfinished_reading(self, mock_send_reply):
        mock_send_reply.return_value.ok = True
        r1 = messages.Instruction.process_incoming("9780111111115 start")
        r2 = messages.Instruction.process_incoming("9780111111115 start")
        look_up_readings = Reading.query.filter_by(book_isbn="9780111111115"
            ).order_by(Reading.start_date.asc()).all()
        self.assertTrue(len(look_up_readings) == 1)
        self.assertEqual(r2, ("You've already started reading this book", 400))

    @patch('shelvd.messages.Reply.send_reply')
    def test_parse_sets_reading_dates_correctly(self, mock_send_reply):
        mock_send_reply.return_value.ok = True
        messages.Instruction.process_incoming("9780111111116 start")
        
        reading = Reading.query.filter_by(book_isbn="9780111111116"
            ).first()
        self.assertTrue(hasattr(reading, 'start_date'))
        reading.start_date

        book = Book.query.filter_by(isbn="9780111111116").first()
        self.assertTrue(hasattr(book, 'last_action_date'))

        self.assertEqual(book.last_action_date, reading.start_date)

        messages.Instruction.process_incoming("9780111111116 end")
        reading = Reading.query.filter_by(book_isbn="9780111111116"
            ).first()
        book = Book.query.filter_by(isbn="9780111111116").first()
        
        self.assertTrue(hasattr(reading, 'end_date'))
        self.assertTrue(reading.end_date > reading.start_date)
        self.assertEqual(book.last_action_date, reading.end_date)

    #     # input = "9780111222333 Start"
    #     # r = messages.Instruction(input)
    #     # action = r.perform()
    #     # self.assertEqual(action[:21], "Started reading book ")

    #     # input = "ducktales start"
    #     # r = messages.Instruction(input)
    #     # action = r.perform()
    #     # self.assertEqual(action[:21, "Started reading book ")

    #     input = "9780111222333 ducktales"
    #     r = messages.Instruction.process_incoming(input)
    #     self.assertEqual(r, "Nickname this book")

    #     input = "9780111222333 duck tales"
    #     r = messages.Instruction.process_incoming(input)
    #     self.assertEqual(r, "Sorry, your message is too long")

    #     input = "9780111222333 abandon"
    #     r = messages.Instruction.process_incoming(input)
    #     self.assertEqual(r, "Finish reading this book")

    #     input = "9780111222333 Finish"
    #     r = messages.Instruction.process_incoming(input)
    #     self.assertEqual(r, "Finish reading this book")

    #     input = "duck duck duck"
    #     r = messages.Instruction.process_incoming(input)
    #     self.assertEqual(r, "Sorry, your message is too long")

    #     input = "9870122122 start"
    #     r = messages.Instruction.process_incoming(input)
    #     self.assertEqual(r, "Sorry, I didn't understand your message")

if __name__ == '__main__':
    unittest.main()
