from django.urls import path

from . import views


app_name = "classroom"

urlpatterns = [
    path("", views.class_list, name="class_list"),
    path("whiteboard/", views.whiteboard, name="whiteboard"),
    path("<int:id>/join/", views.join_class, name="join_class"),
    path("<int:id>/notes/", views.download_notes, name="download_notes"),
    path("<int:id>/recording/", views.watch_recording, name="watch_recording"),
    path("<int:id>/", views.class_detail, name="class_detail"),
]
