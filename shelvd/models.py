#!/usr/bin/python
# -*- coding: utf-8 -*-

import datetime
import os
import json
import collections

from django.db import models
from django.db.models import fields
import requests
from amazon.api import AmazonAPI, AsinNotFound

import twitterhelper


class Book(models.Model):
    isbn = models.CharField(primary_key=True, max_length=13)
    nick = models.CharField(max_length=500)
    page_count = models.IntegerField()
    title = models.CharField(max_length=500)
    author = models.ManyToManyField('Author', related_name='authors',
                blank=True, default=261)
    image_url = models.CharField(max_length=500, blank=True)
    last_action_date = models.DateTimeField(blank=True, null=True)

    @property
    def identifier(self):
        return self.nick or self.isbn

    @property
    def author_names(self):
        authors = [author.name for author in self.author.all()]
        if len(authors) > 1:
            return " & ".join(authors)
        else:
            return authors[0]

    @classmethod
    def find_or_create(cls, request):
        book = Book.find(request)
        if not book:
            book_info = cls.get_amazon_book_data(request.isbn)
            author_names = book_info.pop('authors')
            book = Book(**book_info)
            book.save()
            authors = Author.find_or_create(author_names)
            for author in authors:
                book.author.add(author)
            book.get_amazon_image()
            book.save()
        return book

    @classmethod
    def get_google_book_data(cls, isbn):
        google_api_key = os.environ['GOOGLE_API_KEY']
        url = ("https://www.googleapis.com/books/v1/volumes"
            "?key={0}&country=GB&userIp=86.184.229.225"
            "&q=isbn:{1}").format(google_api_key, isbn)
        bkdata = requests.get(url).json()
        volumedata = bkdata.get('items', [{}])[0].get('volumeInfo', {})
        return {'isbn': isbn,
            'title': volumedata.get('title', 'Unknown'),
            'authors': volumedata.get('authors', ['Unknown']),
            'page_count': volumedata.get('pageCount', 350)
            }

    @classmethod
    def get_amazon_book_data(cls, isbn):
        amazon = AmazonAPI(os.environ['AWS_ACCESS_KEY_ID'],
            os.environ['AWS_SECRET_ACCESS_KEY'],
            os.environ['AWS_ASSOCIATE_TAG'],
            region='UK')
        product_or_products = amazon.lookup(ItemId=isbn, IdType='ISBN',
            SearchIndex="Books")
        if type(product_or_products) is list:
            product = product_or_products[0]
        else:
            product = product_or_products
        return {'isbn': isbn,
            'title': product.title,
            'page_count': product.pages,
            'authors': product.authors
            }

    def get_amazon_image(self):
        amazon = AmazonAPI(os.environ['AWS_ACCESS_KEY_ID'],
            os.environ['AWS_SECRET_ACCESS_KEY'],
            os.environ['AWS_ASSOCIATE_TAG'],
            region='UK')
        try:
            product = amazon.lookup(ItemId=self.isbn, IdType='ISBN',
                SearchIndex="Books")
            if type(product) is list:
                for prod in product:
                    if prod.large_image_url:
                        self.image_url = prod.large_image_url
                    elif prod.medium_image_url:
                        self.image_url = prod.medium_image_url
            elif product.large_image_url:
                self.image_url = product.large_image_url
            elif product.medium_image_url:
                self.image_url = product.medium_image_url
        except AsinNotFound:
            self.image_url = "/static/images/unknown.png"
        self.save()

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
        twitter_helper = twitterhelper.TwitterHelper()
        twitter_helper.send_response("{0} ({1}) was added to your"
            " reading list".format(book.title, book.isbn))

    @classmethod
    def tweet_books_currently_reading(cls):
        books = cls.generate_booklist('unfinished')
        twitter_helper = twitterhelper.TwitterHelper()
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

        if ended and not abandoned:
            booklist = cls.generate_year_by_year_booklist()
        else:
            books = Book.objects.order_by('-last_action_date')
            for book in books:
                reading = Reading.find(book, ended, abandoned)
                if reading:
                    bookmark = reading.bookmarks.order_by('-date')[0]

                    booklist.append({"end_date": reading.clean_end_date,
                        "title": book.title,
                        "identifier": book.identifier,
                        "isbn": book.isbn,
                        "page": bookmark.page,
                        "image_url": book.image_url,
                        "status": type})

        return booklist

    @classmethod
    def generate_year_by_year_booklist(cls):
        booklist = collections.OrderedDict()
        oldest_year = Bookmark.objects.order_by('date')[0].date.year
        this_year = datetime.datetime.today().year
        years = [year for year in range(oldest_year, this_year + 1)]
        years.reverse()
        for year in years:
            books = Book.objects.filter(
                last_action_date__gt=datetime.date(year, 1, 1)
                ).filter(
                last_action_date__lt=datetime.date(year + 1, 1, 1)
                ).order_by('-last_action_date')
            year_booklist = []
            for book in books:
                reading = Reading.find(book, True, False)
                if reading:
                    bookmark = reading.bookmarks.order_by('-date')[0]
                    year_booklist.append({"end_date": reading.clean_end_date,
                        "title": book.title,
                        "identifier": book.identifier,
                        "isbn": book.isbn,
                        "page": bookmark.page,
                        "image_url": book.image_url,
                        "status": type})
            booklist[year] = year_booklist
        return booklist

    @classmethod
    def generate_json_booklist(cls, type):
        booklist = cls.generate_booklist(type)
        return json.dumps(booklist)

    def create_nick(self, nick):
        self.nick = nick
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
        reading = Reading(book=book)
        reading.save()
        Bookmark.create(request, reading)
        return reading

    def end(self, request):
        self.ended = True
        self.end_date = datetime.datetime.now()
        if request.terminator == 'abandon':
            self.abandoned = True
            self.book.last_action_date = self.end_date
            self.book.save()
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


class Author(models.Model):
    name = models.CharField(max_length=500)
    nationality = models.CharField(max_length=500, blank=True)
    ethnicity = models.CharField(max_length=500, blank=True)
    gender = models.CharField(max_length=500, blank=True)

    @classmethod
    def find_or_create(cls, names_list):
        author_objects = []
        for name in names_list:
            author_query = cls.objects.filter(name=name)
            if author_query:
                a = author_query.get()
                author_objects.append(a)
            else:
                a = Author(name=name)
                a.save()
                author_objects.append(a)
        return author_objects
