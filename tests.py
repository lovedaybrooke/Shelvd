import unittest

from flask import Flask
from flask_testing import TestCase

from grammar import *


class TestGrammar(TestCase):

    def create_app(self):
        app = Flask(__name__)
        app.config['TESTING'] = True
        return app

    def test_grammar_initiators(self):
        inputs = "9780111222333 start"
        results = expression.parseString(inputs)

        self.assertTrue("isbn" in results.keys())
        self.assertTrue("initiator" in results.keys())
        self.assertFalse("nickname" in results.keys())
        self.assertEqual(results["isbn"], "9780111222333")
        self.assertEqual(results["initiator"], "start")

        inputs = "Namenick begin"
        results = expression.parseString(inputs)
        self.assertTrue("nickname" in results.keys())
        self.assertEqual(results["nickname"], "Namenick")
        self.assertTrue("initiator" in results.keys())
        self.assertEqual(results["initiator"], "begin")

    def test_grammar_terminators(self):
        inputs = "9780111222333 end"
        results = expression.parseString(inputs)

        self.assertTrue("isbn" in results.keys())
        self.assertTrue("terminator" in results.keys())
        self.assertFalse("nickname" in results.keys())
        self.assertEqual(results["isbn"], "9780111222333")
        self.assertEqual(results["terminator"], "end")

        inputs = "Namenick finish"
        results = expression.parseString(inputs)
        self.assertTrue("nickname" in results.keys())
        self.assertEqual(results["nickname"], "Namenick")
        self.assertTrue("terminator" in results.keys())
        self.assertEqual(results["terminator"], "finish")


    def test_grammar_nicnknaming(self):
        inputs = "9780111222333 KingInYellow"
        results = expression.parseString(inputs)

        self.assertTrue("isbn" in results.keys())
        self.assertEqual(results["isbn"], "9780111222333")
        self.assertTrue("nickname" in results.keys())
        self.assertEqual(results["nickname"], "KingInYellow")

    def test_grammar_currently_reading(self):
        inputs = "reading"
        results = expression.parseString(inputs)
        self.assertTrue("currentlyreading" in results.keys())

        inputs = "Reading"
        results = expression.parseString(inputs)
        self.assertTrue("currentlyreading" in results.keys())


if __name__ == '__main__':
    unittest.main()
