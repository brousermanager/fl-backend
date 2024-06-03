"""
URL configuration for frequenza_libera project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from services.feed import PodcastFeed


urlpatterns = [
    path("admin/", admin.site.urls),
    path("podcast/", include("podcast.urls")),
    path("feed/rss/xml/", PodcastFeed(), name="podcast_feed"),
    # path("podcaster/", include("podcaster.urls")),
    # path("podcast_collection/", include("podcast_collection.urls")),
]
