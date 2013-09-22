import datetime
import os

from django.db import models
from django.db.models import fields
import requests

from twitterhelper import TwitterHelper


class Book(models.Model):
    isbn = models.CharField(primary_key=True, max_length=13)
    nick = models.CharField(max_length=500)
    page_count = models.IntegerField()
    title = models.CharField(max_length=500)
    author = models.CharField(max_length=500)
    last_action_date = models.DateTimeField(blank=True, null=True)

    @property
    def identifier(self):
        return self.nick or self.isbn

    @classmethod
    def find_or_create(cls, request):
        book = Book.find(request)
        if not book:
            book = Book(isbn=request.isbn)
            book.get_google_book_data()
        return book

    @classmethod
    def find(cls, request):
        if request.isbn:
            isbn_query = Book.objects.filter(isbn=request.isbn)
            if isbn_query:
                return isbn_query.get()
            else:
                return False
        elif request.nick:
            nick_query = Book.objects.filter(nick=request.nick)
            if nick_query:
                return nick_query.get()
            else:
                return False
        else:
            return False

    @classmethod
    def add_to_reading_list(cls, request):
        book = cls.find_or_create(request)
        twitter_helper = TwitterHelper()
        twitter_helper.send_response("{0} ({1}) was added to your"
            " reading list".format(book.title, book.isbn))

    @classmethod
    def print_reading_list(cls):
        books = cls.generate_booklist('unfinished')
        twitter_helper = TwitterHelper()
        for book in books:
            twitter_helper.send_response("You've read '{0}' ({1}) to page"
                " {2}".format(book["title"], book["identifier"], book["page"]))

    @classmethod
    def nick_already_used(cls, nick):
        nick_query = Book.objects.filter(nick=nick)
        if nick_query:
            return nick_query.get()
        else:
            return False

    @classmethod
    def generate_booklist(cls, type):
        booklist = []

        if type == 'unfinished':
            ended = False
        else:
            ended = True

        if type == "abandoned":
            abandoned = True
        else:
            abandoned = False

        if type != 'reading_list':
            books = Book.objects.order_by('-last_action_date')
            for book in books:
                reading = Reading.find(book, ended, abandoned)
                if reading:
                    bookmark = reading.bookmarks.order_by('-date')[0]

                    booklist.append({"end_date": reading.clean_end_date,
                        "title": book.title,
                        "identifier": book.identifier,
                        "isbn": book.isbn,
                        "page": bookmark.page})

        else:
            books = Book.objects.all()  # order by most recently added first
            for book in books:
            # reading list books are those that haven't even been started
            # ie, have had no action, so no last_action_date
                if not book.last_action_date:
                    booklist.append({"title": book.title,
                        "isbn": book.isbn})

        return booklist

    def create_nick(self, nick):
        self.nick = nick
        self.save()

    def get_google_book_data(self):
        google_api_key = os.environ['GOOGLE_API_KEY']
        url = ("https://www.googleapis.com/books/v1/volumes"
            "?key={0}&country=GB&userIp=86.184.229.225"
            "&q=isbn:{1}").format(google_api_key, self.isbn)
        bkdata = requests.get(url).json()
        volumedata = bkdata.get('items', [{}])[0].get('volumeInfo', {})
        self.title = volumedata.get('title', 'Unknown')
        self.author = volumedata.get('authors', 'Unknown')[0]
        self.page_count = volumedata.get('pageCount', 350)
        self.save()

    def calculate_page(self, request):
        if request.initiator:
            return 1
        elif 'page' in dir(request):
            return request.page
        elif 'percent' in dir(request):
            return int(self.page_count * request.percent)


class Reading(models.Model):
    book = models.ForeignKey('Book', related_name='readings')
    book_isbn = models.CharField(max_length=13)
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField(blank=True, null=True)
    ended = models.BooleanField(default=False)
    abandoned = models.BooleanField(default=False)

    @property
    def clean_start_date(self):
        if self.start_date:
            return self.start_date.strftime('%B %d, %Y').lstrip('0')
        else:
            return False

    @property
    def clean_end_date(self):
        if self.end_date:
            return self.end_date.strftime('%B %d, %Y').lstrip('0')
        else:
            return False

    @classmethod
    def find(cls, book, ended, abandoned=False):
        reading = Reading.objects.filter(book=book).filter(ended=ended).filter(
            abandoned=abandoned).order_by('-start_date')
        if reading:
            return reading[0]
        else:
            return False

    @classmethod
    def start(cls, book, request):
        reading = Reading(book=book,
            book_isbn=book.isbn)
        reading.save()
        Bookmark.create(request, reading)
        return reading

    def end(self, request):
        self.ended = True
        self.end_date = datetime.datetime.now()
        if request.terminator == 'abandon':
            reading.abandoned = True
        else:
            request.page = self.book.page_count
            Bookmark.create(request, self)
        self.save()

    def get_most_recent_bookmark(self):
        return self.bookmarks.order_by('-date')[0]


class Bookmark(models.Model):
    reading = models.ForeignKey('Reading', related_name='bookmarks')
    page = models.IntegerField(default=0)
    pages_read = models.IntegerField(default=0)
    date = models.DateTimeField(auto_now_add=True)

    @classmethod
    def create(cls, request, reading=False):
        if not reading:
            reading = Reading.find(book, False)
        bookmark = Bookmark()
        bookmark.reading = reading
        bookmark.page = reading.book.calculate_page(request)
        bookmark.page_read = bookmark.calculate_pages_read(request, reading)
        bookmark.save()
        reading.book.last_action_date = bookmark.date
        reading.book.save()

    def calculate_pages_read(self, request, reading):
        # set pages read, using previous bookmark, if one exists
        if request.initiator:
            return 1
        else:
            last_bookmark = reading.get_most_recent_bookmark()
            return self.page - last_bookmark.page
