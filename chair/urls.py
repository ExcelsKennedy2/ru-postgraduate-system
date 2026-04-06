from django.urls import path
from .views import chair_dashboard

urlpatterns = [
    path('', chair_dashboard, name='chair_dashboard'),
]