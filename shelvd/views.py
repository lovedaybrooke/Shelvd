import logging

from django.shortcuts import render
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.core.context_processors import csrf
from django.views.decorators.csrf import csrf_protect
from django.http import HttpResponseRedirect

from models import *
from twitterhelper import TwitterHelper
from shelvd import BadThing


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
