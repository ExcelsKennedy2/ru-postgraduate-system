from django.urls import path
from .views import dean_dashboard

urlpatterns = [
    path('', dean_dashboard, name='dean_dashboard'),
]