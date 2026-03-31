from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from courses.access import get_active_enrollments

from .models import (
    CodeSubmission,
    ScheduledExam,
    Subject,
    SubTopic,
    TestResult,
    Topic,
    TopicTest,
    UserAnswer,
    UserProgress,
)


def _topic_completion_percentage(user):
    total_topics = Topic.objects.count()
    if not getattr(user, "is_authenticated", False) or total_topics == 0:
        return 0
    completed_topics = UserProgress.objects.filter(user=user, completed=True).count()
    return round((completed_topics / total_topics) * 100)


def _next_subtopic(current_subtopic):
    ordered_subtopics = list(
        SubTopic.objects.filter(topic__subject=current_subtopic.topic.subject)
        .select_related("topic", "topic__subject")
        .order_by("topic__order", "order", "id")
    )
    for index, subtopic in enumerate(ordered_subtopics):
        if subtopic.id == current_subtopic.id and index + 1 < len(ordered_subtopics):
            return ordered_subtopics[index + 1]
    return None


def _mock_run_code(language, code):
    code = (code or "").strip()
    if not code:
        return "Write some code and click Run to preview a safe mock execution."

    previews = {
        "python": "Mock Python runner: syntax captured successfully.",
        "java": "Mock Java runner: class structure queued for compilation preview.",
        "javascript": "Mock JavaScript runner: script parsed and simulated.",
    }
    first_line = code.splitlines()[0][:120]
    return f"{previews.get(language, 'Mock runner complete.')}\nPreview: {first_line}"


def dashboard_context(user):
    total_topics = Topic.objects.count()
    completed_topics = 0
    recent_tests = TestResult.objects.none()
    batch = None
    if getattr(user, "is_authenticated", False):
        completed_topics = UserProgress.objects.filter(user=user, completed=True).count()
        recent_tests = TestResult.objects.filter(user=user).select_related("test", "test__topic")[:5]
        batch = getattr(user, "batch", None)
    return {
        "lms_subject_count": Subject.objects.count(),
        "lms_topic_count": total_topics,
        "lms_completed_topics": completed_topics,
        "lms_progress_percentage": _topic_completion_percentage(user),
        "lms_recent_tests": recent_tests,
        "lms_batch": batch,
    }


def subject_list(request):
    subjects = Subject.objects.annotate(
        topic_count=Count("topics", distinct=True),
        subtopic_count=Count("topics__subtopics", distinct=True),
    )
    return render(request, "lms/subject_list.html", {"subjects": subjects})


def subject_detail(request, subject_slug):
    subject = get_object_or_404(
        Subject.objects.prefetch_related("topics__subtopics", "scheduled_exams").annotate(topic_total=Count("topics")),
        slug=subject_slug,
    )
    return render(request, "lms/topic_list.html", {"subject": subject, "topics": subject.topics.all()})


def topic_detail(request, topic_id):
    topic = get_object_or_404(Topic.objects.select_related("subject").prefetch_related("subtopics__contents", "tests"), pk=topic_id)
    progress = None
    if request.user.is_authenticated:
        progress = UserProgress.objects.filter(user=request.user, topic=topic).first()
    return render(
        request,
        "lms/topic_detail.html",
        {
            "topic": topic,
            "subtopics": topic.subtopics.all(),
            "tests": topic.tests.all(),
            "progress": progress,
        },
    )


def content_detail(request, subtopic_id):
    subtopic = get_object_or_404(
        SubTopic.objects.select_related("topic", "topic__subject").prefetch_related("contents"),
        pk=subtopic_id,
    )
    content = subtopic.contents.order_by("-updated_at").first()
    next_subtopic = _next_subtopic(subtopic)
    return render(
        request,
        "lms/content_detail.html",
        {
            "subtopic": subtopic,
            "content": content,
            "next_subtopic": next_subtopic,
        },
    )


