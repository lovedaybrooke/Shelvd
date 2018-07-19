import unittest
import datetime

from flask import Flask
from flask_testing import TestCase
from flask_sqlalchemy import SQLAlchemy

import shelvd.messages as messages
from shelvd.models import Book, Reading
from shelvd import db


class TestInstruction(TestCase):

    def create_app(self):
        app = Flask(__name__)
        app.config.from_object('shelvd.config.TestConfig')
        db = SQLAlchemy(app)
        return app

    def setUp(self):
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_parse_creates_new_book(self):
        messages.Instruction.process_incoming("9780111111111 start")
        look_up_book = Book.query.filter_by(isbn="9780111111111").all()
        self.assertTrue(len(look_up_book) == 1)
        self.assertEqual(look_up_book[0].isbn, "9780111111111")

    def test_parse_creates_new_book_with_uppercase_initiator(self):
        messages.Instruction.process_incoming("9780111111112 Start")
        look_up_book = Book.query.filter_by(isbn="9780111111112").all()
        self.assertTrue(len(look_up_book) == 1)
        self.assertEqual(look_up_book[0].isbn, "9780111111112")
    
    def test_parse_doesnt_create_existing_book(self):
        messages.Instruction.process_incoming("9780111111113 start")
        messages.Instruction.process_incoming("9780111111113 end")
        messages.Instruction.process_incoming("9780111111113 start")
        look_up_book = Book.query.filter_by(isbn="9780111111113").all()
        self.assertTrue(len(look_up_book) == 1)
        self.assertEqual(look_up_book[0].isbn, "9780111111113")

    # def test_finds_book_by_nickname(self):
        

    def test_parse_creates_readings_for_existing_book(self):
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

    def test_parse_creates_only_one_unfinished_reading(self):
        r1 = messages.Instruction.process_incoming("9780111111115 start")
        r2 = messages.Instruction.process_incoming("9780111111115 start")
        look_up_readings = Reading.query.filter_by(book_isbn="9780111111115"
            ).order_by(Reading.start_date.asc()).all()
        self.assertTrue(len(look_up_readings) == 1)
        self.assertEqual(r2, "You've already started reading this book")

    def test_parse_sets_reading_dates_correctly(self):
        messages.Instruction.process_incoming("9780111111116 start")
        
        look_up_reading = Reading.query.filter_by(book_isbn="9780111111116"
            ).first()
        self.assertTrue(hasattr(look_up_reading, 'start_date'))
        reading_start_date = look_up_reading.start_date

        look_up_book = Book.query.filter_by(isbn="9780111111116").first()
        self.assertTrue(hasattr(look_up_book, 'last_action_date'))
        book_action_date = look_up_book.last_action_date
        
        time_difference = book_action_date - reading_start_date
        self.assertTrue(time_difference < datetime.timedelta(0,1))

        messages.Instruction.process_incoming("9780111111116 end")
        self.assertTrue(hasattr(look_up_reading, 'end_date'))
        reading_end_date = look_up_reading.end_date
        self.assertTrue(reading_end_date > reading_start_date)



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
