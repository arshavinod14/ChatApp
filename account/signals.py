from django.dispatch import receiver
from django.db.models.signals import post_save, pre_save
from .models import Account, Profile
import random
import string

@receiver(post_save, sender=Account)
def account_postsave(sender, instance, created, **kwargs):
    if created:
        profile = Profile.objects.create(user=instance)
        if not profile.display_name:
            random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=5))
            email_prefix = instance.email.split('@')[0]
            profile.display_name = f"{email_prefix}_{random_suffix}"
            profile.save()

@receiver(pre_save, sender=Account)
def account_presave(sender, instance, **kwargs):
    if instance.email:
        instance.email = instance.email.lower()