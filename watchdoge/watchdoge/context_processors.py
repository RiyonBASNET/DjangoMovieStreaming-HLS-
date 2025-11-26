from streaming.models import Genre

def genres_list(request):
    genres = Genre.objects.all()
    return {'all_genres':genres}