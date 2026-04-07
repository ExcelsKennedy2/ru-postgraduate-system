from django.urls import path

from .views import chair_approve_request, chair_dashboard, chair_reassign_students

urlpatterns = [
    path('', chair_dashboard, name='chair_dashboard'),
    path('approve/<int:submission_id>/', chair_approve_request, name='chair_approve_request'),
    path('reassign-students/', chair_reassign_students, name='chair_reassign_students'),
]
