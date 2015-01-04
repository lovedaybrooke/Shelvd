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
            return render(request, 'home.html', {})
        except BadThing, message:
            if request.POST["source"] == "twitter":
                t = TwitterHelper()
                t.send_response(message)
                return HttpResponse("OK")
            else:
                return render(request, 'home.html', {'error': message})

def home(request):
    if request.method == 'GET':
        if request.META['HTTP_ACCEPT'] == 'application/json':
            json_booklist = Book.generate_json_booklist('unfinished')
            return HttpResponse(json_booklist,
                content_type="application/json")
        else:
            unfinished_books = Book.generate_booklist('unfinished')
            return render(request, 'home.html',
                {'unfinished_books': unfinished_books})

def finished(request):
    if request.method == 'GET':
        if request.META['HTTP_ACCEPT'] == 'application/json':
            json_booklist = Book.generate_json_booklist('finished')
            return HttpResponse(json_booklist,
                content_type="application/json")
        else:
            finished_books = Book.generate_booklist('finished')
            return render(request, 'finished.html',
                {'finished_books': finished_books})

def abandoned(request):
    if request.method == 'GET':
        if request.META['HTTP_ACCEPT'] == 'application/json':
            json_booklist = Book.generate_json_booklist('abandoned')
            return HttpResponse(json_booklist,
                content_type="application/json")
        else:
            abandoned_books = Book.generate_booklist('abandoned')
            return render(request, 'abandoned.html',
                {'abandoned_books': abandoned_books})

def readingList(request):
    if request.method == 'GET':
        if request.META['HTTP_ACCEPT'] == 'application/json':
            json_booklist = Book.generate_json_booklist('reading_list')
            return HttpResponse(json_booklist,
                content_type="application/json")
        else:
            reading_list_books = Book.generate_booklist('reading_list')
            return render(request, 'reading-list.html',
                {'reading_list_books': reading_list_books})
