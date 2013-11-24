About Shelvd
------------

Shelvd is a reading tracking app inspired by Bkkeepr, made by James Bridle and now sadly mothballed (http://bkkeepr.com/).

The app works off ISBNs and short input messages to track what you've been reading and how much you've read. It has a web interface and a twitter interface and runs on Heroku. Book data comes from Google Books API.

This is the second version of the app, run on Heroku as opposed to Google App Engine. It's actually 2 apps: Shelvd, that does the bulk of the work described in the paragraph above; and [Shelvd_Twitter](https://github.com/lovedaybrooke/shelvd_twitter), which simply connects to the Twitter streaming API, keeps that connection open and posts any DMs to Shelvd.

Set up
------

1. Set up a Twitter account to carry messages to and from the app.
2. Follow this Twitter account from your regular account & have this account follow your regular account
3. Generate the necessary keys and tokens for API usage (see below in "Required Environment Variables")

Required Environment Variables
------------------------------
From Twitter:

* CONSUMER_KEY
* CONSUMER_SECRET
* TOKEN
* TOKEN_SECRET
* TWITTER_HANDLE (the handle from which you'll be posting DMs to the app, and to which you'd like notifications sent)

From Google Books API:
* GOOGLE_API_KEY ([Generate one here](https://code.google.com/apis/console/#project:277472777692:access) – simple API access is all you need.)

Input grammar
-------------

(where 9780123123123 is a sample ISBN)

_To start a book:_

    9780123123123 start
    9780123123123 begin

_To give the book a nickname (an easier-to-remember identifier than the ISBN):_

    9780123123123 nickname

NB 1: this must be done after first starting a book
NB 2: after setting a nickname, you can use it anywhere instead of the ISBN

_To note the page you're up to:_

    9780123123123 196
    nickname 196

NB: this must be done after first starting a book

_To note the % you're up to (Kindle uses % instead of page numbers):_

    9780123123123 8%
    nickname 8%

NB: this must be done after first starting a book

_To finish a book (once you've reached the end):_

	9780123123123 end
	nickname end
	9780123123123 finish
	nickname finish

_To abandon a book (stop reading at your current page):_

	9780123123123 abandon
	nickname abandon
