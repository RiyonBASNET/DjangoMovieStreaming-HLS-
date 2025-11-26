import os
from django.db.models.signals import post_delete
from django.dispatch import receiver
from .models import Movie
from .utils import delete_hls_folder
import shutil
from django.conf import settings

@receiver(post_delete, sender=Movie)
def auto_delete_movie_files(sender, instance, **kwargs):
    if instance.file and os.path.isfile(instance.file.path):
        os.remove(instance.file.path)
    if instance.poster and os.path.isfile(instance.poster.path):
        os.remove(instance.poster.path)

    # Delete HLS folder
    if instance.hls_path:
        hls_dir = os.path.join(settings.MEDIA_ROOT, os.path.dirname(instance.hls_path))
        if os.path.isdir(hls_dir):
            shutil.rmtree(hls_dir)  # deletes folder and all its content


@receiver(post_delete, sender=Movie)
def cleanup_hls_on_delete(sender, instance, **kwargs):
    delete_hls_folder(instance)