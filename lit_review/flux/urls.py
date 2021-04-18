from django.urls import path

from . import views

app_name = 'flux'

urlpatterns = [
    path('', views.index, name='index'),
    path('review/add/', views.createReview, name='review-add'),
    path('review/add/<int:ticket_id>/', views.createReviewOnTicket, name='review-add-on-ticket'),
    path('ticket/add/', views.TicketCreate.as_view(), name='ticket-add'),
]
