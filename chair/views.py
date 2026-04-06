from django.shortcuts import render

# Create your views here.
def chair_dashboard(request):
    return render(request, 'dean/chair.html')