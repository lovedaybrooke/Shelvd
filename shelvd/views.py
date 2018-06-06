import datetime

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
                {'books': dictionary_booklist,
                "status": book_status})


def stats(request):
    data = {'status': 'stats',
            'year': int(request.GET.get(
                    'year', datetime.datetime.today().year - 1))}
    if data['year'] > 2011:
        data['previous_year'] = data['year'] - 1
    if data['year'] < datetime.datetime.today().year:
        data['next_year'] = data['year'] + 1
    return render(request, 'stats.html', data)


def data(request):
    year = int(request.GET['year'])
    if request.GET['type'] == 'nationality':
        data = json.dumps(Author.get_years_author_data(year, 'nationality'))
    elif request.GET['type'] == 'ethnicity':
        data = json.dumps(Author.get_years_author_data(year, 'ethnicity'))
    elif request.GET['type'] == 'gender':
        data = json.dumps(Author.get_years_author_data(year, 'gender'))
    return HttpResponse(data, content_type="application/json")


def home(request):
    return booklistPage(request, "unfinished")


def finished(request):
    return booklistPage(request, "finished")


def abandoned(request):
    return booklistPage(request, "abandoned")
