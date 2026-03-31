from datetime import timedelta

import math
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Q
from django.http import Http404, HttpResponseBadRequest, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone

from courses.access import get_enrolled_course_ids, has_course_access

from .forms import ExamExcelUploadForm, ExamForm, QuestionForm, StudentAnswerForm
from .models import Exam, Option, Question, Result, StudentAnswer, StudentExam


PASS_PERCENTAGE = 40
MAX_TAB_WARNINGS = 3
REQUIRED_EXCEL_COLUMNS = ["exam", "question", "option1", "option2", "option3", "option4", "correct"]


def _exam_schedule_closed(exam):
    return exam.available_until is not None and timezone.now() > exam.available_until


def _exam_unavailable_response(exam):
    if not exam.is_active:
        return "This exam is currently inactive."
    if exam.is_upcoming:
        return f"This exam will start on {timezone.localtime(exam.available_from).strftime('%d %b %Y %I:%M %p')}."
    if exam.is_closed:
        return f"This exam closed on {timezone.localtime(exam.available_until).strftime('%d %b %Y %I:%M %p')}."
    return ""


def _ensure_exam_session(student_exam):
    if not has_course_access(student_exam.student, student_exam.exam.course):
        return redirect("exams:exam_list")
    if student_exam.submitted:
        return redirect(f"{reverse('exams:exam_result')}?exam={student_exam.exam_id}")
    if _exam_schedule_closed(student_exam.exam):
        _submit_exam(student_exam, auto_submitted=True)
        return redirect(f"{reverse('exams:exam_result')}?exam={student_exam.exam_id}")
    if student_exam.is_time_up:
        _submit_exam(student_exam, auto_submitted=True)
        return redirect(f"{reverse('exams:exam_result')}?exam={student_exam.exam_id}")
    return None


def _get_active_student_exam(request, student_exam_id=None):
    queryset = StudentExam.objects.select_related("exam", "exam__course", "student").filter(student=request.user)
    if student_exam_id is not None:
        student_exam = get_object_or_404(queryset, pk=student_exam_id)
    else:
        student_exam = queryset.order_by("-start_time").first()
        if student_exam is None:
            raise Http404("No exam session found.")
    redirect_response = _ensure_exam_session(student_exam)
    return student_exam, redirect_response


def _question_url(student_exam_id, current_index):
    return f"/exams/question/{student_exam_id}/?q={current_index}"


def _is_answered(answer):
    if answer.selected_option_id:
        return True
    if answer.text_answer and answer.text_answer.strip():
        return True
    if answer.code_answer and answer.code_answer.strip():
        return True
    return False


def _calculate_score(student_exam):
    total = 0
    answers = {
        answer.question_id: answer
        for answer in student_exam.answers.select_related("selected_option", "question")
    }
    for question in student_exam.exam.questions.prefetch_related("options"):
        answer = answers.get(question.id)
        if not answer:
            continue
        if question.question_type == Question.QuestionType.MCQ and answer.selected_option and answer.selected_option.is_correct:
            total += question.marks
        elif question.question_type in {Question.QuestionType.TEXT, Question.QuestionType.CODE}:
            if (answer.text_answer and answer.text_answer.strip()) or (answer.code_answer and answer.code_answer.strip()):
                total += question.marks
    return total


@transaction.atomic
def _submit_exam(student_exam, auto_submitted=False):
    if student_exam.submitted:
        result, _ = Result.objects.get_or_create(
            student=student_exam.student,
            exam=student_exam.exam,
            defaults={
                "score": student_exam.score,
                "passed": student_exam.score >= (student_exam.exam.total_marks * PASS_PERCENTAGE / 100),
            },
        )
        return result

    score = _calculate_score(student_exam)
    student_exam.score = score
    student_exam.submitted = True
    student_exam.auto_submitted = auto_submitted
    if timezone.now() > student_exam.end_time:
        student_exam.end_time = timezone.now()
    student_exam.save(update_fields=["score", "submitted", "auto_submitted", "end_time"])

    passed = score >= (student_exam.exam.total_marks * PASS_PERCENTAGE / 100)
    result, _ = Result.objects.update_or_create(
        student=student_exam.student,
        exam=student_exam.exam,
        defaults={"score": score, "passed": passed},
    )
    return result


