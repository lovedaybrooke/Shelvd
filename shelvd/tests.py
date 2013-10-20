from django.test import TestCase
import fudge

from models import *
from shelvd import *
import twitterhelper


class ModelsTestCase(TestCase):
    fixtures = ['models.json']

    def setUp(self):
        self.existing_book_isbn = '9780230200951'
        Request_existing = fudge.Fake('Request').provides('__init__').has_attr(
            isbn=self.existing_book_isbn)
        self.request_existing = Request_existing()

        self.new_book_isbn = '9781408810545'
        Request_new = fudge.Fake('Request').provides('__init__').has_attr(
            isbn=self.new_book_isbn)
        self.request_new = Request_new()

    def test_find_or_create__creating_new_book(self):
        """ Test that new book not in DB is created """

        Book.find_or_create(self.request_new)

        self.assertTrue(len(Book.objects.filter(isbn=self.new_book_isbn).all())
             == 1, "New book not created by Book.find_or_create")

    def test_find_or_create__finding_existing_book(self):
        """ Test that book already in DB is returned, not created again """

        self.assertTrue(len(Book.objects.filter(
            isbn=self.existing_book_isbn).all()) == 1,
            "Fixture book hasn't been created")

        Book.find_or_create(self.request_existing)

        self.assertTrue(len(Book.objects.filter(
            isbn=self.existing_book_isbn).all()) == 1,
            "Pre-existing book been duplicated in DB")

    def test_identifier(self):
        """ Test that ISBN is returned as identifier only if no nickname """

        book = Book.objects.filter(isbn=self.existing_book_isbn).get()
        self.assertTrue(book.identifier == self.existing_book_isbn,
            "Book's identifier method doesn't return ISBN when no nickname")

        book.nick = "Jimmy Shakespeare"
        self.assertTrue(book.identifier == 'Jimmy Shakespeare',
            "Book's identifier method doesn't return nickname when exists")

    @fudge.patch('shelvd.twitterhelper.TwitterHelper')
    def test_add_to_reading_list(self, FakeTwitterHelper):
        """ Test that this function adds book to DB in correct way (ie, no
        last action date, no reading, no bookmarks)
        """

        (FakeTwitterHelper.expects_call()
                        .returns_fake()
                        .expects('send_response').with_arg_count(1))

        Book.add_to_reading_list(self.request_new)
        book = Book.objects.filter(isbn=self.new_book_isbn).get()

        self.assertTrue(book.isbn == self.new_book_isbn)
        self.assertFalse(book.last_action_date)
        self.assertFalse(book.readings.all())
