from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.core.paginator import PageNotAnInteger
from django.core.paginator import EmptyPage
from django.db.models import CharField
from django.db.models import Value
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.urls import reverse
from django.views.generic.edit import DeleteView
from django.views.generic.edit import UpdateView

from itertools import chain

from flux.forms import ReviewModelForm
from flux.forms import TicketModelForm

from posts.models import Review
from posts.models import Ticket


def get_tickets_user_locked(logged_in_user):
    """
    Fonction qui renvoie la liste des identifiants des tickets associés aux
    critiques publiées par l'utilisateur connecté afin de bloquer la création de
    ticket sur ces critiques
    """
    reviews = Review.objects.filter(user=logged_in_user)
    return [item['ticket_id'] for item in list(reviews.values('ticket_id'))]


def get_user_posts(logged_in_user):
    """
    Fonction qui renvoie la liste des posts (tickets et critiques) publiés par
    l'utilisateur connecté
    """
    reviews = Review.objects.filter(user=logged_in_user)
    # returns queryset of reviews
    reviews = reviews.annotate(content_type=Value('REVIEW', CharField()))

    tickets = Ticket.objects.filter(user=logged_in_user)
    # returns queryset of tickets
    tickets = tickets.annotate(content_type=Value('TICKET', CharField()))

    # combine and sort the two types of posts
    posts = sorted(
        chain(reviews, tickets),
        key=lambda post: post.time_created,
        reverse=True
    )

    return posts


@login_required
def index(request):
    """
	Fonction appelée lorsque l'utilisateur est redirigé vers l'application posts
	Le décorateur @login_required permet de restreindre l'accès à l'application
	uniquement aux utilisateurs connectés
    """
    object_list = get_user_posts(request.user)
    paginator = Paginator(object_list, 3)  # 3 posts in each page
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

    context = {'page': page, 'post_list': post_list,
        'ratings' : ReviewModelForm.ratings,
        'locked_tickets': get_tickets_user_locked(request.user)
     }

    return render(request, 'posts/index.html', context)


class TicketUpdate(LoginRequiredMixin, UpdateView):
    """
    Classe héritant de LoginRequiredMixin et UpdateView
    Appelée en tant de que view afin de modifier un ticket
    LoginRequiredMixin permet d'autoriser l'accès qu'aux utilisateurs conneectés
    """
    form_class = TicketModelForm
    template_name = 'posts/ticket_update_form.html'

    def get_object(self):
        return get_object_or_404(Ticket, pk=self.kwargs.get("pk"))

    def form_valid(self, form):
        return super().form_valid(form)

    def get_success_url(self):
        pk = self.kwargs.get("pk")
        messages.success(self.request, f"Le ticket numéro {pk} a été modifié avec succes")
        return reverse("posts:index")


class TicketDelete(LoginRequiredMixin, DeleteView):
    """
    Classe héritant de LoginRequiredMixin et DeleteView
    Appelée en tant de que view afin de supprimer un ticket
    LoginRequiredMixin permet d'autoriser l'accès qu'aux utilisateurs conneectés
    """
    template_name = 'posts/ticket_delete_form.html'

    def get_object(self):
        return get_object_or_404(Ticket, pk=self.kwargs.get("pk"))

    def get_success_url(self):
        pk = self.kwargs.get("pk")
        messages.success(self.request, f"Le ticket numéro {pk} a été supprimmé avec succes")
        return reverse("posts:index")


class ReviewUpdate(LoginRequiredMixin, UpdateView):
    """
    Classe héritant de LoginRequiredMixin et UpdateView
    Appelée en tant de que view afin de modifier une critique
    LoginRequiredMixin permet d'autoriser l'accès qu'aux utilisateurs conneectés
    """
    form_class = ReviewModelForm
    template_name = 'posts/review_update_form.html'

    def get_object(self):
        review = get_object_or_404(Review, pk=self.kwargs.get("pk"))
        review.ratings = ReviewModelForm.ratings
        return review

    def form_valid(self, form):
        return super().form_valid(form)

    def get_success_url(self):
        pk = self.kwargs.get("pk")
        messages.success(self.request, f"La critique numéro {pk} a été modifiée avec succes")
        return reverse("posts:index")


class ReviewDelete(LoginRequiredMixin, DeleteView):
    """
    Classe héritant de LoginRequiredMixin et DeleteView
    Appelée en tant de que view afin de supprimer une critique
    LoginRequiredMixin permet d'autoriser l'accès qu'aux utilisateurs conneectés
    """
    template_name = 'posts/review_delete_form.html'

    def get_object(self):
        return get_object_or_404(Review, pk=self.kwargs.get("pk"))

    def get_success_url(self):
        pk = self.kwargs.get("pk")
        messages.success(self.request, f"La critique numéro {pk} a été supprimmée avec succes")
        return reverse("posts:index")
