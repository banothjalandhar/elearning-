import json
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from django.core.management.base import BaseCommand

from placement.models import Job


class Command(BaseCommand):
    help = "Fetch remote jobs from the Remotive API and save them to the Job model."

    def handle(self, *args, **options):
        request = Request(
            "https://remotive.com/api/remote-jobs",
            headers={"User-Agent": "CodeWithJalandhar/1.0"},
        )
        try:
            with urlopen(request, timeout=30) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except (HTTPError, URLError, TimeoutError) as exc:
            self.stderr.write(self.style.ERROR(f"Unable to fetch jobs: {exc}"))
            return

        jobs = payload.get("jobs", [])
        created_count = 0
        updated_count = 0

        for item in jobs:
            title = (item.get("title") or "").strip()
            company = (item.get("company_name") or "").strip()
            apply_link = (item.get("url") or "").strip()
            if not title or not company:
                continue

            job, created = Job.objects.update_or_create(
                title=title,
                company=company,
                apply_link=apply_link,
                defaults={
                    "location": (item.get("candidate_required_location") or "Remote").strip(),
                    "description": item.get("description") or "",
                    "skills": ", ".join(item.get("tags") or []),
                    "is_active": True,
                },
            )
            if created:
                created_count += 1
            else:
                updated_count += 1

        self.stdout.write(
            self.style.SUCCESS(f"Job sync complete. Created: {created_count}, Updated: {updated_count}")
        )

