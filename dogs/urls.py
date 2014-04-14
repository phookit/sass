from django.conf.urls import patterns, url

from dogs import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^detail/(?P<dog_id>\d+)/$', views.detail, name='detail'),
    url(r'^available/$', views.available, name='index'),
    url(r'^rehomed/$', views.rehomed, name='index'),
)

