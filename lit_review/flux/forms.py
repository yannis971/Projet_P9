#from django.forms import Form
from django.forms.models import ModelForm
from home.models import Review, Ticket

"""
class ReviewForm(Form):
	model = Review
	fields = ['headline', 'rating', 'body']

class TicketForm(Form):
    model = Ticket
    fields = ['title', 'description', 'image']
"""

class ReviewModelForm(ModelForm):
    class Meta:
        model = Review
        fields = ['headline', 'rating', 'body']

class TicketModelForm(ModelForm):
    class Meta:
        model = Ticket
        fields = ['title', 'description', 'image']