@login_required
def exam_list(request):
    enrolled_course_ids = get_enrolled_course_ids(request.user)
    exams = Exam.objects.filter(is_active=True, course_id__in=enrolled_course_ids).prefetch_related("questions")
    attempts = {
        student_exam.exam_id: student_exam
        for student_exam in StudentExam.objects.filter(student=request.user).select_related("exam")
    }
    return render(request, "exams/exam_list.html", {"exams": exams, "attempts": attempts})


@login_required
def start_exam(request, id):
    exam = get_object_or_404(Exam.objects.select_related("course").prefetch_related("questions"), pk=id)
    if not has_course_access(request.user, exam.course):
        messages.error(request, "You are not enrolled in this course")
        return redirect("exams:exam_list")
    student_exam = StudentExam.objects.filter(student=request.user, exam=exam).first()

    unavailable_message = _exam_unavailable_response(exam)
    if unavailable_message:
        messages.warning(request, unavailable_message)
        return redirect("exams:exam_list")

    if request.method == "GET":
        if student_exam and student_exam.submitted:
            messages.info(request, "You have already attempted this exam.")
            return redirect(f"{reverse('exams:exam_result')}?exam={exam.id}")
        return render(
            request,
            "exams/exam_start.html",
            {"exam": exam, "student_exam": student_exam, "max_warnings": MAX_TAB_WARNINGS},
        )

    if student_exam and student_exam.submitted:
        messages.info(request, "You have already attempted this exam.")
        return redirect(f"{reverse('exams:exam_result')}?exam={exam.id}")

    if student_exam is None:
        end_time = timezone.now() + timedelta(minutes=exam.duration)
        if exam.available_until and exam.available_until < end_time:
            end_time = exam.available_until
        student_exam = StudentExam.objects.create(
            student=request.user,
            exam=exam,
            start_time=timezone.now(),
            end_time=end_time,
        )

    return redirect("exams:exam_question", id=student_exam.id)


@login_required
def exam_question(request, id):
    student_exam, redirect_response = _get_active_student_exam(request, id)
    if redirect_response:
        return redirect_response

    questions = list(student_exam.exam.questions.prefetch_related("options"))
    if not questions:
        messages.warning(request, "This exam has no questions yet.")
        return redirect("exams:exam_list")

    try:
        current_index = max(int(request.GET.get("q", 1) or 1), 1)
    except ValueError:
        current_index = 1
    if current_index > len(questions):
        current_index = len(questions)
    question = questions[current_index - 1]

    answer, _ = StudentAnswer.objects.get_or_create(student_exam=student_exam, question=question)
    form = StudentAnswerForm(instance=answer, question=question)

    if request.method == "POST":
        form = StudentAnswerForm(request.POST, instance=answer, question=question)
        if form.is_valid():
            saved_answer = form.save(commit=False)
            saved_answer.student_exam = student_exam
            saved_answer.question = question
            if question.question_type != Question.QuestionType.MCQ:
                saved_answer.selected_option = None
            if question.question_type != Question.QuestionType.TEXT:
                saved_answer.text_answer = ""
            if question.question_type != Question.QuestionType.CODE:
                saved_answer.code_answer = ""
                saved_answer.programming_language = ""
            saved_answer.save()

            if "submit_exam" in request.POST:
                _submit_exam(student_exam)
                messages.success(request, "Exam submitted successfully.")
                return redirect(f"{reverse('exams:exam_result')}?exam={student_exam.exam_id}")

            if "next_question" in request.POST and current_index < len(questions):
                return redirect(_question_url(student_exam.id, current_index + 1))
            if "previous_question" in request.POST and current_index > 1:
                return redirect(_question_url(student_exam.id, current_index - 1))
            messages.success(request, "Answer saved.")
            return redirect(_question_url(student_exam.id, current_index))

    answered_question_ids = {
        answer.question_id for answer in student_exam.answers.all() if _is_answered(answer)
    }
    remaining_seconds = max(int((student_exam.end_time - timezone.now()).total_seconds()), 0)
    return render(
        request,
        "exams/exam_question.html",
        {
            "student_exam": student_exam,
            "question": question,
            "form": form,
            "questions": questions,
            "current_index": current_index,
            "total_questions": len(questions),
            "answered_question_ids": answered_question_ids,
            "remaining_seconds": remaining_seconds,
            "max_warnings": MAX_TAB_WARNINGS,
        },
    )


