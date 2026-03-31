import logging
import time
from decimal import Decimal, InvalidOperation

import requests
from django.conf import settings

from courses.models import Course, Enrollment, upcomingcourse
from exams.models import Exam


logger = logging.getLogger(__name__)
SUPPORTED_PROVIDERS = {"rule_based", "openrouter", "ollama", "huggingface"}
OPENROUTER_DEFAULT_MODEL = "deepseek/deepseek-chat:free"
OPENROUTER_FALLBACK_MODEL = "google/gemma-7b-it:free"


def _format_price(price):
    if isinstance(price, Decimal):
        value = price
    else:
        try:
            value = Decimal(str(price))
        except (InvalidOperation, TypeError):
            return str(price)
    return f"Rs. {value.quantize(Decimal('0.01'))}"


def _build_learning_context(user):
    courses = list(Course.objects.order_by("title")[:12])
    upcoming_batches = list(upcomingcourse.objects.filter(is_active=True).order_by("start_date")[:6])
    exams = list(Exam.objects.filter(is_active=True).order_by("category", "title")[:10])

    enrolled_course_names = []
    if getattr(user, "is_authenticated", False):
        enrolled_course_names = list(
            Enrollment.objects.filter(user=user, payment_done=True, is_active=True)
            .select_related("course")
            .values_list("course__title", flat=True)
        )

    return {
        "contact_email": settings.CHATBOT_CONTACT_EMAIL,
        "contact_phone": settings.CHATBOT_CONTACT_PHONE,
        "courses": [f"- {course.title}: fee {_format_price(course.price)}" for course in courses]
        or ["- Course details will be updated soon."],
        "upcoming_batches": [
            f"- {course.title}: starts {course.start_date.strftime('%d %b %Y %I:%M %p')}, fee {_format_price(course.price)}"
            for course in upcoming_batches
        ]
        or ["- No upcoming batches are listed right now."],
        "exams": [
            f"- {exam.title}: {exam.get_category_display()}, duration {exam.duration} minutes, total marks {exam.total_marks}"
            for exam in exams
        ]
        or ["- No active exams are listed right now."],
        "placement": [
            "- Placement support includes mock interviews, coding tests, aptitude tests, and interview preparation."
        ],
        "enrolled_courses": enrolled_course_names,
    }


def _get_memory(user):
    history = getattr(user, "_chatbot_history", []) or []
    return history[-5:]


def _build_system_prompt(context):
    enrolled_text = (
        ", ".join(context["enrolled_courses"]) if context["enrolled_courses"] else "No enrolled course context available"
    )
    return (
        "You are an expert coding tutor, placement trainer, and friendly teacher for CodeWithJalandhar. "
        "Explain concepts step by step in simple student-friendly language. "
        "Use practical examples and keep answers clear and helpful. "
        f"Enrolled course context: {enrolled_text}. "
        f"Contact email: {context['contact_email']}. Contact phone: {context['contact_phone']}."
    )


def _rule_based_response(message, context):
    message_lower = message.lower()
    if any(keyword in message_lower for keyword in ["course", "python", "java", "django", "react", "skill"]):
        return "Here are the current course details:\n" + "\n".join(context["courses"])
    if any(keyword in message_lower for keyword in ["fee", "fees", "price", "cost"]):
        return "Current fee information:\n" + "\n".join(context["courses"])
    if any(keyword in message_lower for keyword in ["batch", "timing", "schedule", "time"]):
        return "Upcoming batch timings:\n" + "\n".join(context["upcoming_batches"])
    if any(keyword in message_lower for keyword in ["placement", "job", "interview"]):
        return "Placement support details:\n" + "\n".join(context["placement"])
    if any(keyword in message_lower for keyword in ["exam", "test", "assessment"]):
        return "Exam information:\n" + "\n".join(context["exams"])
    if any(keyword in message_lower for keyword in ["contact", "phone", "email", "call", "whatsapp"]):
        return f"You can contact CodeWithJalandhar at {context['contact_email']} or {context['contact_phone']}."
    return "Ask me about coding, courses, fees, batch timings, placement prep, exams, or contact support."


def _build_messages(message, user, context):
    messages = [{"role": "system", "content": _build_system_prompt(context)}]
    for item in _get_memory(user):
        role = item.get("role")
        content = item.get("content")
        if role in {"user", "assistant"} and content:
            messages.append({"role": role, "content": str(content)})
    messages.append({"role": "user", "content": message})
    return messages


def _extract_openrouter_content(data):
    choices = data.get("choices") or []
    if not choices:
        logger.warning("OpenRouter response missing choices: %s", data)
        return ""
    return ((choices[0].get("message") or {}).get("content") or "").strip()


