from django.conf.urls import patterns, url

from stories import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^detail/(?P<story_id>\d+)/$', views.detail, name='detail'),
    url(r'^stories/$', views.stories, name='index'),
    url(r'^poems/$', views.poems, name='index'),
)

