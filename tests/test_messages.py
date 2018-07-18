import unittest

from flask import Flask
from flask_testing import TestCase

import shelvd.messages as messages


class TestInstruction(TestCase):
    def create_app(self):
        app = Flask(__name__)
        app.config['TESTING'] = True
        return app

    def test_imcoming_message_triage(self):
        # Need to change these tests so they run on a dummy DB

        # input = "9780111222333 start"
        # r = messages.Instruction(input)
        # action = r.perform()
        # self.assertEqual(action[:21], "Started reading book ")

        # input = "9780111222333 Start"
        # r = messages.Instruction(input)
        # action = r.perform()
        # self.assertEqual(action[:21], "Started reading book ")

        # input = "ducktales start"
        # r = messages.Instruction(input)
        # action = r.perform()
        # self.assertEqual(action[:21, "Started reading book ")

        input = "9780111222333 ducktales"
        r = messages.Instruction.process_incoming(input)
        self.assertEqual(r, "Nickname this book")

        input = "9780111222333 duck tales"
        r = messages.Instruction.process_incoming(input)
        self.assertEqual(r, "Sorry, your message is too long")

        input = "9780111222333 abandon"
        r = messages.Instruction.process_incoming(input)
        self.assertEqual(r, "Finish reading this book")

        input = "9780111222333 Finish"
        r = messages.Instruction.process_incoming(input)
        self.assertEqual(r, "Finish reading this book")

        input = "duck duck duck"
        r = messages.Instruction.process_incoming(input)
        self.assertEqual(r, "Sorry, your message is too long")

        input = "9870122122 start"
        r = messages.Instruction.process_incoming(input)
        self.assertEqual(r, "Sorry, I didn't understand your message")

if __name__ == '__main__':
    unittest.main()
