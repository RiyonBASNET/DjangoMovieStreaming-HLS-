from django.urls import reverse
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from .tokens import email_verification_token
import os
import uuid

def user_profile_picture_upload_path(instance, filename):
    ext = os.path.splitext(filename)[1]  # Keeps original extension
    unique_filename = f"{uuid.uuid4()}{ext}"
    return f"profile_pictures/users/user_{instance.user.id}/{unique_filename}"




def send_verification_email(request, user):
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = email_verification_token.make_token(user)

    verify_url = request.build_absolute_uri(
        reverse('verify-email', kwargs={"uidb64": uid, "token": token})
    )

    subject = "Verify Your Account"
    message = f"Hello {user.username},\nPlease verify your account:\n{verify_url}"

    send_mail(subject, message, None, [user.email])

    print("Verification URL:", verify_url)

