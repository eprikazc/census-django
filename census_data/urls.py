from django.conf.urls import patterns, include, url
from views import index, get_statistics, get_statistics_for_county

urlpatterns = patterns('',
    url(r'^index/$', index, name="index"),
    url(r'^stat/$', get_statistics, name="get_statistics"),
    url(r'^stat/([^/]+)/([^/]+)/$', get_statistics_for_county, name="get_statistics_for_county"),
)
