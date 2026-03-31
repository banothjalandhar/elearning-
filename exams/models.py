from django.conf import settings
from django.db import models
from django.utils import timezone


class Exam(models.Model):
    class Category(models.TextChoices):
        DSA = "DSA", "DSA Round"
        ADSA = "ADSA", "ADSA Round"
        APTITUDE = "APTITUDE", "Aptitude Round"
        COMMUNICATION = "COMMUNICATION", "Communication Round"
        CODING = "CODING", "Coding Round"

    course = models.ForeignKey("courses.Course", on_delete=models.CASCADE, related_name="exams", null=True, blank=True)
    title = models.CharField(max_length=255)
    category = models.CharField(max_length=20, choices=Category.choices)
    duration = models.PositiveIntegerField(help_text="Duration in minutes")
    total_marks = models.PositiveIntegerField()
    is_active = models.BooleanField(default=True)
    available_from = models.DateTimeField(blank=True, null=True)
    available_until = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["category", "title"]

    def __str__(self):
        return self.title

    @property
    def question_count(self):
        return self.questions.count()

    @property
    def is_upcoming(self):
        return self.available_from is not None and timezone.now() < self.available_from

    @property
    def is_closed(self):
        return self.available_until is not None and timezone.now() > self.available_until

    @property
    def is_available_now(self):
        if not self.is_active:
            return False
        if self.is_upcoming:
            return False
        if self.is_closed:
            return False
        return True


class Question(models.Model):
    class QuestionType(models.TextChoices):
        MCQ = "MCQ", "MCQ"
        TEXT = "TEXT", "TEXT"
        CODE = "CODE", "CODE"

    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name="questions")
    question_text = models.TextField()
    question_type = models.CharField(max_length=10, choices=QuestionType.choices)
    marks = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return f"{self.exam.title} - Q{self.pk}"


class Option(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="options")
    option_text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.option_text


class StudentExam(models.Model):
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="student_exams"
    )
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name="student_exams")
    start_time = models.DateTimeField(default=timezone.now)
    end_time = models.DateTimeField()
    score = models.FloatField(default=0)
    submitted = models.BooleanField(default=False)
    warning_count = models.PositiveIntegerField(default=0)
    auto_submitted = models.BooleanField(default=False)

    class Meta:
        unique_together = ("student", "exam")
        ordering = ["-start_time"]

    def __str__(self):
        return f"{self.student} - {self.exam}"

    @property
    def is_time_up(self):
        return timezone.now() >= self.end_time


class StudentAnswer(models.Model):
    class ProgrammingLanguage(models.TextChoices):
        PYTHON = "python", "Python"
        C = "c", "C"
        JAVA = "java", "Java"

    student_exam = models.ForeignKey(
        StudentExam, on_delete=models.CASCADE, related_name="answers"
    )
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="student_answers")
    selected_option = models.ForeignKey(
        Option, on_delete=models.SET_NULL, blank=True, null=True, related_name="selected_answers"
    )
    text_answer = models.TextField(blank=True, null=True)
    code_answer = models.TextField(blank=True, null=True)
    programming_language = models.CharField(
        max_length=20, choices=ProgrammingLanguage.choices, blank=True, null=True
    )

    class Meta:
        unique_together = ("student_exam", "question")

    def __str__(self):
        return f"{self.student_exam} - {self.question_id}"


class Result(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="results")
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name="results")
    score = models.FloatField()
    passed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("student", "exam")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.student} - {self.exam} - {self.score}"
