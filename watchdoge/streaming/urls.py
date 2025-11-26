from django.urls import path

from . import views

urlpatterns=[
    path('',views.dashboard, name='admin-dashboard'),
    path('movies/',views.showMovies, name='admin-movies-list'),
    path('genres/',views.showGenres, name='admin-genres-list'),
    path('uploadMovie/',views.upload_movie, name='upload-movie'),
    path('addGenre/',views.add_genre, name='add-genre'),
    path('deleteGenre/<int:genreId>/', views.deleteGenre, name='delete-genre'),
    path('deleteMovie/<int:movieId>/', views.deleteMovie, name='delete-movie'),
    path('movieDetails/<int:movieId>/',views.movie_details, name='admin-movie-details'),
    path('editMovie/<int:movieId>/',views.editMovie,name='admin-edit-movie'),
    path('editGenre/<int:genreId>/',views.editGenre,name='admin-edit-genre'),
    path('users-list/',views.users_list,name='admin-users-list'),

]


