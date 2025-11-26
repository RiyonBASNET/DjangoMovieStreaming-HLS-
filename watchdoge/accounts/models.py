from django.db import models
from django.contrib.auth.models import User
from streaming.utils import delete_old_file
from accounts.utils import user_profile_picture_upload_path


class UserProfile(models.Model):
    user=models.OneToOneField(User, on_delete=models.CASCADE)
    profile_picture=models.ImageField(
        upload_to=user_profile_picture_upload_path,
        default='profile_pictures/default_icon.png'
    )
    bio=models.TextField(blank=True)
    birthdate=models.DateField(null=True,blank=True)

    def __str__(self):
        return self.user.username
    
    def save(self, *args, **kwargs):
        if self.pk:
            delete_old_file(self, 'profile_picture')
        super().save(*args, **kwargs)