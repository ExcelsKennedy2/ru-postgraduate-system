# from django.shortcuts import render, redirect
# from django.contrib.auth import authenticate, login
# from django.contrib import messages
# from .models import User

# def login_view(request):
#     if request.method == "POST":
#         # email = request.POST.get('email')
#         unique_id = request.POST.get('unique_id')
#         password = request.POST.get('password')

#         try:
#             user_obj = User.objects.get(unique_id=unique_id)
#             user = authenticate(request, username=user_obj.username, password=password)
#         except User.DoesNotExist:
#             user = None
#         password = request.POST.get('password')

#         # Lookup user by email (since you want email login)
#         try:
#             user_obj = User.objects.get(email=email)
#             user = authenticate(request, username=user_obj.username, password=password)
#         except User.DoesNotExist:
#             user = None

#         if user is not None:
#             login(request, user)
#             # Redirect based on role
#             if user.role == 'student':
#                 return redirect('/students/dashboard/')
#             else:
#                 return redirect('/staff/dashboard/')
#         else:
#             messages.error(request, "Invalid credentials")

#     return render(request, 'users/login.html')

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from .models import User

def login_view(request):
    if request.method == "POST":
        unique_id = request.POST.get('unique_id')
        password = request.POST.get('password')

        try:
            user_obj = User.objects.get(unique_id=unique_id)
            user = authenticate(request, username=user_obj.username, password=password)
        except User.DoesNotExist:
            user = None

        if user is not None:
            login(request, user)

            if user.role == 'student':
                return redirect('/students/dashboard/')
            else:
                return redirect('/supervisor/dashboard/')
        else:
            messages.error(request, "Invalid Admission Number/Staff ID or Password")

    return render(request, 'users/login.html')

from django.contrib.auth import logout

def logout_view(request):
    logout(request)
    return redirect('login')  # Redirect to your login page