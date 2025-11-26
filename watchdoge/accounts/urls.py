from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

# app_name = "accounts"

urlpatterns=[
    path('login/',views.loginUser ,name='login'),
    path('register/',views.registerUser, name='register'),
    path('verify/<uidb64>/<token>/', views.verify_email,name='verify-email'),
    path('logout/',views.logoutUser, name='logout'),
    path('delete-user/<int:userId>/',views.delete_user,name='delete-user'),
    path('edit-user/<int:userId>/',views.edit_user,name='admin-edit-user'),
    path('forgot-password/', auth_views.PasswordResetView.as_view(
        template_name='accounts/password_reset_form.html'
    ), name='password_reset'),

    path('forgot-password/sent/', auth_views.PasswordResetDoneView.as_view(
        template_name='accounts/password_reset_done.html'
    ), name='password_reset_done'),

    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='accounts/password_reset_confirm.html'
    ), name='password_reset_confirm'),

    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='accounts/password_reset_complete.html'
    ), name='password_reset_complete'),
    # path('token/',views.token_send,name='token-send'),
    # path('success/',views.success,name='success')
]
