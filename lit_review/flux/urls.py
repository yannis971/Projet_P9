from django.urls import path

from . import views

app_name = 'flux'

urlpatterns = [
    path('', views.index, name='index'),
]
