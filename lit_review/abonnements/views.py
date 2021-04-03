from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from . import models as md
from django.http import HttpResponse
from django.contrib import messages

# Create your views here.
@login_required
def index(request):
    list_of_other_users = md.list_of_other_users(request.user)
    list_of_followed_by = md.list_of_followed_by(request.user)
    list_of_following = md.list_of_following(request.user)
    context = {'user':request.user,
        'list_of_other_users': list_of_other_users,
        'list_of_followed_by': list_of_followed_by,
        'list_of_following': list_of_following,
        }
    return render(request, 'abonnements/index.html', context)


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


def delete(request, followed_user_id):
    if request.method == 'GET':
        user = request.user
        try:
            followed_user = get_object_or_404(md.User, pk=followed_user_id)
            userFollows = get_object_or_404(md.UserFollows.objects.filter(user=user,followed_user=followed_user))
            userFollows.delete()
        except Error:
            messages.info(request, "La suppression de l'abonnement au compte  {followed_user.username} a échoué !")
        else:
            messages.success(request, f"Abonnement au compte {followed_user.username} supprimé avec succès ! ")
    return HttpResponseRedirect(reverse('abonnements:index'))
