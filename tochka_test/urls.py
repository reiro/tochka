from django.urls import include, path
from django.contrib import admin
from . import views

urlpatterns = [
    path('', include('shares.urls')),
    path('admin/', admin.site.urls),
    path('parser/', views.parser, name='parser'),
]