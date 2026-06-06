"""
AliağaAI — Groq Tool Calling JSON Şema Tanımları.

Her araç Groq API'nin beklediği OpenAI-uyumlu tool tanımı formatındadır.
LLM bu tanımları okuyarak hangi aracı ne zaman çağıracağını belirler.
"""
from __future__ import annotations

TOOL_DEFINITIONS: list[dict] = [
    {
        "type": "function",
        "function": {
            "name": "search_knowledge",
            "description": (
                "Aliağa hakkında genel bilgi, tarih, coğrafya, gezi, turizm, "
                "ulaşım (İZBAN, feribot, otobüs), kurumlar, mahalleler, sanayi, "
                "nüfus, kültür ve belediye hizmetleri gibi konularda veritabanında "
                "hibrit (vektör + kelime) arama yapar. Kullanıcı Aliağa hakkında "
                "genel bir soru sorduğunda veya belirli bir konu hakkında bilgi "
                "istediğinde bu aracı kullan."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": (
                            "Veritabanında aranacak sorgu metni. "
                            "Kullanıcının sorusunun anahtar kavramlarını içermeli."
                        ),
                    }
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_duty_pharmacies",
            "description": (
                "Bugünkü nöbetçi eczaneleri getirir. Kullanıcı eczane, "
                "nöbetçi eczane veya ilaç konusunda sorduğunda kullan."
            ),
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": (
                "Aliağa/İzmir için güncel hava durumu bilgisini getirir. "
                "Sıcaklık, nem, rüzgar ve genel durum bilgisi içerir."
            ),
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_prayer_times",
            "description": (
                "Güncel namaz vakitlerini getirir: imsak, güneş, öğle, "
                "ikindi, akşam, yatsı. Ezan saatleri sorulduğunda kullan."
            ),
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_fuel_prices",
            "description": (
                "Güncel akaryakıt fiyatlarını getirir: benzin, motorin, LPG."
            ),
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_currency_rates",
            "description": (
                "Güncel döviz kurlarını getirir: dolar, euro ve diğer "
                "para birimleri için alış/satış fiyatları."
            ),
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_gold_prices",
            "description": (
                "Güncel altın fiyatlarını getirir: gram altın, çeyrek altın "
                "ve diğer altın türleri için alış/satış fiyatları."
            ),
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_recent_earthquakes",
            "description": (
                "Son 5 depremi listeler. Büyüklük, konum, derinlik ve "
                "tarih bilgisi içerir. Kandilli/AFAD verileri."
            ),
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_emergency_contacts",
            "description": (
                "Acil durum ve önemli telefon numaralarını listeler: "
                "112, itfaiye, polis, jandarma, belediye ve altyapı numaraları."
            ),
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_news_events",
            "description": (
                "Aliağa'daki son haberleri, etkinlikleri, duyuruları, "
                "belediye projelerini, iş ilanlarını, su/elektrik kesintilerini "
                "ve semt pazarlarını arar. Güncel gelişmeler veya belirli "
                "bir konu hakkında içerik istendiğinde kullan."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Aranacak konu veya anahtar kelimeler",
                    }
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_transport_schedules",
            "description": (
                "Aliağa İZBAN tren saatlerini veya feribot sefer saatlerini listeler. "
                "İlgili ulaşım saatleri veya kalkış seferleri sorulduğunda bu aracı kullan."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "mode": {
                        "type": "string",
                        "enum": ["izban", "ferry"],
                        "description": "Ulaşım modu: 'izban' (banliyö treni) veya 'ferry' (feribot)",
                    },
                    "station": {
                        "type": "string",
                        "description": "Filtrelenecek kalkış istasyonu (örn: Aliağa)",
                    },
                    "direction": {
                        "type": "string",
                        "description": "Filtrelenecek yön (örn: Cumaovası)",
                    },
                },
                "required": ["mode"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_taxi_stands",
            "description": (
                "Aliağa taksi duraklarının telefon numaralarını, adreslerini ve "
                "çalışma saatlerini listeler. Taksi durağı, taksi çağırma veya telefon "
                "numarası arandığında bu aracı kullan."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Filtrelenecek taksi durağının adı (örn: Merkez Taksi)",
                    }
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_postal_codes",
            "description": (
                "Aliağa mahallelerinin posta kodlarını getirir. Belirli bir mahallenin "
                "veya genel olarak Aliağa posta kodları sorulduğunda bu aracı kullan."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "neighborhood": {
                        "type": "string",
                        "description": "Posta kodu sorgulanacak mahallenin adı (örn: Atatürk veya Atatürk Mahallesi)",
                    }
                },
                "required": [],
            },
        },
    },
]
