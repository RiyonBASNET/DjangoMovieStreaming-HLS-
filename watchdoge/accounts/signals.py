from django.db.models.signals import post_save,post_delete
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import UserProfile
import os
import shutil

@receiver(post_save,sender=User)
def create_user_profile(sender,instance,created,**kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save,sender=User)
def save_user_profile(sender,instance,**kwargs):
    instance.userprofile.save()

@receiver(post_save, sender=UserProfile)
def move_user_profile_picture(sender, instance, created, **kwargs):
    if instance.profile_picture and 'profile_pictures/temp/' in instance.profile_picture.name:
        original_path = instance.profile_picture.path
        ext = os.path.splitext(original_path)[1]
        new_filename = f"user_{instance.user.id}_profile{ext}"
        new_dir = os.path.join('media/profile_pictures')
        os.makedirs(new_dir, exist_ok=True)
        new_path = os.path.join(new_dir, new_filename)

        # Move file
        if os.path.exists(original_path):
            shutil.move(original_path, new_path)
            instance.profile_picture.name = f"profile_pictures/{new_filename}"
            instance.save()

@receiver(post_delete, sender=UserProfile)
def auto_delete_profile_pic_on_delete(sender, instance, **kwargs):
    if (
        instance.profile_picture and 
        os.path.isfile(instance.profile_picture.path) and 
        'default_icon.png' not in instance.profile_picture.name
    ):
        os.remove(instance.profile_picture.path)