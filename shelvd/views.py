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

@csrf_exempt
def dataTransfer(request):
    if request.method == 'POST':
        input_type = request.POST["type"]
        if input_type == "book":
            ISBNs = [book.isbn for book in Book.objects.all()]
            if request.POST["isbn"] not in ISBNs:
                book = Book()
                book.isbn = request.POST["isbn"]
                book.title = request.POST["title"]
                book.author = request.POST["author"]
                book.page_count = request.POST["page_count"]
                book.nick = request.POST.get("nick", "")
                if request.POST.get("last_action_date"):
                    book.last_action_date = request.POST["last_action_date"]
                book.save()
        if input_type == "reading":
            if not Reading.objects.filter(start_date = request.POST["start_date"]):
                reading = Reading()
                reading.book = Book.objects.filter(isbn=request.POST["isbn"]).get()
                reading.ended = request.POST["ended"]
                reading.abandoned = request.POST["abandoned"]
                if request.POST.get("end_date"):
                    reading.end_date = request.POST["end_date"]
                reading.start_date = request.POST["start_date"]
                reading.save()
        if input_type == "bookmark":
            book = Book.objects.filter(isbn=request.POST["isbn"]).get()
            reading = Reading.objects.filter(book=book).filter(
                start_date=request.POST["start_date"]).get()
            bookmark = Bookmark()
            bookmark.reading = reading
            bookmark.date = request.POST["date"]
            bookmark.page = request.POST["page"]
            bookmark.pages_read = request.POST["pages_read"]
            bookmark.save()

    return render(request, 'home.html', {})

def home(request):
    if request.method == 'GET':
        unfinished_books = Book.generate_booklist('unfinished')
        return render(request, 'home.html',
            {'unfinished_books': unfinished_books})

def finished(request):
    if request.method == 'GET':
        finished_books = Book.generate_booklist('finished')
        return render(request, 'finished.html',
            {'finished_books': finished_books})

def abandoned(request):
    if request.method == 'GET':
        abandoned_books = Book.generate_booklist('abandoned')
        return render(request, 'abandoned.html',
            {'abandoned_books': abandoned_books})

def readingList(request):
    if request.method == 'GET':
        reading_list_books = Book.generate_booklist('reading_list_books')
        return render(request, 'reading-list.html',
            {'reading_list_books': reading_list_books})
