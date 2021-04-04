#from django.contrib.auth.models import User
#from django.db import models
from django.forms import Form
from home.models import Review, Ticket

class ReviewForm(Form):
	model = Review
	fields = ['headline', 'rating', 'body']

class TicketForm(Form):
    model = Ticket
    fields = ['title', 'description', 'image']
