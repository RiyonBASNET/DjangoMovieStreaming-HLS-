from django.shortcuts import render,redirect,get_object_or_404
from django.db.models import Count,Q
from .models import Movie, Genre
from .forms import MovieUploadForm, GenreForm, MovieEditForm
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from accounts.auth import admin_only,user_only
from difflib import SequenceMatcher
import os
from django.conf import settings
from django.utils import timezone
from django.db import transaction
from .tasks import convert_movie_to_hls
# Create your views here.

@login_required
@admin_only
def upload_movie(request):
    if request.method == 'POST':
        form = MovieUploadForm(request.POST, request.FILES)
        if form.is_valid():
            title = form.cleaned_data['title']
            release_year = form.cleaned_data['release_year']

            # Check for duplicates
            if Movie.objects.filter(title__iexact=title.strip(), release_year=release_year).exists():
                messages.error(request, "This movie already exists.")
            else:
                # Save movie with status "uploaded"
                movie = form.save(commit=False)
                movie.status = 'uploaded'
                movie.save()
                form.save_m2m()


                # Trigger background HLS conversion
                transaction.on_commit(lambda: convert_movie_to_hls.delay(movie.id))

                messages.success(request, "Movie uploaded! Conversion in progress.")
                return redirect('admin-movies-list')
        else:
            messages.error(request, "Could not upload. Check the form.")

    else:
        form = MovieUploadForm()

    return render(request, 'streaming/uploadMovie.html', {'form': form})

@login_required
@admin_only
def add_genre(request):
    if request.method == 'POST':
        form = GenreForm(request.POST)
        if form.is_valid():
            try:
                form.save()
                messages.success(request,"Genre added.")
            except Exception:
                messages.error(request,"Genre already exists.")    
            return redirect('add-genre')
        else:
            messages.error(request,"Invalid input")
            return render(request, 'streaming/addGenre.html',{'form':form})

    return render(request,'streaming/addGenre.html',{'form':GenreForm})

@login_required
@admin_only
def showMovies(request):
    genres = Genre.objects.all()
    movies = Movie.objects.all()

    query = request.GET.get('q')

    selected_genres = request.GET.getlist('genres')

    if query:
        movies = movies.filter(
            Q(title__icontains=query) | 
            Q(description__icontains=query)
        )

    if selected_genres:
        movies = movies.filter(genres__id__in=selected_genres).distinct()
    
    paginator = Paginator(movies,5)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj':page_obj,
        'query':query,
        'genres':genres,
        'selected_genres':selected_genres,
        'MEDIA_URL':settings.MEDIA_URL
    }
    return render(request,'streaming/showMovies.html',context)

@login_required
@admin_only
def showGenres(request):
    genres = Genre.objects.all().order_by('name')

    paginator = Paginator(genres,5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj':page_obj,
    }

    return render(request,'streaming/showGenres.html',context)

@login_required
@admin_only
def movie_details(request,movieId):
    movie=get_object_or_404(Movie,id=movieId)

    recommendation= get_similar_movies(movie)
    other_movies = Movie.objects.exclude(id__in=[m.id for m in recommendation]).exclude(id=movie.id)[:5]
    context={
        'movie':movie,
        'allMoives':recommendation,
        'other_movies':other_movies,
    }
    return render(request,'streaming/videoDetails.html',context)

@login_required
@admin_only
def deleteGenre(request,genreId):
    if genreId:
        id=int(genreId)
        genre=Genre.objects.get(id=id)
        genre.delete()
        messages.success(request,"Item deleted")
    else:
        messages.error(request,"An error occured. Try Again.")

    return redirect('admin-genres-list')

@login_required
@admin_only
def deleteMovie(request, movieId):
    movie = get_object_or_404(Movie, id=movieId)

    # Delete poster safely
    if movie.poster and movie.poster.name:
        poster_path = movie.poster.path
        if os.path.exists(poster_path):
            os.remove(poster_path)

    # Delete original video safely (may already be deleted after HLS conversion)
    if movie.file and movie.file.name:
        file_path = movie.file.path
        if os.path.exists(file_path):
            os.remove(file_path)

    # Delete HLS folder (index + segments)
    if movie.hls_path:
        hls_folder = os.path.join(settings.MEDIA_ROOT, os.path.dirname(movie.hls_path))
        if os.path.isdir(hls_folder):
            import shutil
            shutil.rmtree(hls_folder, ignore_errors=True)

    # Delete movie entry from DB
    movie.delete()

    messages.success(request, "Item deleted")
    return redirect('admin-movies-list')

@login_required
@admin_only
def dashboard(request):
    total_users= User.objects.count()
    total_movies = Movie.objects.count()
    total_genres = Genre.objects.count()
    recent_movies = Movie.objects.order_by('-upload_date')[:5]
    movies_per_genre = Genre.objects.annotate(movie_count=Count('movie'))
    context={
        'total_movies': total_movies,
        'total_genres': total_genres,
        'recent_movies': recent_movies,
        'movies_per_genre': movies_per_genre,
        'total_users':total_users,
    }
    return render(request, 'streaming/dashboard.html', context)

@login_required
@admin_only
def editGenre(request,genreId):
    genre=get_object_or_404(Genre, id=genreId)

    if request.method=='POST':
        form=GenreForm(request.POST,instance=genre)
        if form.is_valid():
            form.save()
            messages.success(request,'Edit successful!')
            return redirect('admin-genres-list')
        else:
            messages.error(request,'Something went wrong. Try again!')

    return render(request,'streaming/editGenre.html',{
        'form':GenreForm(instance=genre)
        })

@login_required
@admin_only
def editMovie(request, movieId):
    movie = get_object_or_404(Movie, id=movieId)
    if request.method == 'POST':
        form = MovieEditForm(request.POST, request.FILES, instance=movie)
        if form.is_valid():
            movie = form.save(commit=False)

            # Only reset status if a new file is uploaded
            if 'file' in request.FILES:
                movie.status = 'uploaded'

            movie.save()
            form.save_m2m()

            if 'file' in request.FILES:
                transaction.on_commit(lambda: convert_movie_to_hls.delay(movie.id))

            messages.success(request, "Movie updated successfully.")
            return redirect('admin-movies-list')
    else:
        form = MovieEditForm(instance=movie)

    return render(request, 'streaming/editMovie.html', {'form': form, 'movie': movie})

@login_required
@admin_only
def users_list(request):
    users=User.objects.all()

    paginator = Paginator(users,5)
    page_number=request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request,'streaming/users_list.html',{'page_obj':page_obj})


##############################################
##############################################
def get_similar_movies(current_movie, limit=6):
    all_movies = Movie.objects.exclude(id=current_movie.id)
    current_year = timezone.now().year
    # Genre filtering
    genre_ids = current_movie.genres.values_list('id', flat=True)
    genre_matches = all_movies.filter(genres__in=genre_ids,release_year__lte=current_year).distinct()

    # Optional: Filter by name similarity using SequenceMatcher
    def similarity(a, b):
        return SequenceMatcher(None, a.lower(), b.lower()).ratio()

    genre_matches = sorted(
        genre_matches,
        key=lambda m: similarity(m.title, current_movie.title),
        reverse=True
    )

    return genre_matches[:limit]