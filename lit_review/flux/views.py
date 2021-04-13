from itertools import chain
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy, reverse
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
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from flux.models import Review, Ticket, UserFollows, IntegrityError

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
        users_viewable_reviews = Review.objects.filter(Q(
            ticket__in=get_tickets_user(user)) | Q(user_id__in=get_users_viewable(user)))
    except:
        pass

    return users_viewable_reviews

def get_tickets_user_locked(user):
    return Review.objects.filter(user=user).values('ticket_id')

# Create your views here.
@login_required
def index(request):
    reviews = get_users_viewable_reviews(request.user)
    # returns queryset of reviews
    reviews = reviews.annotate(content_type=Value('REVIEW', CharField()))

    tickets = get_users_viewable_tickets(request.user)
    # returns queryset of tickets
    tickets = tickets.annotate(content_type=Value('TICKET', CharField()))

    # combine and sort the two types of posts
    object_list = sorted(
        chain(reviews, tickets),
        key=lambda post: post.time_created,
        reverse=True
    )

    paginator = Paginator(object_list, 3)  # 3 posts in each page
    page = request.GET.get('page')

    try:
        post_list = paginator.page(page)
    except PageNotAnInteger:
            # If page is not an integer deliver the first page
        post_list = paginator.page(1)
    except EmptyPage:
        # If page is out of range deliver last page of results
        post_list = paginator.page(paginator.num_pages)

    locked_tickets = [item['ticket_id'] for item in list(get_tickets_user_locked(request.user))]

    context = {'user':request.user, 'post_list': post_list, 'ratings' : ReviewModelForm.ratings, 'locked_tickets': locked_tickets}
    return render(request, 'flux/index.html', context)


class TicketCreate(LoginRequiredMixin, CreateView):
    form_class = TicketModelForm
    template_name = 'flux/ticket_form.html'

    def form_valid(self, ticket_form):
        ticket_form.instance.user = self.request.user
        try:
            return super().form_valid(ticket_form)
        except IntegrityError:
            messages.info(self.request, f"Vous avez déjà créé un ticket avec le même titre : {ticket_form.instance.title}")
            return render(self.request, self.template_name, {'ticket_form': ticket_form})

    def get_success_url(self):
        messages.success(self.request, "Le ticket a été créé avec succes")
        return reverse("posts:index")

class TicketDetail(LoginRequiredMixin, DetailView):
    context_object_name = 'ticket_detail'
    template_name = 'flux/ticket_detail.html'
    queryset = Ticket.objects.all()


class TicketList(LoginRequiredMixin, ListView):
    context_object_name = 'ticket_list'
    template_name = 'flux/ticket_list.html'

    def get_queryset(self):
        return Ticket.objects.filter(user=self.request.user).order_by('-time_created')

"""
class ReviewCreate(LoginRequiredMixin, CreateView):
    form_class = ReviewModelForm
    template_name = 'flux/review_form.html'
    success_url = reverse_lazy('flux:review-list')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

"""


@login_required
def createReview(request):
    template_name = 'flux/review_form.html'
    if request.method =='POST':
        ticket_form = TicketModelForm(request.POST)
        review_form = ReviewModelForm(request.POST)
        if ticket_form.is_valid() and review_form.is_valid():
            try:
                ticket_form.instance.user = request.user
                review_form.instance.ticket = ticket_form.save()
            except IntegrityError:
                messages.info(self.request, f"Vous avez déjà créé un ticket avec le même titre : {ticket_form.instance.title}")
                return render(self.request, template_name, {'ticket_form': ticket_form, 'review_form': review_form})
            else:
                review_form.instance.user = request.user
                review_form.save()
                messages.success(request, "La critique a été créée avec succes")
                return HttpResponseRedirect(reverse('posts:index'))
    else:
        ticket_form = TicketModelForm()
        review_form = ReviewModelForm()
    return render(request, template_name ,
                  {'ticket_form': ticket_form, 'review_form': review_form})


@login_required
def createReviewOnTicket(request, ticket_id):
    review_form = ReviewModelForm()
    template_name = 'flux/review_on_ticket_form.html'
    id = 0
    try:
        id = int(ticket_id)
        review_form.instance.ticket = get_object_or_404(Ticket,pk=id)
    except ValueError:
        messages.info(request, "Identifiant ticket non numérique")
    if request.method =='POST':
        review_form = ReviewModelForm(request.POST)
        if review_form.is_valid():
            id = int(ticket_id)
            review_form.instance.ticket = get_object_or_404(Ticket,pk=id)
            review_form.instance.user = request.user
            try:
                review_form.save()
            except IntegrityError:
                messages.info(self.request, f"Vous avez déjà créé une critique sur le ticket N° : {review_form.instance.ticket.id}")
                return render(self.request, template_name, {'ticket_form': ticket_form, 'review_form': review_form})
            else:
                messages.success(request, f"La critique a été créée avec succes")
                return HttpResponseRedirect(reverse('posts:index'))
    context = {'review_form': review_form, 'ticket_id': id}
    return render(request, template_name, context)


class ReviewDetail(LoginRequiredMixin, DetailView):
    context_object_name = 'review_detail'
    template_name = 'flux/review_detail.html'
    queryset = Review.objects.all()


class ReviewList(LoginRequiredMixin, ListView):
    context_object_name = 'review_list'
    template_name = 'flux/review_list.html'

    def get_queryset(self):
        return Review.objects.filter(user=self.request.user).order_by('-time_created')
