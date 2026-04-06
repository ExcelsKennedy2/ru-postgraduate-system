from django.urls import path
from .views import supervisor_dashboard, review_quarterly_report

urlpatterns = [
    path('dashboard/', supervisor_dashboard, name='supervisor_dashboard'),
    path('review-report/<int:pk>/', review_quarterly_report, name='review_quarterly_report'),
]