@login_required
def code_editor(request, subtopic_id):
    subtopic = get_object_or_404(SubTopic.objects.select_related("topic", "topic__subject"), pk=subtopic_id)
    submission, _ = CodeSubmission.objects.get_or_create(user=request.user, subtopic=subtopic)

    if request.method == "POST":
        language = request.POST.get("language", submission.language)
        code = request.POST.get("code", "")
        action = request.POST.get("action", "save")
        submission.language = language
        submission.code = code
        if action == "run":
            submission.output = _mock_run_code(language, code)
            messages.success(request, "Code executed using the safe preview runner.")
        else:
            messages.success(request, "Code saved successfully.")
        submission.save()
        return redirect("lms:code_editor", subtopic_id=subtopic.id)

    return render(
        request,
        "lms/code_editor.html",
        {
            "subtopic": subtopic,
            "submission": submission,
            "languages": CodeSubmission.Language.choices,
        },
    )


@login_required
def topic_test_view(request, test_id):
    test = get_object_or_404(TopicTest.objects.select_related("topic", "topic__subject").prefetch_related("questions"), pk=test_id)
    questions = list(test.questions.all())
    if not questions:
        messages.warning(request, "This test has no questions yet.")
        return redirect("lms:topic_detail", topic_id=test.topic_id)

    if request.method == "POST":
        UserAnswer.objects.filter(user=request.user, question__test=test).delete()
        score = 0
        total = len(questions)
        for question in questions:
            try:
                selected_option = int(request.POST.get(f"question_{question.id}", 0) or 0)
            except (TypeError, ValueError):
                selected_option = 0
            if selected_option:
                UserAnswer.objects.create(user=request.user, question=question, selected_option=selected_option)
                if selected_option == question.correct_option:
                    score += 1

        result = TestResult.objects.create(user=request.user, test=test, score=score, total=total)
        UserProgress.objects.update_or_create(
            user=request.user,
            topic=test.topic,
            defaults={"completed": True, "score": round((score / total) * 100) if total else 0},
        )
        messages.success(request, "Test submitted successfully.")
        return redirect("lms:result_view", result_id=result.id)

    return render(request, "lms/test_page.html", {"test": test, "questions": questions})


@login_required
def result_view(request, result_id):
    result = get_object_or_404(TestResult.objects.select_related("test", "test__topic", "test__topic__subject"), pk=result_id, user=request.user)
    return render(request, "lms/result_page.html", {"result": result})


@login_required
def progress_dashboard(request):
    user = request.user
    active_enrollments = get_active_enrollments(user).select_related("course").order_by("course__title")
    recent_tests = TestResult.objects.filter(user=user).select_related("test", "test__topic")[:5]
    progress_records = UserProgress.objects.filter(user=user).select_related("topic", "topic__subject").order_by("topic__subject__name", "topic__order")
    completed_topics = progress_records.filter(completed=True).count()
    total_topics = Topic.objects.count()
    progress_percentage = round((completed_topics / total_topics) * 100) if total_topics else 0
    scheduled_exams = ScheduledExam.objects.select_related("subject", "batch", "topic_test").filter(batch=user.batch) if user.batch_id else ScheduledExam.objects.none()

    return render(
        request,
        "lms/progress_dashboard.html",
        {
            "enrollments": active_enrollments,
            "progress_records": progress_records,
            "completed_topics": completed_topics,
            "progress_percentage": progress_percentage,
            "recent_tests": recent_tests,
            "scheduled_exams": scheduled_exams[:5],
        },
    )


@login_required
def scheduled_exam_list(request):
    if not request.user.batch_id:
        messages.info(request, "You are not assigned to a batch yet.")
        return render(request, "lms/scheduled_exam_list.html", {"scheduled_exams": [], "user_batch": None})

    exams = ScheduledExam.objects.select_related("subject", "batch", "topic_test").filter(batch=request.user.batch)
    return render(request, "lms/scheduled_exam_list.html", {"scheduled_exams": exams, "user_batch": request.user.batch})


@login_required
def scheduled_exam_detail(request, exam_id):
    scheduled_exam = get_object_or_404(ScheduledExam.objects.select_related("subject", "batch", "topic_test"), pk=exam_id)
    if request.user.batch_id != scheduled_exam.batch_id:
        messages.error(request, "This exam is restricted to another batch.")
        return redirect("lms:scheduled_exam_list")

    now = timezone.now()
    can_start = scheduled_exam.start_time <= now <= scheduled_exam.end_time
    return render(
        request,
        "lms/scheduled_exam_detail.html",
        {
            "scheduled_exam": scheduled_exam,
            "can_start": can_start,
            "starts_later": scheduled_exam.start_time > now,
        },
    )
