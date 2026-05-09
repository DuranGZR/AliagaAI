from __future__ import annotations

import re

from loguru import logger

from app.services.llm import generate_chat_response, get_json_response
from app.services.persona import apply_persona_style

GROUNDED_GENERATION_PROMPT = """Sen AliağaAI'sın. Gorevin once verilen BAGLAM'daki bilgilerden dogru, acik ve kullanisli bir temel cevap uretmek.

CIKTI FORMATI (zorunlu JSON):
{"answer": "...", "used_source_ids": [1, 2], "confidence": 0.0}

Kurallar:
1) Bilgiler (adres, telefon, saat, kurum vb.) dogrudan BAGLAM icinden alinmalidir. Uydurma yapma.
2) Kullanici "nerede", "iletisim", "telefon" gibi net bilgiler istediginde paragraf yerine kisa maddelerle (Adres:, Telefon:, Web:, Saatler: vb.) cevap ver.
3) BAGLAM'da net adres veya telefon yoksa, kullaniciyi bir web sitesine "ziyaret edebilirsiniz" diyerek gecistirme; "Eldeki kaynaklarda acik adres/telefon bilgisi bulunamadi" seklinde net belirt.
4) "Yaklasan etkinlikler" gibi zaman sorulan durumlarda, BAGLAM'daki eski tarihli etkinlikleri guncel veya yaklasacak gibi sunma. Sadece etkinlikleri listele.
5) Eger kullanici bugun, yarin veya belli bir konu hakkinda israrla soruyor ve BAGLAM'da hicbir kayit yoksa, "Eldeki kaynaklarda bu bilgiye ulasamadim" de. "Yoktur" gibi kesin konusma.
6) Cevap metnine [Sx] etiketleri yazma; kaynak indekslerini sadece used_source_ids icinde bildir.
7) confidence 0.0-1.0 arasinda ver (Eger sorulan ana bilgi baglamda yoksa dusuk tut).
"""

AUGMENTATION_PROMPT = """Sen AliağaAI'sın. Verilen TEMEL CEVAP'i, model bilgisini kontrollu kullanarak zenginlestir.

CIKTI FORMATI (zorunlu JSON):
{"augmentation": "...", "adds_new_information": true, "confidence": 0.0}

Kurallar:
1) TEMEL CEVAP'taki yerel olgularla celisme; celisen bir sey uretme.
2) BAGLAM'da gecmeyen yeni yerel sayi/tarih/saat/fiyat/kurum/mahalle bilgisi ekleme.
3) Zenginlestirme sadece genel arka plan, pratik oneriler, yorumlama veya planlama ipuclari olsun.
4) Eger guvenli ve faydali bir ekleme yoksa augmentation bos string, adds_new_information false olsun.
5) augmentation en fazla 3 cumle olsun ve TEMEL CEVAP'i tekrar etmesin.
6) confidence 0.0-1.0 araliginda olsun.
"""

MODEL_ONLY_FALLBACK_PROMPT = """Sen AliağaAI'sın. Veritabaninda kaynak olmasa da kullaniciya faydali bir ilk yanit ver.

Kurallar:
1) Sadece genel bilgi ve guvenli oneri ver; canli/guncel yerel veri (saat, fiyat, nobet, kesin tarih) uydurma.
2) Yerel kesinlik gerektiren kisimlarda dogrulama ihtiyaci oldugunu kibarca belirt.
3) 3-7 cumlelik akici Turkce cevap yaz.
4) Cevabi dogrudan kullaniciya ver; JSON degil, duz metin.
"""


class GenerationService:
    @staticmethod
    async def generate_grounded_answer(
        user_message: str,
        context_data: str,
        conversation_history: list[dict[str, str]] | None = None,
    ) -> tuple[str, list[int], float]:
        """Verilen bağlama dayalı olarak JSON formatında cevap üretir."""
        if not context_data.strip():
            return "", [], 0.0

        messages = [
            {"role": "system", "content": GROUNDED_GENERATION_PROMPT},
        ]
        
        if conversation_history:
            for row in conversation_history[-4:]:
                r_role = row.get("role")
                r_content = row.get("content")
                if r_role in ("user", "assistant") and r_content:
                    messages.append({"role": r_role, "content": r_content})

        messages.append({
            "role": "user",
            "content": f"BAGLAM:\n{context_data}\n\nSORU: {user_message}",
        })

        try:
            payload = await get_json_response(messages, temperature=0.0)
            ans = str(payload.get("answer") or "").strip()
            
            used_ids_raw = payload.get("used_source_ids", [])
            used_ids = []
            if isinstance(used_ids_raw, list):
                for val in used_ids_raw:
                    try:
                        used_ids.append(int(val))
                    except (ValueError, TypeError):
                        pass

            conf = 0.0
            try:
                conf = float(payload.get("confidence", 0.0))
            except (ValueError, TypeError):
                pass
            
            return ans, used_ids, conf
        except Exception as e:
            logger.error(f"Grounded generation hatası: {e}")
            return "", [], 0.0

    @staticmethod
    async def generate_augmentation(
        user_message: str,
        context_data: str,
        grounded_answer: str,
        conversation_history: list[dict[str, str]] | None = None,
    ) -> tuple[str, bool, float]:
        """Cevabı model bilgisi ile güvenli şekilde zenginleştirir."""
        messages = [
            {"role": "system", "content": AUGMENTATION_PROMPT},
        ]
        
        if conversation_history:
            for row in conversation_history[-2:]:
                r_role = row.get("role")
                r_content = row.get("content")
                if r_role in ("user", "assistant") and r_content:
                    messages.append({"role": r_role, "content": r_content})

        messages.append({
            "role": "user",
            "content": f"BAGLAM:\n{context_data}\n\nTEMEL CEVAP:\n{grounded_answer}\n\nSORU: {user_message}",
        })

        try:
            payload = await get_json_response(messages, temperature=0.3)
            aug = str(payload.get("augmentation") or "").strip()
            adds_new = bool(payload.get("adds_new_information", False))
            
            conf = 0.0
            try:
                conf = float(payload.get("confidence", 0.0))
            except (ValueError, TypeError):
                pass
                
            if len(aug) < 10 or not adds_new:
                return "", False, 0.0
                
            return aug, True, conf
        except Exception as e:
            logger.error(f"Augmentation hatası: {e}")
            return "", False, 0.0

    @staticmethod
    async def generate_fallback_answer(
        user_message: str,
        conversation_history: list[dict[str, str]] | None = None,
    ) -> str:
        """Veritabanında kaynak yoksa LLM model bilgisine başvurur."""
        messages = [
            {"role": "system", "content": MODEL_ONLY_FALLBACK_PROMPT},
        ]
        
        if conversation_history:
            for row in conversation_history[-2:]:
                r_role = row.get("role")
                r_content = row.get("content")
                if r_role in ("user", "assistant") and r_content:
                    messages.append({"role": r_role, "content": r_content})
                    
        messages.append({"role": "user", "content": user_message})
        
        try:
            ans = await generate_chat_response(messages, temperature=0.2, response_format=None)
            return (ans or "").strip()
        except Exception as e:
            logger.error(f"Fallback generation hatası: {e}")
            return ""
