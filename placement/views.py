from urllib.parse import urlparse

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .models import Job, JobApplication, MockInterview


def placement_summary(user):
    if user is None or not getattr(user, "is_authenticated", False):
        return {
            "latest_jobs": Job.objects.filter(is_active=True)[:3],
            "my_job_applications": JobApplication.objects.none(),
            "upcoming_mock_interview": None,
        }

    today = timezone.localdate()
    my_job_applications = JobApplication.objects.filter(user=user).select_related("job")
    upcoming_mock_interview = (
        MockInterview.objects.filter(user=user, status=MockInterview.Status.SCHEDULED, date__gte=today)
        .order_by("date", "time")
        .first()
    )
    return {
        "latest_jobs": Job.objects.filter(is_active=True)[:3],
        "my_job_applications": my_job_applications[:5],
        "upcoming_mock_interview": upcoming_mock_interview,
    }


def job_list(request):
    jobs = Job.objects.filter(is_active=True).order_by("-created_at")
    query = request.GET.get("q", "").strip()
    location = request.GET.get("location", "").strip()
    company = request.GET.get("company", "").strip()

    if query:
        jobs = jobs.filter(title__icontains=query)
    if location:
        jobs = jobs.filter(location__icontains=location)
    if company:
        jobs = jobs.filter(company__icontains=company)

    applied_job_ids = set()
    if request.user.is_authenticated:
        applied_job_ids = set(JobApplication.objects.filter(user=request.user).values_list("job_id", flat=True))
    context = {
        "jobs": jobs,
        "applied_job_ids": applied_job_ids,
        "query": query,
        "location": location,
        "company": company,
    }
    return render(request, "placement/job_list.html", context)


def job_detail(request, job_id):
    job = get_object_or_404(Job, pk=job_id, is_active=True)
    application = None
    if request.user.is_authenticated:
        application = JobApplication.objects.filter(user=request.user, job=job).first()
    return render(request, "placement/job_detail.html", {"job": job, "application": application})


@login_required
def apply_job(request, job_id):
    job = get_object_or_404(Job, pk=job_id, is_active=True)
    if request.method != "POST":
        return redirect("placement:job_detail", job_id=job.id)

    existing_application = JobApplication.objects.filter(user=request.user, job=job).first()
    resume = request.FILES.get("resume")
    if existing_application:
        messages.info(request, "You have already applied for this job.")
        return redirect("placement:job_detail", job_id=job.id)

    if resume is None:
        messages.error(request, "Please upload your resume before applying.")
        return redirect("placement:job_detail", job_id=job.id)

    JobApplication.objects.create(
        user=request.user,
        job=job,
        resume=resume,
        status=JobApplication.Status.APPLIED,
    )
    messages.success(request, "Job application submitted successfully.")
    if job.apply_link:
        parsed_link = urlparse(job.apply_link)
        if parsed_link.scheme and parsed_link.netloc:
            return redirect(job.apply_link)
    return redirect("placement:job_detail", job_id=job.id)


@login_required
def mock_interview_list(request):
    interviews = MockInterview.objects.filter(user=request.user).order_by("date", "time")
    return render(request, "placement/mock_interview_list.html", {"interviews": interviews})
