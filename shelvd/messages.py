#!flask/bin/python
# -*- coding: utf-8 -*-
import os

from pyparsing import ParseException

import shelvd.grammar as grammar
from shelvd.models import Book, Reading, MessageException
from shelvd import app


class Instruction(object):

    def __init__(self, incoming_message):
        self.incoming_message = incoming_message

    @classmethod
    def process_incoming(cls, incoming_message):
        try:
            instruction = cls(incoming_message)
            instruction.parse()
            response = instruction.perform()
            return response, 202
        except MessageException as x:
            return str(x), 400

    @classmethod
    def process_from_web(cls, form_values):
        if form_values.get('key') != os.environ['FORM_KEY']:
            if form_values.get('key') == '':
                error = "You need to enter a key to validate your request"
            else:
                error = "That's not the right key"
            return {"success": False, "error": error}
        else:
            try:
                instruction = cls(form_values.get("message"))
                instruction.parse()
                response = instruction.perform()
                return {"success": response, "error": False}
            except MessageException as x:
                return {"success": False, "error": str(x)}

    def parse(self):
        if len(self.incoming_message.split(" ")) > 2:
            raise MessageException("Sorry, your message is too long. "
                "Remember that nicknames cannot include spaces")
        if len(self.incoming_message.split(" ")) < 2:
            raise MessageException("You need to give me a bit more to"
                " work with")
        try:
            parsed_request = grammar.expression.parseString(
                self.incoming_message)
            self.initiator = parsed_request.get("initiator")
            self.terminator = parsed_request.get("terminator")
            self.isbn = parsed_request.get("isbn")
            self.nickname = parsed_request.get("nickname")
            self.currentlyreading = parsed_request.get("currentlyreading")
        except ParseException as x:
            raise MessageException("Sorry, I didn't understand your message")

    def perform(self):
        try:
            if self.isbn and self.nickname:
                return Book.find_book_and_set_nickname(self)
            elif self.initiator:
                return Reading.start_reading(self)
            elif self.terminator:
                if self.isbn:
                    return Reading.end_reading(self)
                else:
                    return "Finish reading this book"
            elif self.currentlyreading:
                return "Tell me what I'm reading"
        except ParseException as x:
            raise MessageException("Sorry, I didn't understand your message")


