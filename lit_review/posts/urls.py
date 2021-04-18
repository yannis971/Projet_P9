from django.urls import path

from . import views

app_name = 'posts'

urlpatterns = [
    path('', views.index, name='index'),
    path('ticket/update/<int:pk>', views.TicketUpdate.as_view(), name='ticket-update'),
    path('ticket/delete/<int:pk>', views.TicketDelete.as_view(), name='ticket-delete'),
    path('review/update/<int:pk>', views.ReviewUpdate.as_view(), name='review-update'),
    path('review/delete/<int:pk>', views.ReviewDelete.as_view(), name='review-delete'),
]
