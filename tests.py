import unittest

from flask import Flask
from flask_testing import TestCase

import shelvd.grammar as grammar
import shelvd.messages as messages


# run from root with python tests.py

class TestGrammar(TestCase):

    def create_app(self):
        app = Flask(__name__)
        app.config['TESTING'] = True
        return app

    def test_grammar_initiators(self):
        inputs = "9780111222333 start"
        results = grammar.expression.parseString(inputs)

        self.assertTrue("isbn" in results.keys())
        self.assertTrue("initiator" in results.keys())
        self.assertFalse("nickname" in results.keys())
        self.assertEqual(results["isbn"], "9780111222333")
        self.assertEqual(results["initiator"], "start")

        inputs = "Namenick begin"
        results = grammar.expression.parseString(inputs)
        self.assertTrue("nickname" in results.keys())
        self.assertEqual(results["nickname"], "Namenick")
        self.assertTrue("initiator" in results.keys())
        self.assertEqual(results["initiator"], "begin")

    def test_grammar_terminators(self):
        inputs = "9780111222333 end"
        results = grammar.expression.parseString(inputs)

        self.assertTrue("isbn" in results.keys())
        self.assertTrue("terminator" in results.keys())
        self.assertFalse("nickname" in results.keys())
        self.assertEqual(results["isbn"], "9780111222333")
        self.assertEqual(results["terminator"], "end")

        inputs = "Namenick finish"
        results = grammar.expression.parseString(inputs)
        self.assertTrue("nickname" in results.keys())
        self.assertEqual(results["nickname"], "Namenick")
        self.assertTrue("terminator" in results.keys())
        self.assertEqual(results["terminator"], "finish")

        inputs = "Namenick abandon"
        results = grammar.expression.parseString(inputs)
        self.assertTrue("nickname" in results.keys())
        self.assertEqual(results["nickname"], "Namenick")
        self.assertTrue("terminator" in results.keys())
        self.assertEqual(results["terminator"], "abandon")

    def test_grammar_nicknaming(self):
        inputs = "9780111222333 KingInYellow"
        results = grammar.expression.parseString(inputs)

        self.assertTrue("isbn" in results.keys())
        self.assertEqual(results["isbn"], "9780111222333")
        self.assertTrue("nickname" in results.keys())
        self.assertEqual(results["nickname"], "KingInYellow")

        # inputs = "9780111222333 King In Yellow"
        # results = grammar.expression.parseString(inputs)

        # self.assertTrue("isbn" in results.keys())
        # self.assertEqual(results["isbn"], "9780111222333")
        # self.assertTrue("nickname" in results.keys())
        # self.assertEqual(results["nickname"], "F451")

        # inputs = "9780111222333 F451"
        # results = grammar.expression.parseString(inputs)

        # self.assertTrue("isbn" in results.keys())
        # self.assertEqual(results["isbn"], "9780111222333")
        # self.assertTrue("nickname" in results.keys())
        # self.assertEqual(results["nickname"], "F451")

    def test_grammar_currently_reading(self):
        inputs = "reading"
        results = grammar.expression.parseString(inputs)
        self.assertTrue("currentlyreading" in results.keys())


class TestRequests(TestCase):
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
        r = messages.Instruction(input)
        action = r.perform()
        self.assertEqual(action, "Nickname this book")

        input = "9780111222333 duck tales"
        r = messages.Instruction(input)
        action = r.perform()
        self.assertEqual(action, "This test should fail because the message has 3 words: {0}".format(input))

        input = "9780111222333 abandon"
        r = messages.Instruction(input)
        action = r.perform()
        self.assertEqual(action, "Finish reading this book")

        input = "9780111222333 Finish"
        r = messages.Instruction(input)
        action = r.perform()
        self.assertEqual(action, "Finish reading this book")

        input = "duck duck duck"
        r = messages.Instruction(input)
        action = r.perform()
        self.assertEqual(action, "I couldn't understand your message")

        input = "9870122122 start"
        r = messages.Instruction(input)
        action = r.perform()
        self.assertEqual(action, "I couldn't understand your message")

if __name__ == '__main__':
    unittest.main()
