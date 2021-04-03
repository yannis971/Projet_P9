from django.urls import path

from . import views

app_name = 'abonnements'

urlpatterns = [
    path('', views.index, name='index'),
    path('create/', views.create, name='create'),
    path('delete/<int:followed_user_id>', views.delete, name='delete'),
]
