from django.contrib import admin

from .models import (
    Batch,
    CodeSubmission,
    Content,
    Question,
    ScheduledExam,
    Subject,
    SubTopic,
    TestResult,
    Topic,
    TopicTest,
    UserAnswer,
    UserProgress,
)


class ContentInline(admin.StackedInline):
    model = Content
    extra = 1


class SubTopicInline(admin.TabularInline):
    model = SubTopic
    extra = 1


class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ("name", "topic_count", "batch_count")
    search_fields = ("name", "description")
    prepopulated_fields = {"slug": ("name",)}

    def topic_count(self, obj):
        return obj.topics.count()

    def batch_count(self, obj):
        return obj.batches.count()


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ("name", "subject", "order", "test_count")
    list_filter = ("subject",)
    search_fields = ("name", "subject__name")
    ordering = ("subject", "order")
    inlines = [SubTopicInline]

    def test_count(self, obj):
        return obj.tests.count()


@admin.register(SubTopic)
class SubTopicAdmin(admin.ModelAdmin):
    list_display = ("name", "topic", "order")
    list_filter = ("topic__subject", "topic")
    search_fields = ("name", "topic__name")
    ordering = ("topic", "order")
    inlines = [ContentInline]


@admin.register(Content)
class ContentAdmin(admin.ModelAdmin):
    list_display = ("subtopic", "updated_at")
    list_filter = ("subtopic__topic__subject",)
    search_fields = ("subtopic__name", "theory", "example", "explanation", "sample_code")


@admin.register(TopicTest)
class TopicTestAdmin(admin.ModelAdmin):
    list_display = ("title", "topic", "duration", "question_total")
    list_filter = ("topic__subject", "topic")
    search_fields = ("title", "topic__name")
    inlines = [QuestionInline]

    def question_total(self, obj):
        return obj.questions.count()


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("test", "question_text", "correct_option")
    list_filter = ("test__topic__subject", "test")
    search_fields = ("question_text", "test__title")


@admin.register(UserAnswer)
class UserAnswerAdmin(admin.ModelAdmin):
    list_display = ("user", "question", "selected_option")
    list_filter = ("question__test__topic__subject",)
    search_fields = ("user__email", "question__question_text")


@admin.register(TestResult)
class TestResultAdmin(admin.ModelAdmin):
    list_display = ("user", "test", "score", "total", "completed_at")
    list_filter = ("test__topic__subject", "test")
    search_fields = ("user__email", "test__title")


@admin.register(UserProgress)
class UserProgressAdmin(admin.ModelAdmin):
    list_display = ("user", "topic", "completed", "score")
    list_filter = ("completed", "topic__subject")
    search_fields = ("user__email", "topic__name")


@admin.register(Batch)
class BatchAdmin(admin.ModelAdmin):
    list_display = ("name", "subject", "start_date")
    list_filter = ("subject",)
    search_fields = ("name", "subject__name")


@admin.register(ScheduledExam)
class ScheduledExamAdmin(admin.ModelAdmin):
    list_display = ("title", "subject", "batch", "start_time", "end_time", "topic_test")
    list_filter = ("subject", "batch")
    search_fields = ("title", "subject__name", "batch__name")


@admin.register(CodeSubmission)
class CodeSubmissionAdmin(admin.ModelAdmin):
    list_display = ("user", "subtopic", "language", "updated_at")
    list_filter = ("language", "subtopic__topic__subject")
    search_fields = ("user__email", "subtopic__name", "code")