def _call_openrouter(message, user, context):
    api_key = (settings.OPENROUTER_API_KEY or "").strip()
    timeout = int(getattr(settings, "OPENROUTER_TIMEOUT", 30) or 30)
    env_model = (settings.OPENROUTER_MODEL or "").strip()

    if not api_key:
        logger.error("OpenRouter API key is missing.")
        return ""

    models_to_try = []
    if env_model:
        models_to_try.append(env_model)
    if OPENROUTER_DEFAULT_MODEL not in models_to_try:
        models_to_try.append(OPENROUTER_DEFAULT_MODEL)
    if OPENROUTER_FALLBACK_MODEL not in models_to_try:
        models_to_try.append(OPENROUTER_FALLBACK_MODEL)

    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": getattr(settings, "OPENROUTER_SITE_URL", "http://127.0.0.1:8000"),
        "X-Title": getattr(settings, "OPENROUTER_APP_NAME", "CodeWithJalandhar"),
    }

    for model in models_to_try:
        payload = {
            "model": model,
            "messages": _build_messages(message, user, context),
            "max_tokens": 280,
            "temperature": 0.7,
        }

        try:
            started_at = time.perf_counter()
            response = requests.post(url, json=payload, headers=headers, timeout=timeout)
            elapsed_ms = round((time.perf_counter() - started_at) * 1000, 2)

            logger.info(
                "OpenRouter request completed. model=%s status=%s time_ms=%s",
                model,
                response.status_code,
                elapsed_ms,
            )

            if response.status_code == 404:
                logger.warning("OpenRouter returned 404 for model=%s body=%s", model, response.text)
                continue

            if response.status_code >= 400:
                logger.error("OpenRouter error. model=%s status=%s body=%s", model, response.status_code, response.text)
                continue

            data = response.json()
            content = _extract_openrouter_content(data)
            if content:
                print(f"Working model: {model}")
                return content
        except requests.Timeout:
            logger.exception("OpenRouter request timed out. model=%s", model)
        except requests.RequestException as exc:
            error_body = ""
            if getattr(exc, "response", None) is not None:
                error_body = exc.response.text
            logger.exception("OpenRouter request failed. model=%s body=%s", model, error_body)
        except ValueError:
            logger.exception("OpenRouter returned invalid JSON. model=%s", model)

    return ""


def _call_ollama(message, user, context):
    timeout = int(getattr(settings, "OLLAMA_TIMEOUT", 30) or 30)
    url = f"{settings.OLLAMA_BASE_URL.rstrip('/')}/api/chat"
    payload = {
        "model": settings.OLLAMA_MODEL,
        "messages": [
            {
                "role": "user",
                "content": message,
            }
        ],
        "stream": False,
    }

    print("Ollama URL:", settings.OLLAMA_BASE_URL)
    print("Model:", settings.OLLAMA_MODEL)

    response = requests.post(
        url,
        json=payload,
        timeout=timeout,
    )
    print("Status code:", response.status_code)

    if response.status_code >= 400:
        logger.error("Ollama error. status=%s body=%s", response.status_code, response.text)
        return "Ollama error: check model or request format"

    response.raise_for_status()
    data = response.json()
    return (data["message"]["content"] or "").strip()


def _call_huggingface(message, user, context):
    api_key = (settings.HUGGINGFACE_API_KEY or "").strip()
    if not api_key:
        return ""

    timeout = int(getattr(settings, "HUGGINGFACE_TIMEOUT", 30) or 30)
    response = requests.post(
        f"https://api-inference.huggingface.co/models/{settings.HUGGINGFACE_MODEL}",
        json={
            "inputs": message,
            "parameters": {"max_new_tokens": 220, "return_full_text": False},
        },
        headers={"Authorization": f"Bearer {api_key}"},
        timeout=timeout,
    )
    response.raise_for_status()
    data = response.json()
    if isinstance(data, list) and data:
        return (data[0].get("generated_text") or "").strip()
    if isinstance(data, dict):
        return (data.get("generated_text") or "").strip()
    return ""


def generate_ai_response(message, user):
    context = _build_learning_context(user)
    provider = (settings.AI_PROVIDER or "rule_based").strip().lower()
    if provider not in SUPPORTED_PROVIDERS:
        provider = "rule_based"

    if provider == "rule_based":
        return _rule_based_response(message, context)

    try:
        if provider == "openrouter":
            reply = _call_openrouter(message, user, context)
        elif provider == "ollama":
            reply = _call_ollama(message, user, context)
        else:
            reply = _call_huggingface(message, user, context)
    except (requests.RequestException, ValueError, KeyError):
        logger.exception("AI provider call failed for provider '%s'.", provider)
        reply = ""

    return reply or _rule_based_response(message, context)
