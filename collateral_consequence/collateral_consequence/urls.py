"""Collateral Consequence URL Configuration.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls import url
from django.conf.urls.static import static
from django.contrib import admin

from collateral_consequence import views

urlpatterns = [
    url(r'^$', views.home_view, name="home"),
    url(r'^search/$', views.crime_search, name="crime_search"),
    url(r'^results/(?P<state>\w+)/$', views.results_view, name="results"),
    url(r'^admin/', admin.site.urls),
    url(r'^manage/add_state$', views.add_state, name="add_state"),
    url(r'^manage/add_all_states$', views.add_all_states, name="add_states"),
    url(r'^api/consequences/(?P<state>\w+)/$', views.consequences_by_state, name="api_consequences")
]

# urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
