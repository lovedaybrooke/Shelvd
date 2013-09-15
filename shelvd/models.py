import datetime
import os

from django.db import models
from django.db.models import fields
import requests

from twitterhelper import TwitterHelper


class Book(models.Model):
    ISBN = models.CharField(primary_key=True, max_length=13)
    nick = models.CharField(max_length=500)
    page_count = models.IntegerField()
    title = models.CharField(max_length=500)
    author = models.CharField(max_length=500)
    last_action_date = models.DateTimeField(blank=True, null=True)

    @property
    def identifier(self):
        return self.nick or self.ISBN

    @classmethod
    def find_or_create(cls, request):
        book = Book.find(request)
        if not book:
            book = Book(ISBN=request.ISBN)
            book.get_google_book_data()
        return book

    @classmethod
    def find(cls, request):
        if request.nick:
            nick_query = Book.objects.filter(nick=request.nick)
            if nick_query:
                return nick_query.get()
        elif request.ISBN:
            ISBN_query = Book.objects.filter(nick=request.nick)
            if ISBN_query:
                return ISBN_query.get()
        else:
            return False

    @classmethod
    def add_to_reading_list(cls, request):
        book = cls.find_or_create(request)
        twitter_helper = TwitterHelper()
        twitter_helper.send_response("{0} ({1}) added to your reading "
            "list".format(book.title, book.ISBN))

    @classmethod
    def nick_already_used(cls, nick):
        return Book.objects.filter(nick=nick).get()

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
                    bookmark = reading.bookmarks.order_by('-date').first()

                    booklist.append({"end_date": reading.clean_end_date,
                        "title": book.title,
                        "identifier": book.identifier,
                        "isbn": book.ISBN,
                        "page": bookmark.page})

        else:
            books = Book.all()  # order by most recently added first
            for book in books:
            # reading list books are those that haven't even been started
            # ie, have had no action, so no last_action_date
                if not book.last_action_date:
                    booklist.append({"title": book.title,
                        "isbn": book.ISBN})

        return booklist

    def create_nick(self, nick):
        self.nick = nick
        self.save()

    def get_google_book_data(self):
        google_api_key = os.environ['GOOGLE_API_KEY']
        url = ("https://www.googleapis.com/books/v1/volumes"
            "?key={0}&country=GB&userIp=86.184.229.225"
            "&q=isbn:{1}").format(google_api_key, self.ISBN)
        bkdata = requests.get(url).json()
        volumedata = bkdata.get('items', [{}])[0].get('volumeInfo', {})
        self.title = volumedata.get('title', 'Unknown')
        self.author = volumedata.get('authors', 'Unknown')[0]
        self.page_count = volumedata.get('pageCount', 350)
        self.save()


class Reading(models.Model):
    book = models.ForeignKey('Book', related_name='readings')
    book_ISBN = models.CharField(max_length=13)
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
        reading = Reading.objects.filter('book_ISBN =',
            book.ISBN).filter('ended =', ended).filter('abandoned =',
            abandoned)
        if reading:
            return reading
        else:
            return False

    @classmethod
    def start(cls, book):
        reading = Reading(book=book,
            book_ISBN=book.ISBN)
        reading.save()
        request.page = 1
        Bookmark.create(request, book, reading)
        return reading

    def end(self):
        self.ended = True
        self.end_date = datetime.datetime.now()
        if request.terminator == 'abandon':
            reading.abandoned = True
        else:
            request.page = self.book.page_count
            Bookmark.create(request, self)
        self.save()

    def get_most_recent_bookmark(self):
        return self.bookmarks.order_by('-date').first()


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
        bookmark.page = bookmark.calculate_page(request, reading.book)
        bookmark.page_read = bookmark.calculate_pages_read(request, reading)
        bookmark.save()
        reading.book.last_action_date = bookmark.date
        reading.book.save()

    def calculate_page(self, request, book):
        if 'page' in dir(request):
            return request.page
        elif 'percent' in dir(request):
            return int(book.page_count * request.percent)

    def calculate_pages_read(self, request, reading):
        # set pages read, using previous bookmark, if one exists
        if request.initiator:
            return 1
        else:
            last_bookmark = reading.get_most_recent_bookmark()
            return self.page - last_bookmark.page
