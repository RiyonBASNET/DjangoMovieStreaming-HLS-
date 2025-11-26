from django.urls import path
from . import views

urlpatterns=[
    path('',views.home,name='home'),
    path('genres/',views.genres_list,name='genres-list'),
    path('movies/',views.movies_list,name='movies-list'),
    path('genre/<str:genreName>/',views.movies_by_genre, name='movies-by-genre'),
    path('movie/<int:movieId>/',views.movie_details,name='movie-details'),
    path('watch-movie/<int:movieId>/',views.watch_movie,name='watch-movie'),
    path('search/',views.movie_search,name='movie-search'),
    path('profile/',views.user_profile_view,name='user-profile'),
    path('profile/<str:username>/edit-pfp/',views.edit_profile_pic,name='edit-profile-pic'),
    path('profile/<str:username>/edit-bio/',views.edit_profile_bio,name='edit-profile-bio'),
    path('favorite/<int:movieId>', views.toggle_favorite, name='toggle-favorite'),
    path('watchlist/',views.my_watchlist, name='watchlist'),
    path('watchlist/add/<int:movieId>/', views.add_to_watchlist, name='add-to-watchlist'),
    path('watchlist/remove-watched/<int:history_id>/', views.remove_from_watched, name='remove-from-watched'),
]