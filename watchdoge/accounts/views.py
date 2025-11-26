from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import get_user_model
from .forms import LoginForm, UserEditForm, UserRegistrationForm, UserProfileForm

# from django.conf import settings
# from django.core.mail import send_mail
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from .auth import admin_only
from .utils import send_verification_email
from django.utils.http import urlsafe_base64_decode
from .tokens import email_verification_token

def registerUser(request):

    if request.method =='POST':
        form = UserRegistrationForm(request.POST)

        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()

            send_verification_email(request, user)

            messages.add_message(request,messages.SUCCESS,'User registration successful! Please check your email to verify.')
            return redirect('login')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
                   

    return render(request,'accounts/register.html',{
        'form':UserRegistrationForm()
    })

def verify_email(request,uidb64,token):
    User = get_user_model()

    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except:
        user = None
    
    if user and email_verification_token.check_token(user, token):
        user.is_active = True
        user.save()

        messages.success(request,"Email verified! You can now login.")
        return redirect("login")
    else:
        messages.error(request, "Verification link is invalid or expired.")
        return redirect("login")


def loginUser(request):
    if request.method =='POST':
        form = LoginForm(request.POST)
        
        if form.is_valid():
            data=form.cleaned_data
            user=authenticate(request,username=data['username'],password=data['password'])

            if user is not None:

                if not user.is_active:
                    messages.error(request,"Please verify your email before logging in.")
                    return redirect("login")
                
                login(request, user)
                
                if user.is_staff:
                    return redirect('/movie-admin/')
                else:
                    return redirect('/')
                
            else:
                messages.add_message(request,messages.ERROR,'User not found.')
                return render(request,'accounts/login.html',{'form':form})
    context={
        'form':LoginForm()
    }
    return render(request,'accounts/login.html',context)

def logoutUser(request):
    logout(request)

    return redirect('/')


@login_required
@admin_only
def delete_user(request,userId):
    user=get_object_or_404(User,id=userId)

    if user.is_staff:
        messages.error(request,"Unable to remove admin. Please discuss with other admins.")
    else:
        user.delete()
        messages.success(request,"User has been offed ;)")

    return redirect('admin-dashboard')

@login_required
@admin_only
def edit_user(request, userId):
    user = get_object_or_404(User, id=userId)
    if request.method == 'POST':
        form = UserEditForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "User updated successfully.")
            return redirect('admin-dashboard') 
        else:
            messages.error(request, "Please correct the error(s) below.")
    else:
        form = UserEditForm(instance=user)
    
    context = {
        'form': form,
        'edit_user': user,
    }
    return render(request, 'accounts/editUserInfo.html', context)


#################################
    # if request.method == 'POST':
    #     username = request.POST.get('username')
    #     email = request.POST.get('email')
    #     password = request.POST.get('password')

    #     try:
    #         if User.objects.filter(username=username).first():
    #             messages.add_message(request, messages.ERROR,
    #                              'username alredy exists')
    #             return redirect('/account/register')

    #         if User.objects.filter(email=email).first():
    #             messages.add_message(request, messages.ERROR,
    #                                 'email alredy exists')
    #             return redirect('/account/register')

    #         user_obj = User.objects.create(username=username, email=email)
    #         user_obj.set_password(password)
    #         user_obj.save()

    #         # auth_token = str(uuid.uuid4())

    #         # profile_obj = UserProfile.objects.create(
    #         #     user=user_obj, auth_token=auth_token)
    #         # profile_obj.save()

    #         # registration_mail(email,auth_token)

    #         # return redirect('/account/token')
            
    #     except Exception as e:
    #         print(e)
    
    # return render(request, 'accounts/register.html')

# def success(request):
#     return render(request, 'accounts/logSuccess.html')

# def token_send(request):
#     return render(request,'accounts/token_send.html')

# def registration_mail(email,token):
#     subject  = 'Registration Verification'
#     message = f'Thank you for registering. Please paste the link to verify your account; http://127.0.0.1:8000/account/varify/{token}'
#     email_from = settings.EMAIL_HOST_USER
#     receipient_list = {email}
#     send_mail(subject, message,email_from,receipient_list)