from django.urls import path

from . import views

app_name = "lms"

urlpatterns = [
    path("", views.subject_list, name="subject_list"),
    path("subject/<slug:subject_slug>/", views.subject_detail, name="subject_detail"),
    path("topic/<int:topic_id>/", views.topic_detail, name="topic_detail"),
    path("content/<int:subtopic_id>/", views.content_detail, name="content_detail"),
    path("editor/<int:subtopic_id>/", views.code_editor, name="code_editor"),
    path("tests/<int:test_id>/", views.topic_test_view, name="topic_test"),
    path("results/<int:result_id>/", views.result_view, name="result_view"),
    path("dashboard/", views.progress_dashboard, name="dashboard"),
    path("scheduled-exams/", views.scheduled_exam_list, name="scheduled_exam_list"),
    path("scheduled-exams/<int:exam_id>/", views.scheduled_exam_detail, name="scheduled_exam_detail"),
]
