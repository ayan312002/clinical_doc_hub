import json
import logging

import httpx

from backend.app.config import settings

logger = logging.getLogger(__name__)


async def call_llm(
    system_prompt: str,
    user_content: str,
    response_format: str | None = "json_object",
    max_tokens: int | None = None,
    image_base64: str | None = None,
) -> dict | str:
    messages = [{"role": "system", "content": system_prompt}]

    if image_base64:
        messages.append(
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": user_content},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/png;base64,{image_base64}"},
                    },
                ],
            }
        )
    else:
        messages.append({"role": "user", "content": user_content})

    payload = {
        "model": settings.LLM_MODEL,
        "messages": messages,
        "max_tokens": max_tokens or settings.LLM_MAX_TOKENS,
        "temperature": settings.LLM_TEMPERATURE,
    }
    if response_format:
        payload["response_format"] = {"type": response_format}

    headers = {
        "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://clinical-doc-hub.local",
        "X-Title": "Clinical Document Intelligence Hub",
    }

    async with httpx.AsyncClient(timeout=120.0) as client:
        try:
            resp = await client.post(
                f"{settings.OPENROUTER_BASE_URL}/chat/completions",
                headers=headers,
                json=payload,
            )
            resp.raise_for_status()
            data = resp.json()
            content = data["choices"][0]["message"]["content"]

            if not content or not content.strip():
                raise ValueError("LLM returned empty response")

            if response_format == "json_object":
                return json.loads(content)
            return content

        except httpx.HTTPStatusError as e:
            logger.error(f"OpenRouter HTTP error {e.response.status_code}: {e.response.text}")
            raise
        except (json.JSONDecodeError, ValueError) as e:
            logger.warning(f"LLM response parse failed: {e}")
            raise
        except Exception as e:
            logger.error(f"LLM call failed: {e}")
            raise


async def call_llm_with_retry(
    system_prompt: str,
    user_content: str,
    response_format: str | None = "json_object",
    max_tokens: int | None = None,
    image_base64: str | None = None,
    max_retries: int = 1,
) -> dict | str:
    last_error = None
    for attempt in range(max_retries + 1):
        try:
            return await call_llm(
                system_prompt=system_prompt,
                user_content=user_content,
                response_format=response_format,
                max_tokens=max_tokens,
                image_base64=image_base64,
            )
        except (ValueError, json.JSONDecodeError) as e:
            last_error = e
            if attempt < max_retries:
                logger.warning(f"LLM attempt {attempt + 1} failed: {e}, retrying...")
                continue
    raise last_error
