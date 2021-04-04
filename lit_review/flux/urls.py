from django.urls import path

from . import views

app_name = 'flux'

urlpatterns = [
    path('', views.index, name='index'),
    #path('review/add/', views.ReviewCreate.as_view(), name='review-add'),
    #path('ticket/add/', views.TicketCreate.as_view(), name='ticket-add'),
    path('review/add/', views.review_add, name='review-add'),
    path('ticket/add/', views.ticket_add, name='ticket-add'),
]
