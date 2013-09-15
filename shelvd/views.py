import logging

from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render

from twitterhelper import TwitterHelper
from shelvd import BadThing, Request


@csrf_exempt
def receiveInput(request):
    if request.method == 'POST':
        try:
            this_request = Request(request.POST["bkinput"])
            this_request.perform()
        except BadThing, message:
            logging.error(message)
            if request.POST["source"] == "twitter":
                t = TwitterHelper()
                t.send_response(message)
            else:
                return render(request, 'home.html', {'error': 'message'})

def home(request):
    if request.method == 'GET':
        return render(request, 'home.html', {})