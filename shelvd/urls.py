from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

import views

urlpatterns = patterns('',
    url(r'^$', views.home),
    url(r'^receive-input$', views.receiveInput)
)

    # Examples:
    # url(r'^$', 'shelvd.views.home', name='home'),
    # url(r'^shelvd/', include('shelvd.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
