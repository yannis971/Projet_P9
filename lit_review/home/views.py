from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect, HttpResponseNotFound
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import CreateUserForm

# Create your views here.

# return redirect fonctionne avec l'URL absolue

def loginUser(request):
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
	messages.success(request, "Vous êtes déconnecté")
	logout(request)
	return HttpResponseRedirect(reverse('home:login'))


@login_required
def index(request):
    context = {'user':request.user}
    return render(request, 'home/index.html', context)

def handler404(request, *args, **argv):
	context = {'args': args, 'argv': argv}
	return render(request, 'home/handler404.html', context)
