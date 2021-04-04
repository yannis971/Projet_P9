from django.shortcuts import render
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views.generic.edit import CreateView
from django import forms
from flux.models import Review, Ticket
from flux.forms import ReviewForm, TicketForm

# Create your views here.
@login_required
def index(request):
    context = {'user':request.user}
    return render(request, 'flux/index.html', context)

"""
class TicketForm(forms.Form):
    model = Ticket
    fields = ['title', 'description', 'image']

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

class TicketCreate(LoginRequiredMixin, CreateView):
    model = Ticket
    fields = ['title', 'description', 'image']
    template_name = 'ticket_add.html'
    #success_url = reverse('flux:index')
    success_url = reverse_lazy('index')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class ReviewCreate(LoginRequiredMixin, CreateView):
    model = Review
    fields = ['headline', 'body']
    template_name = 'review_add.html'
    #success_url = reverse('flux:index')
    success_url = reverse_lazy('flux:index')

    def form_valid(self, form):
        ticket = TicketForm(request.POST).form_valid(form)
        form.instance.ticket = ticket
        form.instance.rating = int(self.request.POST.get('rating'))
        form.instance.user = self.request.user
        return super().form_valid(form)
"""

@login_required
def review_add(request):
    form = ReviewForm()
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        ticket = TicketForm(request.POST).form_valid(form)
        form.instance.ticket = ticket
        form.instance.rating = int(request.POST.get('rating'))
        form.instance.user = request.user
        if form.is_valid():
            form.save()
            messages.success(request, "Création critique OK")
            return HttpResponseRedirect(reverse('flux:index'))
    context = {'form':form, 'ratings': [0, 1, 2, 3, 4, 5]}
    return render(request, 'flux/review_add.html', context)

@login_required
def ticket_add(request):
    form = TicketForm()
    if request.method == 'POST':
        form = TicketForm(request.POST)
        form.instance.user = request.user
        if form.is_valid():
            form.save()
            messages.success(request, "Demande de critique OK")
            return HttpResponseRedirect(reverse('flux:index'))
    context = {'form':form}
    return render(request, 'flux/ticket_add.html', context)
