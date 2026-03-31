import json
import logging
from decimal import Decimal, InvalidOperation
from urllib import error, request

from django.conf import settings

from courses.models import Course, upcomingcourse
from exams.models import Exam


FREE_AI_PROVIDERS = {"ollama", "openrouter", "huggingface"}
logger = logging.getLogger(__name__)


def _format_price(price):
    if isinstance(price, Decimal):
        value = price
    else:
        try:
            value = Decimal(str(price))
        except (InvalidOperation, TypeError):
            return str(price)
    return f"Rs. {value.quantize(Decimal('0.01'))}"


def build_context():
    active_courses = list(Course.objects.order_by("title")[:10])
    upcoming_courses = list(upcomingcourse.objects.filter(is_active=True).order_by("start_date")[:5])
    active_exams = list(Exam.objects.filter(is_active=True).order_by("category", "title")[:10])

    course_lines = [
        f"- {course.title}: fee {_format_price(course.price)}"
        for course in active_courses
    ] or ["- Course details will be updated soon."]

    upcoming_lines = [
        f"- {course.title}: starts {course.start_date.strftime('%d %b %Y %I:%M %p')}, fee {_format_price(course.price)}"
        for course in upcoming_courses
    ] or ["- No upcoming batches are listed right now."]

    exam_lines = [
        f"- {exam.title}: {exam.get_category_display()}, duration {exam.duration} minutes, total marks {exam.total_marks}"
        for exam in active_exams
    ] or ["- No active exams are listed right now."]

    return {
        "contact_email": settings.CHATBOT_CONTACT_EMAIL,
        "contact_phone": settings.CHATBOT_CONTACT_PHONE,
        "courses": course_lines,
        "upcoming_batches": upcoming_lines,
        "placement_info": [
            "- Placement support includes mock interviews, coding practice, aptitude practice, and communication rounds."
        ],
        "exam_info": exam_lines,
    }


def _rule_based_reply(message, context):
    message_lower = message.lower()

    if any(keyword in message_lower for keyword in ["course", "python", "django", "java", "react", "devops"]):
        return "Here are the current course details:\n" + "\n".join(context["courses"])
    if any(keyword in message_lower for keyword in ["fee", "fees", "price", "cost"]):
        return "Current fee information:\n" + "\n".join(context["courses"])
    if any(keyword in message_lower for keyword in ["batch", "timing", "schedule", "time"]):
        return "Upcoming batch timings:\n" + "\n".join(context["upcoming_batches"])
    if any(keyword in message_lower for keyword in ["placement", "job", "interview"]):
        return "Placement support details:\n" + "\n".join(context["placement_info"])
    if any(keyword in message_lower for keyword in ["exam", "test", "assessment"]):
        return "Exam information:\n" + "\n".join(context["exam_info"])
    if any(keyword in message_lower for keyword in ["contact", "phone", "email", "whatsapp", "call"]):
        return (
            "You can contact CodeWithJalandhar at "
            f"{context['contact_email']} or {context['contact_phone']}."
        )

    return (
        "I can help with course info, fees, batch timings, placement support, exam info, and contact details. "
        "Please ask one of those."
    )


def _chat_prompt(message, context):
    return (
        "You are the CodeWithJalandhar assistant for an e-learning website. "
        "Answer briefly, accurately, and only using the provided institute context. "
        "If a detail is missing, say it is not currently listed and share contact info.\n\n"
        f"Contact email: {context['contact_email']}\n"
        f"Contact phone: {context['contact_phone']}\n"
        "Courses:\n"
        + "\n".join(context["courses"])
        + "\nUpcoming batches:\n"
        + "\n".join(context["upcoming_batches"])
        + "\nPlacement support:\n"
        + "\n".join(context["placement_info"])
        + "\nExams:\n"
        + "\n".join(context["exam_info"])
        + f"\n\nUser question: {message}"
    )


def _post_json(url, payload, headers=None):
    req = request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json", **(headers or {})},
        method="POST",
    )
    with request.urlopen(req, timeout=20) as response:
        return json.loads(response.read().decode("utf-8"))


def _call_ollama(message, context):
    data = _post_json(
        f"{settings.OLLAMA_BASE_URL.rstrip('/')}/api/generate",
        {"model": settings.OLLAMA_MODEL, "prompt": _chat_prompt(message, context), "stream": False},
    )
    return data.get("response", "").strip()


def _call_openrouter(message, context):
    if not settings.OPENROUTER_API_KEY:
        return ""
    data = _post_json(
        "https://openrouter.ai/api/v1/chat/completions",
        {
            "model": settings.OPENROUTER_MODEL,
            "messages": [{"role": "user", "content": _chat_prompt(message, context)}],
        },
        headers={"Authorization": f"Bearer {settings.OPENROUTER_API_KEY}"},
    )
    choices = data.get("choices") or []
    if not choices:
        return ""
    return choices[0].get("message", {}).get("content", "").strip()


def _call_huggingface(message, context):
    if not settings.HUGGINGFACE_API_KEY:
        return ""
    data = _post_json(
        f"https://api-inference.huggingface.co/models/{settings.HUGGINGFACE_MODEL}",
        {"inputs": _chat_prompt(message, context)},
        headers={"Authorization": f"Bearer {settings.HUGGINGFACE_API_KEY}"},
    )
    if isinstance(data, list) and data:
        return data[0].get("generated_text", "").strip()
    if isinstance(data, dict):
        return data.get("generated_text", "").strip()
    return ""


def generate_chatbot_reply(message):
    context = build_context()
    provider = settings.AI_PROVIDER.lower().strip()

    if provider not in FREE_AI_PROVIDERS:
        return _rule_based_reply(message, context)

    try:
        if provider == "ollama":
            reply = _call_ollama(message, context)
        elif provider == "openrouter":
            reply = _call_openrouter(message, context)
        else:
            reply = _call_huggingface(message, context)
    except (error.URLError, TimeoutError, ValueError, KeyError, json.JSONDecodeError):
        logger.exception("Chatbot provider call failed for provider '%s'.", provider)
        reply = ""

    return reply or _rule_based_reply(message, context)
