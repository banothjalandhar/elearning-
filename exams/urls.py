from django.urls import path

from . import views

app_name = "exams"

urlpatterns = [
    path("", views.exam_list, name="exam_list"),
    path("upload-excel/", views.upload_exam_excel, name="upload_exam_excel"),
    path("start/<int:id>/", views.start_exam, name="exam_start"),
    path("question/<int:id>/", views.exam_question, name="exam_question"),
    path("autosave/<int:id>/", views.autosave_answer, name="exam_autosave"),
    path("warning/<int:id>/", views.record_warning, name="exam_warning"),
    path("submit/", views.submit_exam, name="exam_submit"),
    path("result/", views.exam_result, name="exam_result"),
    path("history/", views.exam_history, name="exam_history"),
    path("admin/exams/create/", views.admin_exam_create, name="admin_exam_create"),
    path("admin/questions/create/", views.admin_question_create, name="admin_question_create"),
]
