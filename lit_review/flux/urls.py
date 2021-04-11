from django.urls import path

from . import views

app_name = 'flux'

urlpatterns = [
    path('', views.index, name='index'),
    #path('review/add/', views.ReviewCreate.as_view(), name='review-add'),
    path('review/add/', views.createReview, name='review-add'),
    path('review/add/<int:ticket_id>/', views.createReviewOnTicket, name='review-add-on-ticket'),
    path('ticket/add/', views.TicketCreate.as_view(), name='ticket-add'),
    path('review/detail/<int:pk>/', views.ReviewDetail.as_view(), name='review-detail'),
    path('ticket/detail/<int:pk>/', views.TicketDetail.as_view(), name='ticket-detail'),
    path('reviews/', views.ReviewList.as_view(), name='review-list'),
    path('tickets/', views.TicketList.as_view(), name='ticket-list'),
]
