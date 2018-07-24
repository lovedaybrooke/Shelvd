import datetime

import factory
from shelvd import models


class BookFactory(factory.Factory):
    class Meta:
        model = models.Book

    isbn = factory.Sequence(lambda n: '9870000000000%d' % n)
    page_count = 350
    title = 'The King in Yellow'
    last_action_date = factory.LazyFunction(datetime.datetime.now)


class ReadingFactory(factory.Factory):
    class Meta:
        model = models.Reading

    id = factory.Sequence(lambda n: '10%d' % n)
    start_date = factory.LazyFunction(datetime.datetime.now)
    ended = False
    abandoned = False
    book_isbn = factory.SubFactory(BookFactory)


class AuthorFactory(factory.Factory):
    class Meta:
        model = models.Author

    id = factory.Sequence(lambda n: '%d' % n)
    name = "Jeff"
