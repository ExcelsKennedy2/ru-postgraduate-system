from django.urls import path
from .views import home, review_quarterly_report

urlpatterns = [
    path('dashboard/', home, name='supervisor_dashboard'),
    path('review-report/<int:pk>/', review_quarterly_report, name='review_quarterly_report'),
]