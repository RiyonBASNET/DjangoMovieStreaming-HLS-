from django.shortcuts import redirect
from django.contrib import messages


def unauthenticated_user(view_function):
    def wrapper_function(request,*args,**kwargs):
        if request.user.is_authenticated:
            messages.add_message(request,messages.ERROR,"Login required!")
            return redirect('/')
        else:
            return view_function(request,*args,**kwargs)
    return wrapper_function

def admin_only(view_function):
    def wrapper_function(request,*args,**kwargs):
        if request.user.is_authenticated and request.user.is_staff:
            return view_function(request,*args,**kwargs)
        else:
            messages.add_message(request,messages.ERROR,"Admin login required!")
            return redirect('/account/login')
    return wrapper_function


def user_only(view_function):
    def wrapper_function(request,*args,**kwargs):
        if request.user.is_staff:
            messages.add_message(request,messages.SUCCESS,"You can not view this page. Limited to Users.")
            return redirect('/movie-admin/')
        else:
            return view_function(request,*args,**kwargs)
    return wrapper_function