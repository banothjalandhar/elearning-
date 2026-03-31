from django.urls import path

from . import views


app_name = "placement"

urlpatterns = [
    path("", views.job_list, name="job_list"),
    path("jobs/<int:job_id>/", views.job_detail, name="job_detail"),
    path("jobs/<int:job_id>/apply/", views.apply_job, name="apply_job"),
    path("mock-interviews/", views.mock_interview_list, name="mock_interview_list"),
]

