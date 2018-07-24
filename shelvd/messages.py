#!flask/bin/python
# -*- coding: utf-8 -*-
from pyparsing import ParseException
import plivo

import shelvd.grammar as grammar
from shelvd.models import Book, Reading, MessageException
from shelvd import app


class Instruction(object):

    def __init__(self, incoming_message):
        self.incoming_message = incoming_message

    @classmethod
    def process_incoming(cls, incoming_message):
        reply_client = Reply()
        try:
            instruction = cls(incoming_message)
            instruction.parse()
            response = instruction.perform()
            reply_client.send_reply(response)
            return response, 202
        except MessageException as x:
            reply_client.send_reply(str(x))
            return str(x), 400

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
                book = Book.set_nickname(self)
                return ("The book with ISBN {0} is now nicknamed {1}").format(
                    book.isbn, book.nickname)
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


class Reply(object):

    def __init__(self):
        self.client = plivo.RestClient(app.config["PLIVO_AUTH_ID"],
                                       app.config["PLIVO_AUTH_TOKEN"])

    def send_reply(self, text):
        return self.client.messages.create(
                src=app.config["SENDING_NUMBER"],
                dst=app.config["RECIPIENT_NUMBER"],
                text=text
            )
