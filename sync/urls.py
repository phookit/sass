from django.conf.urls import patterns, url

from sync import views

urlpatterns = patterns('',
    url(r'^syncevents/$', views.syncevents, name='syncevents'),
)

