
from django.urls import path

from textify.views import textify_it, md_it, home

urlpatterns = [
    path('', home),
    path('t/<path:url>', textify_it),
    path('m/<path:url>', md_it),
]
