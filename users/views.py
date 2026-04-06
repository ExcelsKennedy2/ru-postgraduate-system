from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.urls import reverse
from urllib.parse import urlparse
from .models import User


def is_safe_url(url, allowed_host=None):
    """Validate that the URL is safe for redirects (prevents open redirect)."""
    if not url:
        return False
    parsed = urlparse(url)
    # Only allow relative URLs (no domain specified)
    return parsed.netloc == '' or parsed.netloc == allowed_host


def login_view(request):
    if request.method == "POST":
        unique_id = request.POST.get('unique_id')
        password = request.POST.get('password')
        next_url = request.POST.get('next', '')

        try:
            user_obj = User.objects.get(unique_id=unique_id)
            user = authenticate(request, username=user_obj.username, password=password)
        except User.DoesNotExist:
            user = None

        if user is not None:
            login(request, user)

            # If 'next' parameter exists and is safe, redirect there
            if next_url and is_safe_url(next_url, allowed_host=request.get_host()):
                return redirect(next_url)
            
            # Otherwise, redirect based on role
            if user.role == 'student':
                return redirect('/students/dashboard/')
            elif user.role == 'supervisor':
                return redirect('/supervisor/dashboard/')
            elif user.role in ['admin', 'dean']:  # admin and dean go to admin site
                return redirect('/admin/')
            else:
                return redirect('/')
        else:
            messages.error(request, "Invalid Admission Number/Staff ID or Password")

    return render(request, 'users/login.html')


def logout_view(request):
    logout(request)
    return redirect('login')  # Redirect to your login page
