# ai_module/urls.py

from django.urls import path
from .views import process_transcript

urlpatterns = [
    path("process-transcript/", process_transcript),
]