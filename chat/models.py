from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.validators import FileExtensionValidator
from django.templatetags.static import static
import shortuuid
import os
import pytz
from PIL import Image


class ChatGroup(models.Model):
    group_name = models.CharField(max_length=128, unique=True, default=shortuuid.uuid)
    groupchat_name = models.CharField(max_length=128, null=True, blank=True)
    admin = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='groupChats', null=True, blank=True, on_delete=models.SET_NULL)
    users_online = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="online_in_groups", blank=True)
    members = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='chat_groups', blank=True)
    is_private = models.BooleanField(default=False)
    group_image = models.ImageField(upload_to='group_images/', null=True, blank=True, validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])])
    last_activity = models.DateTimeField(default=timezone.now)

    def update_last_activity(self):
        self.last_activity = timezone.now()
        self.save()

    def get_formatted_last_activity(self):
        india_tz = pytz.timezone('Asia/Kolkata')
        last_activity_local = self.last_activity.astimezone(india_tz)
        now = timezone.now().astimezone(india_tz)
        
        days_difference = (now.date() - last_activity_local.date()).days

        if days_difference == 0:
            # If the message is from today, show the exact time
            return last_activity_local.strftime("%I:%M %p").lower().lstrip('0')
        elif days_difference == 1:
            # If the message is from yesterday, show "Yesterday"
            return "Yesterday"
        elif days_difference == 2:
            # If the message is from the day before yesterday, show "Day before yesterday"
            return last_activity_local.strftime("%A")
        elif 2 < days_difference < 7:
            # If the message is from earlier this week (but not yesterday or day before), show the day name
            return last_activity_local.strftime("%A")
        else:
            # For messages a week old or older, show the date
            return last_activity_local.strftime("%d %b %Y")

    def __str__(self):
        return self.groupchat_name or self.group_name
    
    @property
    def avatar(self):
        if self.group_image:
            return self.group_image.url
        return static('images/grp-icon.jpg')
    
    

class GroupMessage(models.Model):
    group = models.ForeignKey(ChatGroup, related_name='chat_messages', on_delete=models.CASCADE)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    body = models.CharField(max_length=300, blank=True, null=True)
    file = models.FileField(upload_to='files/', blank=True, null=True)

    created = models.DateTimeField(auto_now_add=True)

    def get_formatted_time(self):
        india_tz = pytz.timezone('Asia/Kolkata')
        india_time = self.created.astimezone(india_tz)
        return india_time.strftime("%I:%M %p").lower().lstrip('0')
    
    @property
    def filename(self):
        if self.file:
            return os.path.basename(self.file.name)
        return None

    def __str__(self):
        if self.body:
            return f'{self.author.name} : {self.body}'
        elif self.file:
            return f'{self.author.name} : {self.filename}'

    class Meta:
        ordering = ['-created']

    @property    
    def is_image(self):
        try:
            image = Image.open(self.file) 
            image.verify()
            return True 
        except:
            return False
    
    

        

