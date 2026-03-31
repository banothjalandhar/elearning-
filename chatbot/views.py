import json

from django.http import JsonResponse
from django.views.decorators.http import require_POST

from accounts.ai_service import generate_ai_response


@require_POST
def chatbot_api(request):
    try:
        payload = json.loads(request.body or "{}")
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON payload."}, status=400)

    user_message = str(payload.get("message", "")).strip()
    if not user_message:
        return JsonResponse(
            {
                "reply": (
                    "Hello! I can help with coding doubts, placement prep, course info, fees, batch timings, exam info, and contact details."
                )
            }
        )

    history = request.session.get("chatbot_history", [])
    chat_user = request.user
    if getattr(request.user, "is_authenticated", False):
        chat_user._chatbot_history = history[-5:]
    else:
        class GuestChatUser:
            is_authenticated = False

        chat_user = GuestChatUser()
        chat_user._chatbot_history = history[-5:]

    reply = generate_ai_response(user_message, chat_user)

    updated_history = (history + [{"role": "user", "content": user_message}, {"role": "assistant", "content": reply}])[-10:]
    request.session["chatbot_history"] = updated_history

    return JsonResponse({"reply": reply})
