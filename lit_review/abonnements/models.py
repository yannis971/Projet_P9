from django.db import models
from django.db import IntegrityError
from django.db.models.functions import Lower

# Create your models here.

from django.contrib.auth.models import User
from home.models import UserFollows

def list_of_other_users(user):
    return User.objects.filter(is_active=True,is_staff=False).exclude(username=user.username).order_by(Lower('username'))

def list_of_other_users_values(user):
    return list(User.objects.values('id', 'username').filter(is_active=True,is_staff=False).exclude(username=user.username).order_by(Lower('username')))


def list_of_following(user):
    return UserFollows.objects.filter(user=user).order_by(Lower('followed_user__username'))


def list_of_followed_by(user):
    return UserFollows.objects.filter(followed_user=user).order_by(Lower('user__username'))


def createUserFollows(user, followed_user):
    pass
