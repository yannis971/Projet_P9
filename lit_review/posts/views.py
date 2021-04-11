from itertools import chain
from django.db.models import CharField, Value
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import UpdateView, DeleteView

from posts.models import Review, Ticket
from flux.forms import ReviewModelForm, TicketModelForm



# Create your views here.
@login_required
def index(request):
    reviews = Review.objects.filter(user=request.user)
    locked_tickets = [item['ticket_id'] for item in list(reviews.values('ticket_id'))]
    # returns queryset of reviews
    reviews = reviews.annotate(content_type=Value('REVIEW', CharField()))

    tickets = Ticket.objects.filter(user=request.user)
    # returns queryset of tickets
    tickets = tickets.annotate(content_type=Value('TICKET', CharField()))

    # combine and sort the two types of posts
    posts = sorted(
        chain(reviews, tickets),
        key=lambda post: post.time_created,
        reverse=True
    )

    context = {'user':request.user, 'posts': posts, 'ratings' : ReviewModelForm.ratings, 'locked_tickets': locked_tickets}
    return render(request, 'posts/index.html', context)


class TicketUpdate(LoginRequiredMixin, UpdateView):
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
    template_name = 'posts/ticket_delete_form.html'

    def get_object(self):
        return get_object_or_404(Ticket, pk=self.kwargs.get("pk"))

    def get_success_url(self):
        pk = self.kwargs.get("pk")
        messages.success(self.request, f"Le ticket numéro {pk} a été supprimmé avec succes")
        return reverse("posts:index")


class ReviewUpdate(LoginRequiredMixin, UpdateView):
    form_class = ReviewModelForm
    template_name = 'posts/review_update_form.html'
    #queryset = Review.objects.all()

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
    template_name = 'posts/review_delete_form.html'

    def get_object(self):
        return get_object_or_404(Review, pk=self.kwargs.get("pk"))

    def get_success_url(self):
        pk = self.kwargs.get("pk")
        messages.success(self.request, f"La critique numéro {pk} a été supprimmée avec succes")
        return reverse("posts:index")
