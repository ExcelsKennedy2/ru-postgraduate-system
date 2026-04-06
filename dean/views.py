from django.shortcuts import render


# Create your views here.
def dean_dashboard(request):
    return render(request, 'dean/dean.html')