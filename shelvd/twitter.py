import datetime

from django.db import models
from django.db.models import fields
from django.contrib.csrf.middleware import csrf_exempt

class DirectMessage(models.Model):
    text = models.CharField()
    date = models.DateTimeField()
    twitter_id = models.CharField()

@csrf_exempt
def receive_tweet(request):
    if request.method == "POST":
    	datestring = "".join(request.POST["date"].split("+0000 "))
    	date_as_date_time = datetime.datetime.strptime(datestring,
    		"%a %b %d %H:%M:%S %Y")
        dm = DirectMessage(text=request.POST["text"],
        	date=date_as_date_time, twitter_id=request.POST["twitter_id"])
        dm.save()
