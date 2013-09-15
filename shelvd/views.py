from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.http import HttpResponse

from twitterhelper import TwitterHelper
from shelvd import BadThing, Request


@csrf_exempt
def receiveInput(request):
    if request.method == 'POST':
        try:
            this_request = Request(request.POST["bkinput"])
            this_request.perform()
            return render(request, 'home.html', {})
        except BadThing, message:
            if request.POST["source"] == "twitter":
                t = TwitterHelper()
                t.send_response(message)
                return HttpResponse("OK")
            else:
                return render(request, 'home.html', {'error': 'message'})

def home(request):
    if request.method == 'GET':
        return render(request, 'home.html', {})