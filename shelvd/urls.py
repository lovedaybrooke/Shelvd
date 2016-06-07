from django.conf.urls import patterns, include, url
from django.views.decorators.csrf import csrf_exempt

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

import views

urlpatterns = patterns('',
    url(r'^$', views.home),
    url(r'^abandoned$', views.abandoned),
    url(r'^finished$', views.finished),
    url(r'^receive-input$', csrf_exempt(views.receiveInput)),
    url(r'^stats$', views.stats),
    url(r'^data$', views.data)
)
