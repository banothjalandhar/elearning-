import csv

from django.contrib import admin
from django.http import HttpResponse
from django.urls import reverse
from django.utils.html import format_html

from .models import Exam, Option, Question, Result, StudentAnswer, StudentExam


class OptionInline(admin.TabularInline):
    model = Option
    extra = 2


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("id", "exam", "question_type", "marks")
    list_filter = ("question_type", "exam__category")
    search_fields = ("question_text", "exam__title")
    inlines = [OptionInline]


@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = (
        "course",
        "title",
        "category",
        "duration",
        "total_marks",
        "is_active",
        "available_from",
        "available_until",
        "created_at",
        "upload_questions_link",
    )
    list_filter = ("category", "is_active", "course")
    search_fields = ("title", "course__title")

    def upload_questions_link(self, obj):
        url = reverse("exams:upload_exam_excel")
        return format_html('<a class="button" href="{}?exam={}">Upload Excel</a>', url, obj.pk)

    upload_questions_link.short_description = "Excel Import"


@admin.register(Option)
class OptionAdmin(admin.ModelAdmin):
    list_display = ("question", "option_text", "is_correct")
    list_filter = ("is_correct",)
    search_fields = ("option_text", "question__question_text")


def export_results_csv(modeladmin, request, queryset):
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="exam_results.csv"'
    writer = csv.writer(response)
    writer.writerow(["Student", "Email", "Exam", "Category", "Score", "Passed", "Created At"])
    for result in queryset.select_related("student", "exam"):
        writer.writerow(
            [
                result.student.username,
                result.student.email,
                result.exam.title,
                result.exam.get_category_display(),
                result.score,
                result.passed,
                result.created_at,
            ]
        )
    return response


export_results_csv.short_description = "Export selected results as CSV"


@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    list_display = ("student", "exam", "score", "passed", "created_at")
    list_filter = ("passed", "exam__category")
    search_fields = ("student__username", "student__email", "exam__title")
    actions = [export_results_csv]


@admin.register(StudentExam)
class StudentExamAdmin(admin.ModelAdmin):
    list_display = ("student", "exam", "score", "submitted", "warning_count", "auto_submitted")
    list_filter = ("submitted", "auto_submitted", "exam__category")
    search_fields = ("student__username", "student__email", "exam__title")


@admin.register(StudentAnswer)
class StudentAnswerAdmin(admin.ModelAdmin):
    list_display = ("student_exam", "question", "selected_option", "programming_language")
    search_fields = ("student_exam__student__username", "question__question_text")
