from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth import get_user_model,authenticate,login,logout
from django.contrib import messages
from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.http import Http404

def index(request):
    return render(request,'index.html')


from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.views.decorators.cache import never_cache

@never_cache
def login_user(request):
    if request.user.is_authenticated:
        return redirect('chatHomepage')

    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')
        next_url = request.POST.get('next')  # Retrieve 'next' parameter from the POST data

        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, "You have been successfully logged in.")
            
            # Redirect to 'next' URL or default to 'chatHomepage'
            return redirect(next_url or 'chatHomepage')
        else:
            messages.error(request, "Invalid username or password.")
            return redirect('login')
    else:
        next_url = request.GET.get('next')  # Retrieve 'next' parameter from the URL
        return render(request, 'login.html', {'next': next_url})



@never_cache
def register(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm-password')


        if not name or not email or not password or not confirm_password:
            messages.error(request, "All fields are required.")
        elif password != confirm_password:
            messages.error(request, "Passwords do not match.")
        else:
            Account = get_user_model()
            if Account.objects.filter(email=email).exists():
                messages.error(request, "An account with this email already exists.")
            else:
                try:
                    user = Account.objects.create_user(name=name, email=email, password=password)
                    messages.success(request, "Registration successful. Please log in.")
                    return redirect('login')  
                except Exception as e:
                    messages.error(request, f"An error occurred during registration: {str(e)}")

    return render(request, 'register.html')


def logout_user(request):
    logout(request)
    messages.success(request, "You have been successfully logged out.")
    return redirect('login')


from django.shortcuts import redirect

@login_required
def profile_view(request, name=None):
    Account = get_user_model()

    if name and name != "None":
        user = get_object_or_404(Account, name=name)
        profile = user.profile
    else:
        profile = request.user.profile
        if not profile.user.name:
            # Set display_name as name if the user doesn't have a name
            profile.user.name = profile.display_name or profile.user.username
            profile.user.save()

        # Redirect to the correct profile URL with the name
        return redirect('profile_view', name=profile.user.name)
    
    return render(request, 'profile.html', {'profile': profile})



@login_required
def profile_edit_view(request):
    profile = request.user.profile
    if request.method == 'POST':
        profile.display_name = request.POST.get('display_name', '')
        profile.info = request.POST.get('info', '')
        if 'image' in request.FILES:
            profile.image = request.FILES['image']
        profile.save()
        return redirect('profile', name=profile.user.name)  # Pass the name parameter

    context = {
        'profile': profile,
    }
    return render(request, 'profile_edit.html', context)



@login_required
def profile_settings_view(request):
    profile = request.user.profile
    context = {
        'profile': profile,
    }
    return render(request,'profile_settings.html',context)


@login_required
def profile_delete_view(request):
    profile = request.user.profile
    user = request.user
    if request.method == 'POST':
        logout(request)
        user.delete()
        messages.success(request,'Account Deleted,what a pity!')
        return redirect('index')
    context = {
        'profile': profile,
    }
    return render(request,'profile_delete.html',context)