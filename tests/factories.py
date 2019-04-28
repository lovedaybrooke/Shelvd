import datetime

import factory

from shelvd import models, messages


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


class FakeMessage(object):
    pass


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
        end_date=datetime.datetime(2017, 1, 5),
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


def mock_api_lookup(isbn):
    if isbn == "9780241341629":
        return {"title": "Not Ghost Stories", "page_count": 380,
                "authors": ["R. M. James", "Ghost Author"]}
    elif isbn == "9780000000666":
        return {"title": "Especially Violent Fairytales", 
                "page_count": 620,
                "authors": ["D. Grimmer", "Ghost Author"]}
    elif isbn == "9780000000777":
        return {"title": "Mysterious Semi-known Book", 
                "page_count": 280,
                "authors": ["A. N. Author"]}
    elif isbn == "9780000000888":
        return {"title": "Mysterious Unknown Book", 
                "page_count": 260,
                "authors": []}
    elif isbn == "0879111111111":
        return {}


def create_objects_for_models_testing(db):
    b1 = BookFactory(  # book with 2 unended readings: 1 abandoned & 1 not
        isbn="9780111111113",
        title="Necronomicon (not a real book)",  # curtail at (
        last_action_date=datetime.datetime(2017, 1, 5)
    )
    b2 = BookFactory(  # book with unended reading
        isbn="9780111111114",
        title="The King in Yellow: various stories",  # curtail at :
        nickname="YKing",
        last_action_date=datetime.datetime(2017, 1, 1)
    )
    b3 = BookFactory(  # book with no reading
        isbn="9780111111188",
        title="The Yellow Wallpaper"
    )
    b4 = BookFactory(  # book with 1 readings, 1 unended, 1 ended
        isbn="9780111111333",
        title="Ghost Stories of Antiquarians IE History Fans",  # curtail with space & ...
        last_action_date=datetime.datetime(2016, 3, 1)
    )
    b5 = BookFactory(
        isbn="9780111111334",
        title="Oh, Whistle, and I'll Come Laddiebuck"  # curtail with ...
    )
    r1 = ReadingFactory(  # finished reading of Necronomicon
        book_isbn=b1.isbn,
        start_date=datetime.datetime(2017, 1, 1),
        end_date=datetime.datetime(2017, 1, 5),
        ended=True
    )
    r2 = ReadingFactory(  # unfinished reading of King
        book_isbn=b2.isbn,
        start_date=datetime.datetime(2017, 2, 1),
        ended=False
    )
    r3 = ReadingFactory(  # finished, abandoned reading of Necronomicon
        book_isbn=b1.isbn,
        start_date=datetime.datetime(2016, 1, 1),
        end_date=datetime.datetime(2016, 1, 10),
        ended=True,
        abandoned=True
    )
    r4 = ReadingFactory(  # finished reading of Ghost Stories
        book_isbn=b4.isbn,
        start_date=datetime.datetime(2016, 3, 1),
        end_date=datetime.datetime(2016, 3, 9),
        ended=True
    )
    r5 = ReadingFactory(  # unfinished reading of Ghost Stories
        book_isbn=b4.isbn,
        start_date=datetime.datetime(2016, 4, 1),
        ended=False
    )
    a1 = AuthorFactory(
        id=1001,
        name="R. M. James"
    )
    db.session.add(b1)
    db.session.add(b2)
    db.session.add(b3)
    db.session.add(b4)
    db.session.add(b5)
    db.session.add(r1)
    db.session.add(r2)
    db.session.add(r3)
    db.session.add(r4)
    db.session.add(r5)
    db.session.add(a1)
    db.session.commit()
