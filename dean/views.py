from django.shortcuts import render
from .views import dean_dashboard

# Create your views here.
def dean_dashboard(request):
    return render(request, 'dean/dean.html')