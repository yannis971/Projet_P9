from django.conf import settings
from django.core.validators import MinValueValidator
from django.core.validators import MaxValueValidator
from django.db import models
from django.utils import timezone


class Ticket(models.Model):
    """
    Entité Ticket : correspond à une demande de critique
    """
    title = models.CharField(max_length=128)
    description = models.CharField(max_length=2048, blank=True)
    user = models.ForeignKey(
        to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    image = models.ImageField(null=True, blank=True, upload_to='images/')
    time_created = models.DateTimeField(default=timezone.now)

    class Meta:
        """
        Contrainte d'unicité d'un ticket sur le titre et l'utilisateur
        """
        constraints = [
            models.UniqueConstraint(fields=['title', 'user'], name='unique_ticket'),
        ]


class Review(models.Model):
    """
    Entité Review : correspond à une critique sur un livre ou un article
    """
    ticket = models.ForeignKey(to=Ticket, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField(
        # validates that rating must be between 0 and 5
        validators=[MinValueValidator(0), MaxValueValidator(5)])
    headline = models.CharField(max_length=128)
    body = models.CharField(max_length=8192, blank=True)
    user = models.ForeignKey(
        to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    time_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        """
        Contrainte d'unicité d'une critique sur le ticket et l'utilisateur
        """
        constraints = [
            models.UniqueConstraint(fields=['ticket', 'user'], name='unique_review'),
        ]


class UserFollows(models.Model):
    """
    Entité Liens entre utilisateurs et utilisateurs suivis
    """
    user = models.ForeignKey(
        to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='following')
    followed_user = models.ForeignKey(
        to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='followed_by')

    class Meta:
        """
        Contrainte d'unicité pour éviter des liens en doublons
        """
        unique_together = ('user', 'followed_user', )
