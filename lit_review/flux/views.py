
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.core.paginator import PageNotAnInteger
from django.core.paginator import EmptyPage
from django.db.models import CharField
from django.db import IntegrityError
from django.db.models import Q
from django.db.models import Value
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.urls import reverse
from django.views.generic.edit import CreateView

from itertools import chain

from flux.forms import ReviewModelForm
from flux.forms import TicketModelForm
from home.models import Review
from home.models import Ticket
from home.models import UserFollows


def get_users_viewable(logged_in_user):
    """
    Fonction qui renvoie la liste des identifiants des utilisateurs
    dits "visibles" à savoir :
    - l'utilisateur connecté lui même : "users"
    - et les utilsateurs suivis par l'utilsateur connecté : "followed_users"
    """
    users = User.objects.filter(id=logged_in_user.id).values_list('id')
    followed_users = UserFollows.objects.filter(user=logged_in_user).values_list('followed_user_id')
    users_viewable = chain(users, followed_users)
    return users_viewable


def get_users_viewable_tickets(logged_in_user):
    """
    Fonction qui renvoie la liste (queryset) des tickets créés par les
    utilisateurs dits "visibles" (voir la fonction get_users_viewable plus haut)
    """
    return Ticket.objects.filter(user_id__in=get_users_viewable(logged_in_user))


def get_tickets_user(logged_in_user):
    """
    Fonction qui renvoie la liste (queryset) des tickets créés par
    l'utilisateur connecté
    """
    return Ticket.objects.filter(user=logged_in_user)


def get_users_viewable_reviews(logged_in_user):
    """
    Fonction qui renvoie la liste des critiques :
    - sur les tickets publiés par "logged_in_user" ou
    - créés par "user" ou les utilisateurs auquels "logged_in_user" est abonné
    """
    try:
        users_viewable_reviews = Review.objects.filter(Q(ticket__in=get_tickets_user(logged_in_user)) | Q(user_id__in=get_users_viewable(logged_in_user)))
    except Review.DoesNotExist:
        users_viewable_reviews = Review.objects.filter(user=logged_in_user)

    return users_viewable_reviews


def get_tickets_user_locked(logged_in_user):
    """
    Fonction qui renvoie la liste des tickets publiés par l'utilisateur connecté
    afin de bloquer la création de critique par l'utilisateur sur ses propres
    tickets
    """
    return Review.objects.filter(user=logged_in_user).values('ticket_id')


@login_required
def index(request):
    """
    Fonction appelée lorsque l'utilisateur est redirigé vers l'application flux
    Le décorateur @login_required permet de restreindre l'accès à l'application
    uniquement aux utilisateurs connectés
    """
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

    # utilisation de la classe Paginator pour gérer la pagination
    paginator = Paginator(object_list, 3)  # 3 posts par page
    page = request.GET.get('page')

    try:
        post_list = paginator.page(page)
    except PageNotAnInteger:
        # si l'argument page est non numérique on redirige vers la première
        # page
        post_list = paginator.page(1)
    except EmptyPage:
        # on renvoie la dernière page si l'argument page est au delà du nombre
        # de page maximal
        post_list = paginator.page(paginator.num_pages)

    locked_tickets = [item['ticket_id'] for item in list(get_tickets_user_locked(request.user))]

    context = dict()
    context['user'] = request.user
    context['post_list'] = post_list
    context['ratings'] = ReviewModelForm.ratings
    context['locked_tickets'] = locked_tickets

    return render(request, 'flux/index.html', context)


class TicketCreate(LoginRequiredMixin, CreateView):
    """
    Classe héritant de LoginRequiredMixin et CreateView
    Appelée en tant de que view afin de créer un ticket
    LoginRequiredMixin permet d'autoriser l'accès qu'aux utilisateurs conneectés
    """
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


@login_required
def createReview(request):
    """
    Fonction appelée afin de créer un ticket et la critique associée
    Le décorateur @login_required permet de restreindre l'accès à l'application
    uniquement aux utilisateurs connectés
    """
    template_name = 'flux/review_form.html'
    if request.method == 'POST':
        ticket_form = TicketModelForm(request.POST)
        review_form = ReviewModelForm(request.POST)
        if ticket_form.is_valid() and review_form.is_valid():
            try:
                ticket_form.instance.user = request.user
                review_form.instance.ticket = ticket_form.save()
            except IntegrityError:
                messages.info(request, f"Vous avez déjà créé un ticket avec le même titre : {ticket_form.instance.title}")
                return render(request, template_name, {'ticket_form': ticket_form, 'review_form': review_form})
            else:
                review_form.instance.user = request.user
                review_form.save()
                messages.success(request, "La critique a été créée avec succes")
                return HttpResponseRedirect(reverse('posts:index'))
    else:
        ticket_form = TicketModelForm()
        review_form = ReviewModelForm()
    return render(request, template_name, {'ticket_form': ticket_form, 'review_form': review_form})


@login_required
def createReviewOnTicket(request, ticket_id):
    """
    Fonction appelée afin de créer une critique en réponse à un ticket existant
    Le décorateur @login_required permet de restreindre l'accès à l'application
    uniquement aux utilisateurs connectés
    """
    review_form = ReviewModelForm()
    template_name = 'flux/review_on_ticket_form.html'
    id = 0
    try:
        id = int(ticket_id)
        review_form.instance.ticket = get_object_or_404(Ticket, pk=id)
    except ValueError:
        messages.info(request, "Identifiant ticket non numérique")
    if request.method == 'POST':
        review_form = ReviewModelForm(request.POST)
        if review_form.is_valid():
            id = int(ticket_id)
            review_form.instance.ticket = get_object_or_404(Ticket, pk=id)
            review_form.instance.user = request.user
            try:
                review_form.save()
            except IntegrityError:
                messages.info(request, f"Vous avez déjà créé une critique sur le ticket N° : {review_form.instance.ticket.id}")
                return render(request, template_name, {'review_form': review_form})
            else:
                messages.success(request, "La critique a été créée avec succes")
                return HttpResponseRedirect(reverse('posts:index'))
    context = {'review_form': review_form, 'ticket_id': id}
    return render(request, template_name, context)
