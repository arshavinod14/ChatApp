from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from django.templatetags.static import static

class AccountManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Users must have an email address')
        email = self.normalize_email(email)
        email = email.lower()
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(email, password, **extra_fields)


class Account(AbstractBaseUser, PermissionsMixin):
    name = models.CharField(max_length=50, null=True)
    email = models.EmailField(max_length=100, unique=True)
    phone = models.CharField(max_length=10, unique=True, null=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = AccountManager()

    def __str__(self):
        return self.email



class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='avatars/', null=True, blank=True)
    display_name = models.CharField(max_length=20, null=True, blank=True,unique=True)
    info = models.TextField(null=True, blank=True, default="")
    removed_from_public = models.BooleanField(default=False)

    def __str__(self):
        return str(self.user)

    @property
    def name(self):
        if self.display_name:
            return self.display_name
        elif self.user.name:
            return self.user.name
        else:
            return self.user.email 

    @property
    def avatar(self):
        if self.image:
            return self.image.url
        return static('images/avatar.svg')

    @property
    def user_info(self):
        return self.info or ""
