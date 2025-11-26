from django import forms
from .models import Movie, Genre
from django.core.exceptions import ValidationError
import datetime
import os

class MovieUploadForm(forms.ModelForm):
    class Meta:
        model = Movie
        fields = ['title', 'description', 'file', 'poster', 'genres', 'trailerUrl', 'release_year', 'duration_minutes']
        widgets = {
            'genres': forms.CheckboxSelectMultiple(),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Restrict file chooser to videos
        self.fields['file'].widget.attrs.update({'accept': 'video/*'})
        # (Optional) restrict poster to images
        self.fields['poster'].widget.attrs.update({'accept': 'image/*'})

    def clean_file(self):
        file = self.cleaned_data.get('file')
        if not file:
            raise forms.ValidationError("Movie file is required.")
        return file

    def clean_poster(self):
        poster = self.cleaned_data.get('poster')
        if not poster:
            raise forms.ValidationError("Movie poster is required.")
        return poster

    def clean_release_year(self):
        year=self.cleaned_data.get('release_year')
        if year < 1880 or year > datetime.datetime.now().year+2:
            raise forms.ValidationError("Enter valid year between 1880 and next two years.")
        return year
    
    def clean_duration_minutes(self):
        duration=self.cleaned_data.get('duration_minutes')
        if duration < 40 or duration > 600:
            raise forms.ValidationError("Duration must be between 40 and 600 minutes.")
        return duration

class GenreForm(forms.ModelForm):
    class Meta:
        model=Genre
        fields='__all__'

class MovieEditForm(forms.ModelForm):
    
    class Meta:
        model = Movie
        fields = ['title', 'description', 'file', 'poster', 'genres', 'trailerUrl', 'release_year', 'duration_minutes']
        widgets = {
            'genres': forms.CheckboxSelectMultiple(),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['file'].widget.attrs.update({'accept': 'video/*'})
        self.fields['poster'].widget.attrs.update({'accept': 'image/*'})

    def clean_release_year(self):
        year = self.cleaned_data['release_year']
        if year < 1880 or year > datetime.datetime.now().year + 2:
            raise forms.ValidationError("Enter valid year between 1880 and next two years.")
        return year

    def clean_duration_minutes(self):
        duration = self.cleaned_data['duration_minutes']
        if duration < 40 or duration > 600:
            raise forms.ValidationError("Duration must be between 40 and 600 minutes.")
        return duration