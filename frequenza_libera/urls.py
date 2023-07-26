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

#from base.views import create_podcast
from podcast.views import create_podcast
from podcaster.views import create_podcaster
from collection.views import create_collection
from subject.views import create_subject

urlpatterns = [
    path('admin/', admin.site.urls),
    path('collection/create', create_collection, name='create_collection'),
    
    path('podcaster/create', create_podcaster, name='create_podcaster'),
    
    path('podcast/create', create_podcast, name='create_podcast'),
    path('subject/create', create_subject, name='create_podcast')
]
