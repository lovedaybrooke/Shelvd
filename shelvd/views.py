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

def bookmarks(request):
    logger = logging.getLogger('shelvd')
    books = Book.objects.filter(last_action_date__lt='2015-08-23')
    logger.info('{0} books finished before 2015-08-23'.format(len(books)))
    logger.info('--------------------------------------------------')

    for book in books:
        logger.info(u'Book is {0}, ({1})'.format(book.title, book.isbn))
        last_reading = Reading.objects.filter(book_id=book.isbn).order_by('-end_date')[0]
        logger.info('    last reading ended {0}'.format(last_reading.end_date))
        bookmarks = Bookmark.objects.filter(reading_id=last_reading.id).order_by('-id')
        logger.info('    {0} bookmarks'.format(len(bookmarks)))
        for bookmark in bookmarks:
            bookmark.date = last_reading.end_date
            bookmark.save()

    return booklistPage(request, "finished")
