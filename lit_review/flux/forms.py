from django.db import models
from django.forms.models import ModelForm

from home.models import Review, Ticket


class ReviewModelForm(ModelForm):
    """
    Classe basée sur ModelForm décrivant le formulaire de création d'une
    critique (model Review)
    """
    ratings = [0, 1, 2, 3, 4, 5]
    class Meta:
        """
        classe permettant de définir le model et les champs qui seront gérés
        dans le formulaire généré par la classe  ReviewModelForm
        """
        model = Review
        fields = ['headline', 'rating', 'body']


class TicketModelForm(ModelForm):
    """
    Classe basée sur ModelForm décrivant le formulaire de création d'une
    demande de critique (model Ticket)
    """

    class Meta:
        """
        classe permettant de définir le model et les champs qui seront gérés
        dans le formulaire généré par la classe  TicketModelForm
        """
        model = Ticket
        fields = ['title', 'description', 'image']
