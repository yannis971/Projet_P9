from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.views.generic.base import TemplateView
from django.views.generic.edit import DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from . import models as md
from django.http import HttpResponse
from django.contrib import messages
import json


class Index(LoginRequiredMixin, TemplateView):
    template_name = 'abonnements/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['list_of_other_users'] = md.list_of_other_users(self.request.user)
        context['list_of_followed_by'] = md.list_of_followed_by(self.request.user)
        context['list_of_following'] = md.list_of_following(self.request.user)
        context['users_json'] = json.dumps(md.list_of_other_users_values(self.request.user))
        return context


@login_required
def create(request):
    if request.method == 'POST':
        user = request.user
        try:
            followed_user_id = int(request.POST.get('followed_user_id'))
            followed_user = get_object_or_404(md.User, pk=followed_user_id)
            query = md.UserFollows(user=user, followed_user=followed_user)
            query.save()
        except ValueError:
            messages.info(request, "Identifiant utilisateur non numérique ! Impossible de créer un abonnement !")
        except md.IntegrityError:
            messages.info(request, f"L'abonnement au compte {followed_user.username} existe déjà ! Il est impossible de le créer !")
        else:
            messages.success(request, f"Abonnement au compte {followed_user.username} créé avec succès !")
    return HttpResponseRedirect(reverse('abonnements:index'))


class UserFollowsDelete(LoginRequiredMixin, DeleteView):
    template_name = 'abonnements/user_follows_delete_form.html'

    def get_object(self):
        followed_user = get_object_or_404(md.User, pk=self.kwargs.get("pk"))
        userFollows = get_object_or_404(md.UserFollows.objects.filter(user=self.request.user,followed_user=followed_user))
        return userFollows

    def get_success_url(self):
        #followed_user = get_object_or_404(md.User, pk=self.kwargs.get("pk"))
        messages.success(self.request, f"L'abonnement au compte {self.object.followed_user.username} a été supprimé avec succès !")
        return reverse("abonnements:index")
