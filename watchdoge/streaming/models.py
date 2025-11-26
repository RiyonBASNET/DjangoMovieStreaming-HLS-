from django.db import models
from django.utils import timezone
from django.core.validators import FileExtensionValidator, MinValueValidator,MaxValueValidator
from django.utils.text import slugify
import datetime
from .utils import delete_old_file,movie_file_upload_path,poster_upload_path
import os


class Genre(models.Model):
    name = models.CharField(max_length=100,unique=True)
    
    class Meta:
        ordering=['name']
        
    def save(self, *args, **kwargs):
        # Capitalize only the first letter of the name
        self.name = self.name.capitalize()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name
    

class Movie(models.Model):
    STATUS_CHOICES = [
        ('uploaded', 'Uploaded'),      # Just uploaded, waiting for conversion
        ('processing', 'Processing'),  # Conversion in progress
        ('ready', 'Ready'),            # HLS conversion done
        ('failed', 'Failed'),          # Conversion failed
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()

    # Original video file
    file = models.FileField(
        upload_to=movie_file_upload_path,
        validators=[FileExtensionValidator(allowed_extensions=['mp4','mkv','mov','avi'])],
        blank=True,
        null=True
    )

    # Path to HLS folder/index.m3u8
    hls_path = models.CharField(max_length=255, blank=True, null=True)

    poster = models.ImageField(
        upload_to=poster_upload_path,
        validators=[FileExtensionValidator(allowed_extensions=['jpg','jpeg','png'])],
        blank=True,
        null=True
    )

    genres = models.ManyToManyField('Genre')
    trailerUrl = models.URLField(null=True)

    release_year = models.PositiveIntegerField(
        blank=True,
        null=True,
        validators=[MinValueValidator(1888), MaxValueValidator(datetime.datetime.now().year + 2)]
    )

    duration_minutes = models.PositiveIntegerField(
        blank=True,
        null=True,
        validators=[MinValueValidator(40), MaxValueValidator(600)]
    )

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='uploaded')
    upload_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.title

    @property
    def hls_url(self):
        """Return URL to HLS index.m3u8 if ready"""
        if self.status == 'ready' and self.hls_path:
            return '/' + self.hls_path  # assuming MEDIA_URL serves 'media/' root
        return None

    def save(self, *args, **kwargs):
        """
        Save the movie.
        Note: HLS conversion is now handled by Celery in the background.
        """
        is_new = self.pk is None

        if self.pk:
            # Get the old object from DB
            old_obj = Movie.objects.filter(pk=self.pk).first()

            # Delete old video **only if** a new video file was uploaded
            if old_obj and old_obj.file and self.file and old_obj.file != self.file:
                delete_old_file(self, 'file')

            # Delete old poster **only if** a new poster was uploaded
            if old_obj and old_obj.poster and self.poster and old_obj.poster != self.poster:
                delete_old_file(self, 'poster')


        super().save(*args, **kwargs)