@login_required
def autosave_answer(request, id):
    if request.method != "POST":
        return HttpResponseBadRequest("Invalid request method.")

    student_exam, redirect_response = _get_active_student_exam(request, id)
    if redirect_response:
        return JsonResponse({"redirect_url": redirect_response.url}, status=409)

    question_id = request.POST.get("question_id")
    question = get_object_or_404(Question, pk=question_id, exam=student_exam.exam)
    answer, _ = StudentAnswer.objects.get_or_create(student_exam=student_exam, question=question)

    if question.question_type == Question.QuestionType.MCQ:
        option_id = request.POST.get("selected_option")
        answer.selected_option = Option.objects.filter(pk=option_id, question=question).first() if option_id else None
        answer.text_answer = ""
        answer.code_answer = ""
        answer.programming_language = ""
    elif question.question_type == Question.QuestionType.TEXT:
        answer.text_answer = request.POST.get("text_answer", "")
        answer.selected_option = None
        answer.code_answer = ""
        answer.programming_language = ""
    else:
        answer.code_answer = request.POST.get("code_answer", "")
        answer.programming_language = request.POST.get("programming_language", "")
        answer.selected_option = None
        answer.text_answer = ""
    answer.save()
    return JsonResponse({"status": "saved"})


@login_required
def record_warning(request, id):
    if request.method != "POST":
        return HttpResponseBadRequest("Invalid request method.")

    student_exam, redirect_response = _get_active_student_exam(request, id)
    if redirect_response:
        return JsonResponse({"redirect_url": redirect_response.url}, status=409)

    student_exam.warning_count += 1
    student_exam.save(update_fields=["warning_count"])

    if student_exam.warning_count >= MAX_TAB_WARNINGS:
        _submit_exam(student_exam, auto_submitted=True)
        return JsonResponse(
            {
                "status": "submitted",
                "message": "Exam auto-submitted because tab switching limit was exceeded.",
                "redirect_url": f"{reverse('exams:exam_result')}?exam={student_exam.exam_id}",
            }
        )

    remaining = MAX_TAB_WARNINGS - student_exam.warning_count
    return JsonResponse(
        {
            "status": "warning",
            "message": f"Tab switching detected. {remaining} warning(s) remaining before auto submission.",
            "warning_count": student_exam.warning_count,
        }
    )


@login_required
def submit_exam(request):
    if request.method != "POST":
        return redirect("exams:exam_list")

    student_exam_id = request.POST.get("student_exam_id")
    student_exam, redirect_response = _get_active_student_exam(request, student_exam_id)
    if redirect_response:
        return redirect_response

    _submit_exam(student_exam, auto_submitted=student_exam.is_time_up)
    messages.success(request, "Exam submitted successfully.")
    return redirect(f"{reverse('exams:exam_result')}?exam={student_exam.exam_id}")


@login_required
def exam_result(request):
    exam_id = request.GET.get("exam")
    results = Result.objects.select_related("exam").filter(student=request.user)
    if exam_id:
        results = results.filter(exam_id=exam_id)
    result = results.order_by("-created_at").first()
    if result is None:
        messages.info(request, "No exam result found yet.")
        return redirect("exams:exam_list")
    return render(request, "exams/exam_result.html", {"result": result})


