import logging

from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.http import HttpResponse

from twitterhelper import TwitterHelper
from shelvd import BadThing, Request
from models import *


@csrf_exempt
def receiveInput(request):
    if request.method == 'POST':
        try:
            this_request = Request(request.POST["bkinput"])
            this_request.perform()
            if request.POST["source"] == "app":
                return HttpResponse(json.dumps({"response": "OK"}),
                    content_type="application/json")
            else:
                return render(request, 'unfinished.html', {})
        except BadThing, message:
            if request.POST["source"] == "twitter":
                t = TwitterHelper()
                t.send_response(message)
                return HttpResponse("OK")
            elif request.POST["source"] == "app":
                error_message = "{0}".format(message)
                return HttpResponse(json.dumps({
                        "response": "error", "message": error_message}),
                    content_type="application/json")
            else:
                return render(request, 'home.html', {'error': message})


def booklistPage(request, book_status):
    if request.method == 'GET':
        if request.META['HTTP_ACCEPT'] == 'application/json':
            json_booklist = Book.generate_json_booklist(book_status)
            return HttpResponse(json_booklist,
                content_type="application/json")
        else:
            dictionary_booklist = Book.generate_booklist(book_status)
            return render(request, '{0}.html'.format(book_status),
                {'books': dictionary_booklist})


def home(request):
    return booklistPage(request, "unfinished")


def finished(request):
    return booklistPage(request, "finished")


def abandoned(request):
    return booklistPage(request, "abandoned")


def readingList(request):
    return booklistPage(request, "reading_list")

def authors(request):
    Author.generate_initial_authors()
    return booklistPage(request, "finished")