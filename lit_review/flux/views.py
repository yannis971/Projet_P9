from itertools import chain
from django.shortcuts import render
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views.generic.edit import CreateView
from django.views.generic import DetailView
from django.views.generic import ListView
from django.db.models import CharField, Value
from django.contrib.auth.models import User
from django.db.models import Q
from django import forms
from flux.models import Review, Ticket, UserFollows

#from flux.forms import ReviewForm, TicketForm
from flux.forms import ReviewModelForm, TicketModelForm


def get_users_viewable(user):
    users = User.objects.filter(id=user.id).values_list('id')
    followed_users = UserFollows.objects.filter(user=user).values_list('followed_user_id')
    users_viewable = chain(users, followed_users)
    return users_viewable


def get_users_viewable_tickets(user):
    return Ticket.objects.filter(user_id__in=get_users_viewable(user))


def get_tickets_user(user):
    return Ticket.objects.filter(user=user)

def get_users_viewable_reviews(user):
    users_viewable_reviews = Review.objects.filter(user=user)
    try:
        users_viewable_reviews = Review.objects.get(Q(ticket__in=get_tickets_user(user)) | Q(user_id__in=get_users_viewable(user)),)
    except:
        pass
    return users_viewable_reviews


# Create your views here.
@login_required
def index(request):
    reviews = get_users_viewable_reviews(request.user)
    print("reviews", reviews)
    # returns queryset of reviews
    reviews = reviews.annotate(content_type=Value('REVIEW', CharField()))

    tickets = get_users_viewable_tickets(request.user)
    # returns queryset of tickets
    tickets = tickets.annotate(content_type=Value('TICKET', CharField()))
    # combine and sort the two types of posts
    posts = sorted(
        chain(reviews, tickets),
        key=lambda post: post.time_created,
        reverse=True
    )
    context = {'user':request.user, 'posts': posts }
    return render(request, 'flux/index.html', context)


class TicketCreate(LoginRequiredMixin, CreateView):
    form_class = TicketModelForm
    template_name = 'flux/ticket_form.html'
    success_url = reverse_lazy('flux:ticket-list')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class TicketDetail(LoginRequiredMixin, DetailView):
    context_object_name = 'ticket_detail'
    template_name = 'flux/ticket_detail.html'
    queryset = Ticket.objects.all()


class TicketList(LoginRequiredMixin, ListView):
    context_object_name = 'ticket_list'
    template_name = 'flux/ticket_list.html'

    def get_queryset(self):
        return Ticket.objects.filter(user=self.request.user).order_by('-time_created')


class ReviewCreate(LoginRequiredMixin, CreateView):
    form_class = ReviewModelForm
    template_name = 'flux/review_form.html'
    success_url = reverse_lazy('flux:review-list')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class ReviewDetail(LoginRequiredMixin, DetailView):
    context_object_name = 'review_detail'
    template_name = 'flux/review_detail.html'
    queryset = Review.objects.all()


class ReviewList(LoginRequiredMixin, ListView):
    context_object_name = 'review_list'
    template_name = 'flux/review_list.html'

    def get_queryset(self):
        return Review.objects.filter(user=self.request.user).order_by('-time_created')
