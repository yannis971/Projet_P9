from django.urls import path

from . import views

app_name = 'abonnements'

urlpatterns = [
    path('', views.index, name='index'),
]
