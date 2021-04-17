from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class CreateUserForm(UserCreationForm):
	"""
	Formulaire de création basée sur le modele User et héritant de la classe
	UserCreationForm du package django.contrib.auth.forms
	"""
	class Meta:
		"""
		classe permettant de définir le model et les champs qui seront gérés
		dans le formulaire généré par la classe  CreateUserForm
		"""
		model = User
		fields = ['username', 'email', 'password1', 'password2']
