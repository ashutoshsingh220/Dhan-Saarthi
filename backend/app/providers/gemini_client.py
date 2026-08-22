import logging
from google import genai
from google.genai import types

from app.core.config import settings

logger = logging.getLogger(__name__)


class GeminiClient:
    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or settings.gemini_api_key

    def generate_response(
        self,
        system_instruction: str,
        user_context: str,
        history: list[dict[str, str]],
        user_message: str,
    ) -> str:
        if not self.api_key or self.api_key.startswith("replace_") or "mock" in self.api_key:
            logger.warning("No valid GEMINI_API_KEY configured. Returning fallback AI response.")
            return (
                "Saarthi AI is currently operating in offline mode. "
                "To enable real-time personalized AI responses, configure your valid GEMINI_API_KEY in backend/.env.local."
            )

        try:
            client = genai.Client(api_key=self.api_key)

            full_system_instruction = f"{system_instruction}\n\n{user_context}"

            contents = []
            for item in history:
                role = "user" if item["role"] == "user" else "model"
                contents.append(
                    types.Content(
                        role=role,
                        parts=[types.Part.from_text(text=item["content"])],
                    )
                )

            contents.append(
                types.Content(
                    role="user",
                    parts=[types.Part.from_text(text=user_message)],
                )
            )

            config = types.GenerateContentConfig(
                system_instruction=full_system_instruction,
                temperature=0.7,
                max_output_tokens=3072,
            )

            models_to_try = [
                "models/gemini-3.6-flash",
                "models/gemini-3.5-flash",
                "models/gemini-flash-latest",
                "models/gemini-pro-latest",
            ]
            last_err = None

            for model_name in models_to_try:
                try:
                    response = client.models.generate_content(
                        model=model_name,
                        contents=contents,
                        config=config,
                    )
                    if response and response.text:
                        return response.text.strip()
                except Exception as ex:
                    last_err = ex
                    logger.debug(f"Model {model_name} failed: {ex}")
                    continue

            if last_err:
                raise last_err

            return "Saarthi received an empty response. Please try asking your question again."

        except Exception as e:
            err_msg = str(e)
            logger.error(f"Gemini API invocation failed: {type(e).__name__} - {err_msg}")

            if "PERMISSION_DENIED" in err_msg or "API_KEY_INVALID" in err_msg or "403" in err_msg:
                return (
                    "Saarthi AI API key is invalid or unauthorized (403 Permission Denied). "
                    "Please check your GEMINI_API_KEY in backend/.env.local and get a valid key from Google AI Studio."
                )

            return f"Saarthi AI encounter: {err_msg[:120]}... Please try asking your question again."

    def generate_response_stream(
        self,
        system_instruction: str,
        user_context: str,
        history: list[dict[str, str]],
        user_message: str,
    ):
        """
        Generates streaming chunks for AI Saarthi chat responses.
        Yields text chunks as they arrive from Gemini API.
        """
        if not self.api_key or self.api_key.startswith("replace_") or "mock" in self.api_key:
            logger.warning("No valid GEMINI_API_KEY configured. Returning fallback AI streaming response.")
            yield (
                "Saarthi AI is currently operating in offline mode. "
                "To enable real-time personalized AI responses, configure your valid GEMINI_API_KEY in backend/.env.local."
            )
            return

        try:
            client = genai.Client(api_key=self.api_key)
            full_system_instruction = f"{system_instruction}\n\n{user_context}"

            contents = []
            for item in history:
                role = "user" if item["role"] == "user" else "model"
                contents.append(
                    types.Content(
                        role=role,
                        parts=[types.Part.from_text(text=item["content"])],
                    )
                )

            contents.append(
                types.Content(
                    role="user",
                    parts=[types.Part.from_text(text=user_message)],
                )
            )

            config = types.GenerateContentConfig(
                system_instruction=full_system_instruction,
                temperature=0.7,
                max_output_tokens=3072,
            )

            models_to_try = [
                "models/gemini-3.6-flash",
                "models/gemini-3.5-flash",
                "models/gemini-flash-latest",
                "models/gemini-pro-latest",
            ]
            stream_success = False

            for model_name in models_to_try:
                try:
                    response_stream = client.models.generate_content_stream(
                        model=model_name,
                        contents=contents,
                        config=config,
                    )
                    for chunk in response_stream:
                        if chunk and chunk.text:
                            stream_success = True
                            yield chunk.text
                    if stream_success:
                        return
                except Exception as ex:
                    logger.debug(f"Streaming model {model_name} failed: {ex}")
                    continue

            yield "Saarthi received an empty response. Please try asking your question again."

        except Exception as e:
            err_msg = str(e)
            logger.error(f"Gemini API streaming failed: {type(e).__name__} - {err_msg}")
            yield f"Saarthi AI encounter: {err_msg[:120]}... Please try asking your question again."
