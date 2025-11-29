# tasks.py
from celery import shared_task
from .models import Movie
from django.conf import settings
from .utils import delete_original_after_conversion
import os
import subprocess
import time
import getpass

FFMPEG_PATH = r"C:\ffmpeg\bin\ffmpeg.exe"

@shared_task(bind=True)
def convert_movie_to_hls(self, movie_id):
    """
    Celery task to convert uploaded movie into HLS.
    Windows-safe:
    - Uses absolute paths for FFmpeg, input, output
    - Adds short delay to avoid file locks
    - Updates movie.status in DB: uploaded -> processing -> ready/failed
    """
    try:
        # Fetch movie
        movie = Movie.objects.get(id=movie_id)
        input_file = os.path.abspath(movie.file.path)

        # Double check file exists
        if not os.path.exists(input_file):
            print(f"[TASK] Input file missing for movie {movie_id}, retrying in 2s...")
            time.sleep(2)
            if not os.path.exists(input_file):
                raise FileNotFoundError(f"File not found: {input_file}")

        # Output directory for HLS files
        output_dir = os.path.join(settings.MEDIA_ROOT, "movies", "hls", str(movie_id))
        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.abspath(os.path.join(output_dir, "index.m3u8"))

        # Update status → processing
        movie.status = "processing"
        movie.save(update_fields=["status"])
        print(f"[TASK] Movie {movie.id} status set to PROCESSING (user: {getpass.getuser()})")

        # Small delay to avoid Windows file lock issues
        time.sleep(1)

        # FFmpeg command
        cmd = [
            FFMPEG_PATH,
            "-y",
            "-i", input_file,
            "-c:v", "libx264",        # Re-encode video
            "-preset", "veryfast",    # Optional speed
            "-profile:v", "main",
            "-level", "4.0",
            "-c:a", "aac",
            "-b:a", "128k",
            "-start_number", "0",
            "-hls_time", "6",
            "-hls_list_size", "0",
            "-hls_segment_filename", os.path.join(output_dir, "segment_%03d.ts"),
            "-f", "hls",
            output_file
        ]


        print(f"[TASK] Running FFmpeg for movie {movie.id}")
        subprocess.run(cmd, check=True)

        # Conversion succeeded
        rel_path = os.path.relpath(output_file, settings.MEDIA_ROOT).replace("\\", "/")
        movie.hls_path = rel_path
        movie.status = "ready"
        movie.save(update_fields=["status", "hls_path"])
        print(f"[TASK] Movie {movie.id} conversion completed. Status set to READY.")

        # Delete original file after successful conversion
        delete_original_after_conversion(movie)


    except Exception as e:
        try:
            movie = Movie.objects.get(id=movie_id)
            movie.status = "failed"
            movie.save(update_fields=["status"])
            print(f"[TASK] Movie {movie.id} conversion FAILED: {str(e)}")

            # 🧹 Cleanup: remove empty HLS folder if FFmpeg didn’t produce output
            output_dir = os.path.join(settings.MEDIA_ROOT, "movies", "hls", str(movie_id))
            if os.path.isdir(output_dir) and not os.listdir(output_dir):
                os.rmdir(output_dir)
                print(f"[CLEANUP] Removed empty HLS folder: {output_dir}")

        except Movie.DoesNotExist:
            print(f"[TASK] Failed movie {movie_id} not found in DB.")
        raise e

