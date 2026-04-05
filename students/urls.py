from django.urls import path
from .views import student_dashboard, submissions_api, download_submission, download_all_submissions, book_presentation, list_quarterly_reports, create_quarterly_report, detail_quarterly_report, update_quarterly_report, submit_quarterly_report

urlpatterns = [
    path('dashboard/', student_dashboard, name='student_dashboard'),
    path('api/submissions/', submissions_api, name='submissions_api'),
    path('submissions/<int:submission_id>/download/', download_submission, name='download_submission'),
    path('submissions/download-all/', download_all_submissions, name='download_all_submissions'),
    path('book-presentation/', book_presentation, name='book_presentation'),
    path('reports/', list_quarterly_reports, name='list_quarterly_reports'),
    path('reports/create/', create_quarterly_report, name='create_quarterly_report'),
    path('reports/<int:pk>/', detail_quarterly_report, name='detail_quarterly_report'),
    path('reports/<int:pk>/edit/', update_quarterly_report, name='update_quarterly_report'),
    path('reports/<int:pk>/submit/', submit_quarterly_report, name='submit_quarterly_report'),
]