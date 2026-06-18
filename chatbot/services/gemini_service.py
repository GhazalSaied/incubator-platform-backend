from pathlib import Path

from django.conf import settings
from google import genai

from chatbot.models import ChatMessage


PROMPTS = {
    "backend": "backend.txt",
    "frontend": "frontend.txt",
    "ui_ux": "uiux.txt",
    "marketing": "marketing.txt",
    "business": "business.txt",
    "legal": "legal.txt",
}


class GeminiService:

    @staticmethod
    def generate_response(session, user_message):

        prompt_file = PROMPTS.get(
            session.consultation_field,
            "business.txt"
        )

        prompt_path = (
            Path(__file__).resolve().parent.parent
            / "prompts"
            / prompt_file
        )

        with open(prompt_path, "r", encoding="utf-8") as file:
            system_prompt = file.read()

        messages = ChatMessage.objects.filter(
            session=session
        ).order_by("-created_at")[:15]

        messages = reversed(messages)

        conversation_history = ""

        for msg in messages:
            conversation_history += (
                f"{msg.sender}: {msg.content}\n"
            )

        prompt = f"""
{system_prompt}

سجل المحادثة السابقة:

{conversation_history}

رسالة المستخدم الحالية:

{user_message}

أجب وفق تخصصك فقط.
إذا كان السؤال خارج مجال تخصصك اطلب من المستخدم الانتقال إلى المستشار المناسب.
"""

        client = genai.Client(
            api_key=settings.GEMINI_API_KEY
        )

        response = client.models.generate_content(
            model="gemini-3.1-flash-lite",
            contents=prompt
        )

        return response.text


    @staticmethod
    def stream_response(session, user_message):

        prompt_file = PROMPTS.get(
            session.consultation_field,
            "business.txt"
        )

        prompt_path = (
            Path(__file__).resolve().parent.parent
            / "prompts"
            / prompt_file
        )

        with open(prompt_path, "r", encoding="utf-8") as file:
            system_prompt = file.read()

        messages = ChatMessage.objects.filter(
            session=session
        ).order_by("-created_at")[:10]

        messages = reversed(messages)

        conversation_history = ""
        for msg in messages:
            conversation_history += f"{msg.sender}: {msg.content}\n"

        prompt = f"""
{system_prompt}

سجل المحادثة السابقة:
{conversation_history}

رسالة المستخدم:
{user_message}
"""

        client = genai.Client(api_key=settings.GEMINI_API_KEY)

        response = client.models.generate_content_stream(
            model="gemini-3.1-flash-lite",
            contents=prompt
        )

        for chunk in response:
            if chunk.text:
                yield chunk.text