from django.contrib.auth.models import AbstractUser
from django.db import models

from .constants import ROLES, ADMIN, MODER, USER


class User(AbstractUser):
    confirmation_code = models.CharField(max_length=32, editable=False)
    role = models.CharField(choices=ROLES, default='user', max_length=9)
    bio = models.TextField('Biography', blank=True)

    @property
    def is_admin(self):
        return self.role == ADMIN

    @property
    def is_moder(self):
        return self.role == MODER

    @property
    def is_user(self):
        return self.role == USER
