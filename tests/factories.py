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


def create_objects_for_message_testing(db):
    b1 = BookFactory(
        isbn="9780111111113",
        title="Necronomicon"
    )
    b2 = BookFactory(
            isbn="9780111111114",
            title="The King in Yellow",
            nickname="YKing"
        )
    r1 = ReadingFactory(
        book_isbn=b1.isbn,
        start_date=datetime.datetime(2017, 1, 1),
        ended=True
    )
    a1 = AuthorFactory(
        id=1001,
        name="R. M. James"
    )
    db.session.add(b1)
    db.session.add(b2)
    db.session.add(r1)
    db.session.add(a1)
    db.session.commit()


def mock_amazon_lookup(*args, **kwargs):
    class MockBook(object):
        title = "Not Ghost Stories"
        pages = 380
        authors = ["R. M. James", "Ghost Author"]
    return MockBook()
