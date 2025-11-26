# Django Movie Streaming Platform

A full-featured movie streaming web application built using Python (Django).
The platform supports video uploading, automatic HLS conversion, user accounts, watchlists, favorites, and more.

## Features

### Movie Management
- Upload movies with poster, title, description, genres, duration, and release year
- Automatic video conversion to HLS (.m3u8) using Celery and FFmpeg
- Poster and video file cleanup on update
- Genre-based filtering and content-based recommendations

### User Features
- User registration and login
- Watchlist (add/remove movies)
- Favorite movies
- (Upcoming) User reviews and ratings

### Admin Features
- Custom admin dashboard
- Movie CRUD operations
- Upload and processing status
- Duplicate movie and genre prevention
- Sorted and clean genre naming
- Separate profile update forms (profile picture and bio)

### Technical Details
- Django backend with Crispy Forms
- HLS streaming for adaptive playback
- Background tasks handled by Celery + Redis
- Organized media file management
- Content-based recommendation engine (genre + title similarity)

## Project Structure

```

VSS/
│
├── venv/
├── watchdoge/
│   ├── streaming/
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── utils.py
│   │   ├── templates/
│   │   └── ...
│   ├── userspage/
│   │   ├── views.py
│   │   ├── forms.py
│   │   └── ...
│   ├── manage.py
│   └── ...
└── README.md

```

## Installation and Setup

### 1. Clone the repository

```
git clone <your-repo-url>
cd VSS
````

### 2. Create a virtual environment

```
python -m venv venv
```

Activate it:

Windows:

```
venv\Scripts\activate
```

Linux/Mac:

```
source venv/bin/activate
```

### 3. Install required packages

```
pip install -r requirements.txt
```

### 4. Run migrations

```
python manage.py migrate
```

### 5. Start the development server

```
python manage.py runserver
```

## Video Processing (HLS Conversion)

When a video is uploaded:

1. File is saved to `media/movies/files/`
2. Celery detects the upload
3. FFmpeg converts the video to HLS (.m3u8 + .ts segments)
4. The converted playlist is streamed through the player

## Key Dependencies

* Django
* django-crispy-forms
* Celery
* Redis
* FFmpeg (system dependency)

## Future Improvements

* Add user reviews and ratings
* Advanced recommendation engine
* Admin analytics dashboard
* Subtitles (VTT upload)
* Deployment configuration

## License

This project is for educational and portfolio use.

```
