from django.conf.urls import patterns, url

from fb import views

urlpatterns = patterns('',
    #url(r'^$', views.index, name='index'),
    url(r'^adminauth/$', views.adminauth, name='adminauth'),
    url(r'^nocookies$', views.nocookies, name='nocookies'),
)

