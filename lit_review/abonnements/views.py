from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.db.models.functions import Lower
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic.base import TemplateView
from django.views.generic.edit import DeleteView

import json

from django.core import serializers
from django.http import HttpResponse
from django.http import JsonResponse

from home.models import UserFollows


def list_of_other_users(logged_in_user):
    """
    Fonction qui renvoie la liste (queryset) des utilisateurs à l'exception de
    l'administrateur du site et de l'utilisateur connecté
    """
    return User.objects.filter(is_active=True, is_staff=False).exclude(username=logged_in_user.username).order_by(Lower('username'))


def list_of_other_users_values(logged_in_user):
    """
    Fonction identique à list_of_other_users mais renvoie la liste des couples
    'id' et 'username'
    """
    return list(User.objects.values("id", "username").filter(is_active=True, is_staff=False).exclude(username=logged_in_user.username).order_by(Lower('username')))


def list_of_following(logged_in_user):
    """
    Fonction qui renvoie la liste (queryset) des abonnements de l'utilisateur
    connecté triée sur le nom d'utilisateur
    """
    return UserFollows.objects.filter(user=logged_in_user).order_by(Lower('followed_user__username'))


def list_of_followed_by(logged_in_user):
    """
    Fonction qui renvoie la liste (queryset) des abonnés de l'utilisateur
    connecté triée sur le nom d'utilisateur
    """
    return UserFollows.objects.filter(followed_user=logged_in_user).order_by(Lower('user__username'))


class Index(LoginRequiredMixin, TemplateView):
    """
    Classe héritant de LoginRequiredMixin et TemplateView
    Appelée en tant de que view lorsque l'url passée dans la requete est
    http://127.0.0.1:8000/abonnements/
    LoginRequiredMixin permet d'autoriser l'accès qu'aux utilisateurs conneectés
    """
    template_name = 'abonnements/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['list_of_other_users'] = list_of_other_users(self.request.user)
        context['list_of_followed_by'] = list_of_followed_by(self.request.user)
        context['list_of_following'] = list_of_following(self.request.user)
        context['users_json'] = json.dumps(list_of_other_users_values(self.request.user))
        return context


@login_required
def user_follows_create(request):
    """
    Fonction permetant de créer un abonnement
    """
    if request.method == 'POST':
        user = request.user
        try:
            followed_user_id = int(request.POST.get('followed_user_id'))
            followed_user = get_object_or_404(User, pk=followed_user_id)
            query = UserFollows(user=user, followed_user=followed_user)
            query.save()
        except ValueError:
            messages.info(request, "Identifiant utilisateur non numérique !")
        except IntegrityError:
            messages.info(request, f"L'abonnement au compte {followed_user.username} existe déjà ! Il est impossible de le créer !")
        else:
            messages.success(request, f"L'abonnement au compte {followed_user.username} a été créé avec succès !")
    return HttpResponseRedirect(reverse('abonnements:index'))


class UserFollowsDelete(LoginRequiredMixin, DeleteView):
    """
    Classe héritant de LoginRequiredMixin et DeleteView
    Appelée en tant de que view afin de supprimer un abonnement
    LoginRequiredMixin permet d'autoriser l'accès qu'aux utilisateurs conneectés
    """
    template_name = 'abonnements/user_follows_delete_form.html'

    def get_object(self):
        followed_user = get_object_or_404(User, pk=self.kwargs.get("pk"))
        userFollows = get_object_or_404(UserFollows.objects.filter(
            user=self.request.user,
            followed_user=followed_user))
        return userFollows

    def get_success_url(self):
        messages.success(self.request, f"L'abonnement au compte {self.object.followed_user.username} a été supprimé avec succès !")
        return reverse("abonnements:index")

@login_required
def fetchUsers(request):
    """ Renvoie une liste des user.id et user.username triés sur user.username """
    users_list = list_of_other_users_values(request.user)
    return JsonResponse(users_list, safe=False)
