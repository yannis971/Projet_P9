from django.urls import path

from . import views

app_name = 'abonnements'

urlpatterns = [
    path('', views.Index.as_view(), name='index'),
    path('create/', views.create, name='create'),
    path('delete/<int:pk>', views.UserFollowsDelete.as_view(), name='delete'),
]