@login_required
def exam_history(request):
    results = Result.objects.filter(student=request.user).select_related("exam")
    return render(request, "exams/exam_history.html", {"results": results})


@staff_member_required
def admin_exam_create(request):
    form = ExamForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Exam created successfully.")
        return redirect("exams:admin_exam_create")
    exams = Exam.objects.all()
    return render(request, "exams/admin_exam_form.html", {"form": form, "exams": exams})


@staff_member_required
def admin_question_create(request):
    form = QuestionForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Question created successfully. Add options from Django admin for MCQs.")
        return redirect("exams:admin_question_create")
    questions = Question.objects.select_related("exam")
    return render(request, "exams/admin_question_form.html", {"form": form, "questions": questions})


def _normalize_cell(value):
    if value is None:
        return ""
    if isinstance(value, float) and math.isnan(value):
        return ""
    return str(value).strip()


@staff_member_required
@transaction.atomic
def upload_exam_excel(request):
    initial = {}
    if request.method == "GET" and request.GET.get("exam"):
        initial["exam"] = request.GET.get("exam")
    form = ExamExcelUploadForm(request.POST or None, request.FILES or None, initial=initial)

    if request.method == "POST" and form.is_valid():
        try:
            import pandas as pd
        except ImportError:
            messages.error(request, "Excel import requires pandas and openpyxl. Please install them first.")
            return redirect("exams:upload_exam_excel")

        exam = form.cleaned_data["exam"]
        excel_file = form.cleaned_data["file"]

        try:
            dataframe = pd.read_excel(excel_file)
        except Exception:
            messages.error(request, "Unable to read the Excel file. Please upload a valid .xlsx or .xls file.")
            return redirect("exams:upload_exam_excel")

        normalized_columns = [str(column).strip().lower() for column in dataframe.columns]
        dataframe.columns = normalized_columns
        missing_columns = [column for column in REQUIRED_EXCEL_COLUMNS if column not in normalized_columns]
        if missing_columns:
            messages.error(request, f"Missing required columns: {', '.join(missing_columns)}")
            return redirect("exams:upload_exam_excel")

        imported_count = 0
        errors = []

        for index, row in dataframe.iterrows():
            row_number = index + 2
            question_text = _normalize_cell(row.get("question"))
            options = [_normalize_cell(row.get(f"option{position}")) for position in range(1, 5)]
            correct_option_text = _normalize_cell(row.get("correct"))

            if not question_text:
                errors.append(f"Row {row_number}: question is required.")
                continue

            if any(not option_text for option_text in options):
                errors.append(f"Row {row_number}: all four option columns are required.")
                continue

            matching_correct_option = next(
                (option_text for option_text in options if option_text.casefold() == correct_option_text.casefold()),
                None,
            )
            if not matching_correct_option:
                errors.append(f"Row {row_number}: correct answer must exactly match one of the option texts.")
                continue

            question = Question.objects.create(
                exam=exam,
                question_text=question_text,
                question_type=Question.QuestionType.MCQ,
                marks=1,
            )
            Option.objects.bulk_create(
                [
                    Option(
                        question=question,
                        option_text=option_text,
                        is_correct=option_text.casefold() == matching_correct_option.casefold(),
                    )
                    for option_text in options
                ]
            )
            imported_count += 1

        exam.total_marks = sum(exam.questions.values_list("marks", flat=True))
        exam.save(update_fields=["total_marks"])

        if imported_count:
            messages.success(request, f"Imported {imported_count} questions successfully.")
        if errors:
            messages.warning(request, "Some rows were skipped: " + " ".join(errors[:5]))
            if len(errors) > 5:
                messages.warning(request, f"{len(errors) - 5} more row error(s) were skipped.")
        if not imported_count and not errors:
            messages.info(request, "No questions were imported.")
        return redirect("exams:upload_exam_excel")

    return render(request, "exams/upload_excel.html", {"form": form})
