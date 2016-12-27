from collections import OrderedDict

from django.test import TestCase
import fudge

from models import *
from shelvd import *

# This relies on the environment variables set in .env. Run 
# export $(cat .env) 
# in terminal before running tests

class BookTestCase(TestCase):
    fixtures = ['models.json']

    def setUp(self):
        def fake_a_request(identifier_type, identifier):
            if identifier_type == 'isbn':
                FakeRequest = fudge.Fake('Request').provides(
                    '__init__').has_attr(isbn=identifier)
            elif identifier_type == 'nick':
                FakeRequest = fudge.Fake('Request').provides(
                    '__init__').has_attr(nick=identifier).has_attr(isbn='')
            else:
                FakeRequest = fudge.Fake('Request').provides(
                    '__init__').has_attr(nick='').has_attr(isbn='')
            return FakeRequest()
        self.existing_book_isbn = '9780230200951'
        Request_existing = fudge.Fake('Request').provides('__init__').has_attr(
            isbn=self.existing_book_isbn)
        self.request_existing = Request_existing()

        self.new_book_isbn = '9781408810545'
        Request_new = fudge.Fake('Request').provides('__init__').has_attr(
            isbn=self.new_book_isbn)
        self.request_new = Request_new()

    def test_find_or_create(self):
        """ Test that new book not in DB is created, and that book already 
        in DB is returned, not created again
        """

        # Need to mock the get_google_books_data() method somehow
        Book.find_or_create(self.request_new)

        self.assertTrue(len(Book.objects.filter(isbn=self.new_book_isbn).all())
             == 1, "New book not created by Book.find_or_create")

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
            "Book's identifier method doesn't return nickname when "
            "nickname exists")

    def test_author_names(self):
        """ Test that ISBN is returned as identifier only if no nickname """

        book = Book.objects.filter(isbn='9780006550686').get()
        self.assertTrue(book.author_names == "Arundhati Roy",
            "Book with one author doesn't return correct author name as string")

        book = Book.objects.filter(isbn='9780140447552').get()
        self.assertTrue(book.author_names == "Snorri Sturluson & Jessie L. Byock",
            "Book with multiple authors doesn't return correct author names "
            "as string, joined by &")
        

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

    def test_get_google_book_data(self):
        """ Test that Google Books API returns data in the expected format
        """

        actual_data = Book.get_google_book_data('9781408810545')

        should_be_data = {'isbn': '9781408810545',
            'title': 'Harry Potter and the Philosopher\'s Stone',
            'authors': ['J. K. Rowling'],
            'page_count': 223
        }

        self.assertEqual(actual_data, should_be_data,
            'Book.get_google_book_data did not return correct data. Should be:'
            '\n{0}\nActually is:\n{1}'.format(should_be_data, actual_data))
    
    def test_generate_year_by_year_booklist(self):
        results = OrderedDict([(2016, {'count': 0, 'books': []}), (2015, 
            {'count': 0, 'books': []}), (2014, {'count': 2, 'books': [{
            'isbn': u'9780006550686', 'end_date': 'October 24, 2014', 'title':
             u'The God of Small Things', 'image_url': u'', 'identifier': 
             u'9780006550686', 'page': 368}, {'isbn': u'9780061695131', 
             'end_date': 'February 24, 2014', 'title': u'Tell My Horse', 
             'image_url': u'', 'identifier': u'9780061695131', 'page': 336}]}),
            (2013, {'count': 1, 'books': [{'isbn': u'9780007491520', 'end_date':
             'December 31, 2013', 'title': u'Neuromancer', 'image_url': u'',
             'identifier': u'Neurom', 'page': 320}]})])
        self.assertEqual(Book.generate_year_by_year_booklist(), 
            results)

    def test_generate_booklist_abandoned(self):
        list = [{'status': 'abandoned', 'isbn': u'9780006550686', 'end_date':
        'May 24, 2014', 'title': u'The God of Small Things', 'image_url': u'',
        'identifier': u'9780006550686', 'page': 180}, {'status': 'abandoned',
        'isbn': u'9780061695131', 'end_date': 'February 24, 2013', 'title':
        u'Tell My Horse', 'image_url': u'', 'identifier': u'9780061695131',
        'page': 336}]
        self.assertEqual(Book.generate_booklist("abandoned"), list)

    def test_generate_booklist_unfinished(self):
        list = [{'status': 'unfinished', 'isbn': u'9780140449198', 'end_date':
        False, 'title': u'The Epic of Gilgamesh', 'image_url': u'',
        'identifier': u'9780140449198', 'page': 205}, {'status': 'unfinished',
        'isbn': u'9780140447552', 'end_date': False, 'title':
        u'The Saga of the Volsungs', 'image_url': u'', 'identifier':
        u'9780140447552', 'page': 56}]
        self.assertEqual(Book.generate_booklist("unfinished"), list)


class ReadingTestCase(TestCase):
    fixtures = ['models.json']

    def setUp(self):
        pass

    def test_clean_start_date(self):
        reading = Reading.objects.filter(id=4).get()
        self.assertEqual(reading.clean_start_date,
            "January 01, 2014")

    def test_clean_end_date(self):
        reading = Reading.objects.filter(id=4).get()
        self.assertEqual(reading.clean_end_date,
            "February 24, 2014")
    
    def test_get_all_readings_for_year(self):
        """ 2014 readings that shouldn't be included:
            1 (finished on 2013-12-31)
            2 (unfinished)
            6 (abandoned)
            
        """
        readings_2014 = Reading.get_all_readings_for_year(2014)
        correct_data_2014 = [7, 4]
        self.assertEqual([reading.id for reading in readings_2014],
            correct_data_2014)

        """ 2013 readings that shouldn't be included:
            3 (unfinished)
            5 (abandoned)
        """
        readings_2013 = Reading.get_all_readings_for_year(2013)
        correct_data_2013 = [1]
        self.assertEqual([reading.id for reading in readings_2013],
            correct_data_2013)
    


