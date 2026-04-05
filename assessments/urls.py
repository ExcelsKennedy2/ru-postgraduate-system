from django.urls import path
from .views import submit_work, give_feedback

urlpatterns = [
    path('submit/', submit_work, name='submit_work'),
    path('feedback/', give_feedback, name='give_feedback'),
]