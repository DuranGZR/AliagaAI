"""AliagaAI LLM service (OpenAI & Groq with Fallback)."""
from __future__ import annotations

import asyncio
import json
from typing import Any, Callable, Awaitable

from groq import AsyncGroq
from openai import AsyncOpenAI
from loguru import logger

from app.core.config import settings


# Lazy-loaded LLM clients (ilk kullanımda oluşturulur, test edilebilirliği artırır)
_openai_client: AsyncOpenAI | None = None
_groq_client: AsyncGroq | None = None
_clients_initialized: bool = False


def _init_clients() -> None:
    """LLM istemcilerini lazy olarak başlatır."""
    global _openai_client, _groq_client, _clients_initialized
    if _clients_initialized:
        return

    if settings.OPENAI_API_KEY:
        _openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        logger.info("OpenAI istemcisi başlatıldı.")
    else:
        logger.warning("OPENAI_API_KEY bulunamadi. OpenAI devre disi.")

    if settings.GROQ_API_KEY:
        _groq_client = AsyncGroq(api_key=settings.GROQ_API_KEY)
        logger.info("Groq istemcisi başlatıldı.")
    else:
        logger.warning("GROQ_API_KEY bulunamadi. Groq devre disi.")

    _clients_initialized = True


def _build_providers(model_override: str | None = None) -> list[dict[str, Any]]:
    """Aktif LLM sağlayıcılarının listesini döndürür.
    OpenAI birincil, Groq ikincil olarak sıralanır."""
    _init_clients()
    providers: list[dict[str, Any]] = []

    if _openai_client:
        providers.append({
            "name": "OpenAI",
            "client": _openai_client,
            "default_model": settings.OPENAI_MODEL,
        })

    if _groq_client:
        providers.append({
            "name": "Groq",
            "client": _groq_client,
            "default_model": settings.GROQ_MODEL,
        })

    for p in providers:
        p["selected_model"] = model_override or p["default_model"]

    return providers


async def _call_with_fallback(
    call_fn: Callable[[Any, str], Awaitable[Any]],
    label: str = "LLM",
) -> Any | None:
    """
    Tüm sağlayıcıları sırayla dener, her birinde LLM_MAX_RETRIES kadar tekrar yapar.

    call_fn(client, model_name) -> Any
        Başarılı sonuç dönerse, değer geri iletilir.
        Exception fırlatırsa retry/fallback mekanizması çalışır.
    """
    providers = _build_providers()

    if not providers:
        logger.error(f"[{label}] Hiçbir LLM istemcisi (OpenAI veya Groq) aktif değil.")
        return None

    last_exc = None
    for provider in providers:
        client = provider["client"]
        name = provider["name"]
        provider_model = provider["selected_model"]

        retries = max(1, settings.LLM_MAX_RETRIES)
        delay = 1.0

        for attempt in range(retries):
            try:
                result = await call_fn(client, provider_model)
                logger.info(f"[{label}] [{name}] Yanıt başarıyla alındı (Model: {provider_model})")
                return result
            except Exception as exc:
                last_exc = exc
                logger.warning(
                    f"[{label}] [{name}] API hatası (deneme {attempt + 1}/{retries}): {exc}"
                )
                if attempt < retries - 1:
                    await asyncio.sleep(delay)
                    delay *= 1.5

        logger.warning(f"[{label}] [{name}] sağlayıcısı başarısız oldu. Diğer sağlayıcıya geçiliyor...")

    logger.error(f"[{label}] Tüm LLM sağlayıcıları başarısız oldu. Son hata: {last_exc}")
    return None


async def generate_chat_response(
    messages: list[dict],
    model: str | None = None,
    response_format: dict | None = None,
    temperature: float = 0.0,
    max_tokens: int | None = None,
) -> str | None:
    """Chat completion çağrısı yapar.
    Öncelikle OpenAI (birincil) dener, başarısız olursa Groq (ikincil) modeline döner."""

    async def _call(client, model_name: str):
        kwargs: dict[str, Any] = {
            "messages": messages,
            "model": model_name,
            "temperature": temperature,
            "max_tokens": max_tokens or settings.LLM_DEFAULT_MAX_TOKENS,
            "timeout": 12.0,
        }
        if response_format:
            kwargs["response_format"] = response_format

        completion = await client.chat.completions.create(**kwargs)
        return completion.choices[0].message.content

    # modele özel override varsa provider'lara uygula
    if model:
        providers = _build_providers(model)
        for p in providers:
            p["selected_model"] = model

    return await _call_with_fallback(_call, label="Chat")


async def get_json_response(
    messages: list[dict],
    model: str | None = None,
    temperature: float = 0.0,
    max_tokens: int | None = None,
) -> dict:
    """Call model and parse JSON object response."""
    response_text = await generate_chat_response(
        messages=messages,
        model=model,
        response_format={"type": "json_object"},
        temperature=temperature,
        max_tokens=max_tokens,
    )
    if not response_text:
        return {}

    try:
        return json.loads(response_text)
    except json.JSONDecodeError as exc:
        logger.error(f"LLM cikti JSON formatinda degil: {exc}\nCikti: {response_text}")
        return {}


async def create_tool_completion(
    messages: list[dict],
    tools: list[dict],
    model: str | None = None,
    temperature: float = 0.1,
    max_tokens: int | None = None,
) -> object | None:
    """Groq veya OpenAI Tool Calling API çağrısı.
    Öncelikle OpenAI (birincil) dener, başarısız olursa Groq (ikincil) modeline döner."""

    async def _call(client, model_name: str):
        return await client.chat.completions.create(
            messages=messages,
            model=model_name,
            temperature=temperature,
            max_tokens=max_tokens or settings.LLM_DEFAULT_MAX_TOKENS,
            tools=tools,
            tool_choice="auto",
            timeout=12.0,
        )

    # modele özel override varsa provider'lara uygula
    if model:
        providers = _build_providers(model)
        for p in providers:
            p["selected_model"] = model

    return await _call_with_fallback(_call, label="Tool")
