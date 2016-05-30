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
    url(r'^reading_list$', views.readingList),
    url(r'^receive-input$', csrf_exempt(views.receiveInput))
)

    # Examples:
    # url(r'^$', 'shelvd.views.home', name='home'),
    # url(r'^shelvd/', include('shelvd.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
