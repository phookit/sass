from django.conf.urls import patterns, url

from phookit.apps.supporters import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    # ex: /supporter/detail/5/
    # Show details about a supporter
    url(r'^detail/(?P<supporter_id>\d+)/$', views.detail, name='detail'),
)

