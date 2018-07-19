#!flask/bin/python
# -*- coding: utf-8 -*-
from pyparsing import ParseException

import shelvd.grammar as grammar
from shelvd.models import Reading, MessageException

class Instruction(object):

    def __init__(self, incoming_message):
        self.incoming_message = incoming_message.lower()

    @classmethod
    def process_incoming(cls, incoming_message):
        try:
            instruction = cls(incoming_message)
            instruction.parse()
            return instruction.perform()
        except MessageException as x:
            # instead of raising an error, send an SMS
            return str(x)

    def parse(self):
        if len(self.incoming_message.split(" ")) > 2:
            raise MessageException("Sorry, your message is too long")
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
                return "Nickname this book"
            elif self.initiator:
                reading = Reading.start_reading(self)
                return "Started reading book {0}".format(self.isbn)
            elif self.terminator:
                if self.isbn:
                    reading = Reading.end_reading(self)
                    return "Finish reading this book"
                else:
                    return "Finish reading this book"
            elif self.currentlyreading:
                return "Tell me what I'm reading"
        except ParseException as x:
            raise MessageException("Sorry, I didn't understand your message")

  
