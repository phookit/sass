from django.conf.urls import patterns, url

from volunteers import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^detail/(?P<volunteer_id>\d+)/$', views.detail, name='detail'),
    url(r'^application/$', views.application, name='application'),
    url(r'^thanks/$', views.application_thanks, name='thanks'),
)

