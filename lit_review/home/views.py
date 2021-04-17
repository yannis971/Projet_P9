from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from home.forms import CreateUserForm


def loginUser(request):
	"""
	Fonction permettant à un utilisateur de se connecter et de s'authentifier à
	l'aide d'un identifiant et d'un mot de passe
	"""
	if request.user.is_authenticated:
		return HttpResponseRedirect(reverse('home:index'))
	else:
		if request.method == 'POST':
			username = request.POST.get('username')
			password = request.POST.get('password')
			user = authenticate(request, username=username, password=password)
			if user is not None:
				login(request, user)
				return HttpResponseRedirect(reverse('home:index'))
			else:
				messages.info(request, "Nom d'utilisateur ou mot de passe invalide")
		context = {}
		return render(request, 'home/login.html', context)


def registerUser(request):
	"""
	Fonction permettant à un utilisateur de s'inscrire à l'aide d'un formulaire
	de création de compte héritant de la classe UserCreationForm du package
	django.contrib.auth.forms
	"""
	if request.user.is_authenticated:
		return HttpResponseRedirect(reverse('home:index'))
	else:
		form = CreateUserForm()
		if request.method == 'POST':
			form = CreateUserForm(request.POST)
			if form.is_valid():
				form.save()
				username = form.cleaned_data.get('username')
				password = form.cleaned_data.get('password1')
				user = authenticate(request, username=username, password=password)
				if user is not None:
					login(request, user)
					return HttpResponseRedirect(reverse('home:index'))
				else:
					messages.info(request, "Nom d'utilisateur ou mot de passe invalide")
					return HttpResponseRedirect(reverse('home:login'))
		context = {'form':form}
		return render(request, 'home/register.html', context)


def logoutUser(request):
	"""
	Fonction permettant de se déconnecter du site
	"""
	messages.success(request, "Vous êtes déconnecté")
	logout(request)
	return HttpResponseRedirect(reverse('home:login'))


@login_required
def index(request):
	"""
	Fonction appelée lorsque l'utilisateur saisie l'URL d'accès au site :
	http://127.0.0.1:8000/home
	Le décorateur @login_required permet de restreindre l'accès au site
	uniquement aux utilisateurs connectés
	Une fois connecté, l'utilisateur est redirigée vers l'accueil de
	l'application flux
	"""
	return HttpResponseRedirect(reverse('flux:index'))


def handler404(request, *args, **argv):
	"""
	Gestionnaire d'erreur HTTP 404 redirigeant vers une page d'erreur 404
	customisée
	"""
	context = {'args': args, 'argv': argv}
	return render(request, 'home/404.html', context)
