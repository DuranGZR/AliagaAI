from groq import AsyncGroq
from app.config import get_settings
import logging

logger = logging.getLogger(__name__)
settings = get_settings()


class LLMService:
    def __init__(self) -> None:
        self._client = AsyncGroq(api_key=settings.groq_api_key)

    async def generate_response(self, query: str, context: str, system_prompt: str | None = None) -> str:
        if not system_prompt:
            system_prompt = (
                "Sen Aliağa şehir rehberi asistanısın. "
                "Sadece sana verilen bağlam bilgilerini kullanarak cevap ver. "
                "Bağlamda olmayan bilgileri uydurma. "
                "Türkçe, samimi ve kısa cevap ver. "
                "Eğer bağlamda yeterli bilgi yoksa, bunu belirt."
            )

        messages = [
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": f"Kullanıcı Sorusu: {query}\n\nBağlam Bilgisi:\n{context}",
            },
        ]

        try:
            response = await self._client.chat.completions.create(
                model=settings.groq_model,
                messages=messages,
                temperature=settings.groq_temperature,
                max_tokens=settings.groq_max_tokens,
            )
            return response.choices[0].message.content or ""
        except Exception as e:
            logger.error(f"LLM error: {e}")
            return "Üzgünüm, şu anda yanıt oluşturulamıyor. Lütfen tekrar deneyin."

    async def classify_intent(self, query: str) -> dict:
        system_prompt = (
            "Kullanıcının sorusunu analiz et ve aşağıdaki JSON formatında sınıflandır. "
            "Sadece JSON döndür, başka bir şey yazma.\n\n"
            '{"intent": "<sql|rag|hybrid>", "category": "<pharmacy|place|institution|news|event|announcement|tourism|general>", "filters": {}}\n\n'
            "Kurallar:\n"
            "- Nöbetçi eczane, mekan, kurum gibi yapılandırılmış veri soruları → sql\n"
            "- Haber, duyuru, etkinlik gibi metin araması gerektiren sorular → rag\n"
            "- Öneri, tavsiye gibi hem veri hem bağlam gerektiren sorular → hybrid\n"
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query},
        ]

        try:
            response = await self._client.chat.completions.create(
                model=settings.groq_model,
                messages=messages,
                temperature=0.0,
                max_tokens=200,
            )
            import json
            content = response.choices[0].message.content or "{}"
            content = content.strip()
            if content.startswith("```"):
                content = content.split("\n", 1)[-1].rsplit("```", 1)[0]
            return json.loads(content)
        except Exception as e:
            logger.error(f"Intent classification error: {e}")
            return {"intent": "hybrid", "category": "general", "filters": {}}
