from django.conf.urls import patterns, include, url

from shelvd import twitter

urlpatterns = patterns('',
    url(r'^receive-tweet$', twitter.receive-tweet,
        name='receive-tweet')
)
