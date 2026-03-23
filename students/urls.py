from django.urls import path
from .views import student_dashboard, submissions_api, download_submission, download_all_submissions, book_presentation

urlpatterns = [
    path('dashboard/', student_dashboard, name='student_dashboard'),
    path('api/submissions/', submissions_api, name='submissions_api'),
    # path('submissions/<int:submission_id>/download/', download_submission, name='download_submission'),
    # path('submissions/download-all/', download_all_submissions, name='download_all_submissions'),
    path('book-presentation/', book_presentation, name='book_presentation'),
]