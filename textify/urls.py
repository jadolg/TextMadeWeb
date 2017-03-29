from django.conf.urls import url, include

from textify.views import textify_it, md_it, home

urlpatterns = [
    url(r'^$', home),
    url(r'^t/(?P<url>.*?)$', textify_it),
    url(r'^m/(?P<url>.*?)$', md_it),
]
