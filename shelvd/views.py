import logging

from django.contrib.csrf.middleware import csrf_exempt

from twitterhelper import TwitterHelper
from shelvd import BadThing, Request


@csrf_exempt
def receiveTweet(request):
    if request.method == 'POST':
        try:
            this_request = Request(request.POST["message"])
            this_request.perform()
        except BadThing, message:
            logging.error(message)
            t = TwitterHelper()
            t.send_response(message)
