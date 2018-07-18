#!flask/bin/python
# -*- coding: utf-8 -*-
import logging
from collections import defaultdict

from pyparsing import ParseException

import grammar

class Request(object):

    def __init__(self, incoming_message):
        self.incoming_message = incoming_message.lower()
        try:
            parsed_request = grammar.expression.parseString(
                self.incoming_message)
            self.initiator = parsed_request.get("initiator")
            self.terminator = parsed_request.get("terminator")
            self.isbn = parsed_request.get("isbn")
            self.nickname = parsed_request.get("nickname")
            self.currently_reading = parsed_request.get("currently_reading")
        except ParseException as x:
            self.error = x

    def perform(self):
        if hasattr(self, "error"):
            return "I couldn't understand your message"
        else:
            if self.isbn and self.nickname:
                return "Nickname this book"
            elif self.initiator:
                return "Start reading this book"
            elif self.terminator:
                return "Finish reading this book"
            elif self.currently_reading:
                return "Tell me what I'm reading"   