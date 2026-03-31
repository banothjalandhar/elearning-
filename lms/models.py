from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify


class Subject(models.Model):
    name = models.CharField(max_length=120, unique=True)
    description = models.TextField(blank=True)
    slug = models.SlugField(max_length=140, unique=True, blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("lms:subject_detail", args=[self.slug])


class Topic(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="topics")
    name = models.CharField(max_length=150)
    order = models.PositiveIntegerField(default=1)
    slug = models.SlugField(max_length=170, blank=True)

    class Meta:
        ordering = ["subject__name", "order", "name"]
        unique_together = ("subject", "name")

    def __str__(self):
        return f"{self.subject.name} - {self.name}"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class SubTopic(models.Model):
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name="subtopics")
    name = models.CharField(max_length=150)
    order = models.PositiveIntegerField(default=1)
    slug = models.SlugField(max_length=170, blank=True)

    class Meta:
        ordering = ["topic__order", "order", "name"]
        unique_together = ("topic", "name")

    def __str__(self):
        return f"{self.topic.name} - {self.name}"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Content(models.Model):
    subtopic = models.ForeignKey(SubTopic, on_delete=models.CASCADE, related_name="contents")
    theory = models.TextField()
    example = models.TextField(blank=True)
    explanation = models.TextField(blank=True)
    sample_code = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["subtopic__order", "id"]

    def __str__(self):
        return f"Content for {self.subtopic}"


class TopicTest(models.Model):
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name="tests")
    title = models.CharField(max_length=200)
    duration = models.PositiveIntegerField(help_text="Duration in minutes")

    class Meta:
        ordering = ["topic__subject__name", "topic__order", "title"]

    def __str__(self):
        return self.title


class Question(models.Model):
    test = models.ForeignKey(TopicTest, on_delete=models.CASCADE, related_name="questions")
    question_text = models.TextField()
    option1 = models.CharField(max_length=255)
    option2 = models.CharField(max_length=255)
    option3 = models.CharField(max_length=255)
    option4 = models.CharField(max_length=255)
    correct_option = models.PositiveSmallIntegerField(choices=[(1, "Option 1"), (2, "Option 2"), (3, "Option 3"), (4, "Option 4")])

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return f"{self.test.title} - Q{self.pk}"

    @property
    def options(self):
        return [
            (1, self.option1),
            (2, self.option2),
            (3, self.option3),
            (4, self.option4),
        ]


class UserAnswer(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="topic_user_answers")
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="user_answers")
    selected_option = models.PositiveSmallIntegerField(choices=[(1, "Option 1"), (2, "Option 2"), (3, "Option 3"), (4, "Option 4")])

    class Meta:
        unique_together = ("user", "question")

    def __str__(self):
        return f"{self.user} - {self.question}"


class TestResult(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="topic_test_results")
    test = models.ForeignKey(TopicTest, on_delete=models.CASCADE, related_name="results")
    score = models.PositiveIntegerField(default=0)
    total = models.PositiveIntegerField(default=0)
    completed_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-completed_at"]

    def __str__(self):
        return f"{self.user} - {self.test} - {self.score}/{self.total}"


class UserProgress(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="topic_progress")
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name="progress_records")
    completed = models.BooleanField(default=False)
    score = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ("user", "topic")
        ordering = ["topic__subject__name", "topic__order"]

    def __str__(self):
        return f"{self.user} - {self.topic}"


class Batch(models.Model):
    name = models.CharField(max_length=150)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="batches")
    start_date = models.DateField()

    class Meta:
        ordering = ["subject__name", "start_date", "name"]

    def __str__(self):
        return self.name


class ScheduledExam(models.Model):
    title = models.CharField(max_length=200)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="scheduled_exams")
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE, related_name="scheduled_exams")
    topic_test = models.ForeignKey(TopicTest, on_delete=models.SET_NULL, null=True, blank=True, related_name="scheduled_instances")
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    class Meta:
        ordering = ["start_time"]

    def __str__(self):
        return self.title

    def clean(self):
        if self.end_time <= self.start_time:
            raise ValidationError({"end_time": "End time must be after the start time."})
        if self.batch_id and self.subject_id and self.batch.subject_id != self.subject_id:
            raise ValidationError({"batch": "Batch subject must match the scheduled exam subject."})
        if self.topic_test_id and self.subject_id and self.topic_test.topic.subject_id != self.subject_id:
            raise ValidationError({"topic_test": "Linked test subject must match the scheduled exam subject."})

    @property
    def is_active_now(self):
        now = timezone.now()
        return self.start_time <= now <= self.end_time


class CodeSubmission(models.Model):
    class Language(models.TextChoices):
        PYTHON = "python", "Python"
        JAVA = "java", "Java"
        JAVASCRIPT = "javascript", "JavaScript"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="code_submissions")
    subtopic = models.ForeignKey(SubTopic, on_delete=models.CASCADE, related_name="code_submissions")
    language = models.CharField(max_length=20, choices=Language.choices, default=Language.PYTHON)
    code = models.TextField(blank=True)
    output = models.TextField(blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("user", "subtopic")
        ordering = ["-updated_at"]

    def __str__(self):
        return f"{self.user} - {self.subtopic}"
