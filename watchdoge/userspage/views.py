from django.shortcuts import render,redirect,get_object_or_404
from streaming.models import Movie,Genre
from django.core.paginator import Paginator
from django.db.models import Q
from django.db.models.functions import Lower
from django.contrib.auth.decorators import login_required
from accounts.models import UserProfile
from .models import WatchHistory, Favorite, Watchlist
from accounts.auth import user_only
from django.contrib import messages
from difflib import SequenceMatcher
import os
from django.conf import settings
from django.utils import timezone 
# Create your views here.

def home(request):
    movies=Movie.objects.all()
    genres=Genre.objects.all()

    current_year = timezone.now().year
    
    latest_movies= movies.filter(release_year=current_year).order_by('-release_year')
    coming_soon = movies.filter(release_year__gt=current_year).order_by('release_year')
    

    context={
        'movies':movies,
        'genres':genres,
        'latest_movies':latest_movies,
        'coming_soon':coming_soon,
    }
    return render(request,'userspage/homepage.html',context)

def genres_list(request):
    genres=Genre.objects.all().order_by('name')

    return render(request, 'userspage/genres.html',{'genres':genres})

def movies_list(request):
    movies = Movie.objects.all().order_by('title')
    paginator = Paginator(movies,15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request,'userspage/movies.html',{'page_obj':page_obj})

def movies_by_genre(request,genreName):
    genre=Genre.objects.get(name__iexact=genreName)
    movies=Movie.objects.filter(genres=genre).order_by(Lower('title'))

    paginator = Paginator(movies,15)

    page_number=request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context={
        'genre':genre,
        'page_obj':page_obj
    }
    return render(request,'userspage/movies_by_genre.html',context)

def movie_details(request,movieId):
    movie=get_object_or_404(Movie,id=movieId)

    is_favorite=False
    if request.user.is_authenticated:
        is_favorite=Favorite.objects.filter(user=request.user, movie=movie).exists()
    
    in_watchlist=False
    if request.user.is_authenticated:
        in_watchlist=Watchlist.objects.filter(user=request.user,movie=movie).exists()
    #recommendation algorithm
    recommended_movies= get_similar_movies(movie)
    
    context={
        'movie':movie,
        'recommended_movies':recommended_movies,
        'is_favorite':is_favorite,
        'in_watchlist':in_watchlist,
    }
    return render(request,'userspage/movie_details.html',context)

def watch_movie(request,movieId):
    movie=get_object_or_404(Movie,id=movieId)
    
    #Log watch movies
    if request.user.is_authenticated:
        WatchHistory.objects.get_or_create(user=request.user,movie=movie)

    recommendations=get_similar_movies(movie)
    context={
        'movie':movie,
        'recommended_movies':recommendations,
        'MEDIA_URL': settings.MEDIA_URL
    }
    return render(request,'userspage/watch_movie.html',context)

def movie_search(request):
    query = request.GET.get('query','')
    selected_genres = request.GET.getlist('genres')
    movies= Movie.objects.all()
    
    if query:
        movies = movies.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) 
        ).distinct()

    if selected_genres:
        movies = movies.filter(genres__id__in=selected_genres).distinct()
    
    paginator = Paginator(movies,10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context={
        'query':query,
        'page_obj':page_obj,
        'selected_genres':list(map(int,selected_genres)),
    }
    return render(request, 'userspage/search_result.html', context)

#######################
#######################
def get_similar_movies(current_movie, limit=5):
    all_movies = Movie.objects.exclude(id=current_movie.id)

    current_year=timezone.now().year
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
###########################
###########################

@login_required
@user_only
def user_profile_view(request):
    profile = UserProfile.objects.get(user=request.user)
    history = WatchHistory.objects.filter(user=request.user)[:10]
    favorites = Favorite.objects.filter(user=request.user).select_related('movie')

    context={
        'profile':profile,
        'watch_history':history,
        'favorite_movies':favorites,
    }
    return render(request, 'userspage/user_profile.html',context)


@login_required
@user_only
def edit_profile_pic(request, username):
    user_profile = get_object_or_404(UserProfile, user__username=username)

    if request.method == 'POST' and request.FILES.get('userImage'):
        new_image = request.FILES['userImage']
        
        if (
            user_profile.profile_picture
            and user_profile.profile_picture.name != 'profile_pictures/default_icon.png'
            and os.path.exists(user_profile.profile_picture.path)
        ):
            os.remove(user_profile.profile_picture.path)

        user_profile.profile_picture = new_image
        user_profile.save()
        messages.success(request, "Profile image updated successfully!")

    return redirect('user-profile')


@login_required
@user_only
def edit_profile_bio(request, username):
    user_profile = get_object_or_404(UserProfile, user__username=username)

    if request.method == 'POST':
        new_bio = request.POST.get('bio')
        if new_bio:
            user_profile.bio = new_bio
            user_profile.save()
            messages.success(request, "Bio updated successfully!")

    return redirect('user-profile')


@login_required
def toggle_favorite(request, movieId):
    movie = get_object_or_404(Movie, id=movieId)
    favorite, created = Favorite.objects.get_or_create(user=request.user, movie=movie)

    if not created:
        # already exists → remove
        favorite.delete()
        messages.error(request, f"Removed {movie.title} from favorites.")
    else:
        messages.success(request, f"Added {movie.title} to favorites.")

    return redirect('movie-details', movieId=movie.id)

@login_required
@user_only
def my_watchlist(request):
    profile = UserProfile.objects.get(user=request.user)
    # All movies the user has watched
    watched_movies = WatchHistory.objects.filter(user=request.user).select_related('movie')

    # Movies in Watchlist but not yet watched
    plan_to_watch = Watchlist.objects.filter(user=request.user).exclude(
        movie__in=[w.movie for w in watched_movies]
    ).select_related('movie')
    context = {
        'profile':profile,
        'watched_movies': watched_movies,
        'plan_to_watch': plan_to_watch,
    }
    return render(request, 'userspage/watchlist.html', context)

@login_required
@user_only
def add_to_watchlist(request, movieId):
    movie = get_object_or_404(Movie, id=movieId)
    Watchlist.objects.get_or_create(user=request.user, movie=movie)
    messages.error(request, "You need an account to perform this action!")
    return redirect('movie-details', movieId=movie.id)

@login_required
def remove_from_watched(request, history_id):
    # Get the WatchHistory entry
    watched = get_object_or_404(WatchHistory, id=history_id, user=request.user)
    Watchlist.objects.filter(user=request.user, movie=watched.movie).delete()
    watched.delete()
    return redirect('watchlist')