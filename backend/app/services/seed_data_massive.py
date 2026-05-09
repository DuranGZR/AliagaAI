"""
AliağaAI - Devasa Veri Dosyası
Bu dosya RAG sistemi için Aliağa hakkında detaylı, geniş kapsamlı mekan, kurum, mahalle ve bilgi verilerini içerir.
"""
from datetime import date

EMERGENCY_CONTACTS = [
    {"name": "Polis İmdat", "phone": "112", "category": "acil", "priority": 1},
    {"name": "Ambulans / Acil Yardım", "phone": "112", "category": "acil", "priority": 0},
    {"name": "İtfaiye", "phone": "112", "category": "acil", "priority": 2},
    {"name": "Jandarma", "phone": "112", "category": "acil", "priority": 3},
    {"name": "Sahil Güvenlik", "phone": "112", "category": "acil", "priority": 4},
    {"name": "İZSU Arıza", "phone": "185", "category": "altyapi", "priority": 10},
    {"name": "GDZ Elektrik Arıza", "phone": "186", "category": "altyapi", "priority": 11},
    {"name": "Doğalgaz Arıza (İzmirgaz)", "phone": "187", "category": "altyapi", "priority": 13},
    {"name": "Cenaze Hizmetleri (Belediye)", "phone": "188", "category": "belediye", "priority": 20},
    {"name": "Aliağa Belediyesi Çözüm Masası", "phone": "153", "category": "belediye", "priority": 21},
    {"name": "Aliağa Belediyesi Ana Santral", "phone": "0232 399 00 00", "category": "belediye", "priority": 22},
]

STREET_MARKETS = [
    {
        "name": "Çarşamba Pazarı (Merkez Pazarı)",
        "day_of_week": "carsamba",
        "neighborhood": "Yeni Mahalle",
        "address": "Cengiz Topel Caddesi, Yeni Mahalle, Aliağa",
        "description": "Aliağa'nın en büyük, en kalabalık semt pazarıdır. Sebze, meyve, giyim ve ev eşyaları bulunur.",
    },
    {
        "name": "Kapalı Pazar (Cumartesi Pazarı)",
        "day_of_week": "cumartesi",
        "neighborhood": "Atatürk Mahallesi",
        "address": "Beyazıt Caddesi No:6, Atatürk Mahallesi, Aliağa",
        "description": "Cumartesi günleri Aliağa Kapalı Pazaryerinde kurulan, düzenli ve yoğun bir pazardır.",
    },
    {
        "name": "Yeni Şakran Pazarı",
        "day_of_week": "cuma",
        "neighborhood": "Yeni Şakran",
        "address": "İnönü Caddesi / Atatürk Caddesi, Yeni Şakran, Aliağa",
        "description": "Yeni Şakran beldesinin yerel pazarı. Cuma günleri kurulur ve özellikle yaz aylarında kalabalık olur.",
    },
    {
        "name": "Helvacı Pazarı",
        "day_of_week": "cuma",
        "neighborhood": "Helvacı",
        "address": "Mimar Sinan Mahallesi / Fatih Mahallesi, Helvacı, Aliağa",
        "description": "Helvacı bölgesindeki halkın ihtiyaçlarını karşıladığı yerel cuma pazarı.",
    },
]

PLACES = [
    # Yeme-İçme: Balık & Deniz Ürünleri
    {
        "name": "Aliağa Balıkevi",
        "category": "restoran",
        "subcategory": "balik",
        "description": "Aliağa Sahili'nde, deniz manzarasına karşı taze günlük balık ve zeytinyağlı Ege mezeleri sunan meşhur restoran.",
        "tags": ["deniz ürünleri", "balık", "manzaralı", "sahil", "meze", "alkollü"],
    },
    {
        "name": "İzzet Usta Et & Balık",
        "category": "restoran",
        "subcategory": "balik",
        "description": "Hem et mangal hem de günlük balık çeşitleri ile Aliağa'nın köklü ve güvenilir restoranlarından biri.",
        "tags": ["et", "balık", "aile dostu", "mangal", "ızgara"],
    },
    {
        "name": "Radika Balık Restoran",
        "category": "restoran",
        "subcategory": "balik",
        "description": "Deniz kıyısında, şık konsepti ve çeşitli Ege otlarından oluşan mezeleriyle dikkat çeken deniz ürünleri restoranı.",
        "tags": ["balık", "meze", "radika", "deniz kenarı"],
    },
    # Yeme-İçme: Et & Kebap
    {
        "name": "Chef Âlâ Ocakbaşı",
        "category": "restoran",
        "subcategory": "kebap",
        "description": "Adana, Urfa ve zırh kebabı gibi ocakbaşı kültürünü Aliağa'da yaşatan elit et restoranı.",
        "tags": ["ocakbaşı", "ızgara", "kebap", "et"],
    },
    {
        "name": "Pasha Mangalbaşi",
        "category": "restoran",
        "subcategory": "kebap",
        "description": "Masalarda kendin pişir kendin ye konsepti sunan, geniş aile grupları için uygun mangal restoranı.",
        "tags": ["mangal", "kendin pişir", "aile", "kebap"],
    },
    {
        "name": "Cennet Vadisi Restoran",
        "category": "restoran",
        "subcategory": "kahvalti",
        "description": "Özellikle hafta sonu serpme kahvaltısı ve doğa içindeki huzurlu ortamıyla bilinen kahvaltı ve et mangal mekanı.",
        "tags": ["kahvaltı", "serpme kahvaltı", "doğa", "mangal"],
    },
    {
        "name": "Çamlıkeler Kavurma",
        "category": "restoran",
        "subcategory": "et",
        "description": "Aliağa-İzmir yolu üzerinde yıllardır efsaneleşmiş sac kavurmasıyla bilinen meşhur durak lezzeti.",
        "tags": ["kavurma", "sac kavurma", "yol üstü"],
    },
    # Yeme-İçme: Ev Yemekleri & Pide
    {
        "name": "Deniz'in Mutfağı",
        "category": "restoran",
        "subcategory": "ev_yemekleri",
        "description": "Aliağa merkezde, anne eli değmiş gibi özenle hazırlanan sulu yemekler ve zeytinyağlılar sunan lokanta.",
        "tags": ["ev yemekleri", "sulu yemek", "öğle yemeği"],
    },
    {
        "name": "Azim Pide",
        "category": "restoran",
        "subcategory": "pide",
        "description": "Çıtır lahmacunları ve özel peynirli Karadeniz pideleriyle yılların esnaf lokantası.",
        "tags": ["pide", "lahmacun", "esnaf lokantası"],
    },
    {
        "name": "Konyalı Mirzaoğlu",
        "category": "restoran",
        "subcategory": "etli_ekmek",
        "description": "Hakiki Konya etli ekmeği, bıçakarası ve fırın kebabı yapan meşhur restoran.",
        "tags": ["etli ekmek", "konya mutfağı", "kebap"],
    },
    # Kafeler & Barlar
    {
        "name": "Seyir Cafe & Restaurant",
        "category": "kafe",
        "subcategory": "kafe",
        "description": "Aliağa sahilinde deniz manzaralı, geniş oturma alanına sahip, kahve, nargile ve hafif yemek seçenekleri sunan kafe.",
        "tags": ["deniz manzaralı", "nargile", "kahve", "tatlı"],
    },
    {
        "name": "Liman Cafe Bar",
        "category": "kafe",
        "subcategory": "bar",
        "description": "Aliağa merkez sahilde, canlı müzik dinlenebilecek ve akşamları sosyalleşilebilecek modern pub.",
        "tags": ["pub", "canlı müzik", "gece hayatı", "bira"],
    },
    # Turistik Yerler: Antik Kentler
    {
        "name": "Aigai Antik Kenti",
        "category": "turistik",
        "subcategory": "antik_kent",
        "description": "Yunt Dağı eteklerinde (Gün Dağı) yer alan, Aiolis bölgesinin 12 antik kentinden biridir. Harika korunmuş bir Agora (pazar yeri), meclis binası (Bouleuterion) ve taş döşeli antik yollara sahiptir. M.Ö. 8. yüzyılda kurulmuştur. Ziyaretçiler için harika bir doğa ve tarih yürüyüşü sunar.",
        "tags": ["antik kent", "tarih", "arkeoloji", "doğa yürüyüşü", "aiolis"],
    },
    {
        "name": "Kyme Antik Kenti",
        "category": "turistik",
        "subcategory": "antik_kent",
        "description": "Aliağa Nemrut Limanı yakınlarında yer alan, Batı Anadolu'nun en büyük ve en güçlü Aiolis kentlerinden biridir. Amazon Kraliçesi Kyme tarafından kurulduğu rivayet edilir. Kenti ünlü kılan şey, o dönemde basılan antik sikkelerdir.",
        "tags": ["antik kent", "nemrut limanı", "tarih", "arkeoloji", "aiolis"],
    },
    {
        "name": "Gryneion Apollon Tapınağı",
        "category": "turistik",
        "subcategory": "antik_kent",
        "description": "Yeni Şakran sahil yolu üzerinde, antik dönemde Apollon'a adanmış çok önemli bir kehanet (bilicilik) merkezidir.",
        "tags": ["tapınak", "apollon", "kehanet", "antik kent", "tarih"],
    },
    {
        "name": "Myrina Antik Kenti",
        "category": "turistik",
        "subcategory": "antik_kent",
        "description": "Aliağa yakınlarında, özellikle antik dönem Pişmiş Toprak (Terrakotta) heykelcikleriyle dünyaca ünlü Aiolis kenti.",
        "tags": ["antik kent", "heykelcik", "terrakotta", "tarih"],
    },
    # Turistik Yerler: Plajlar ve Doğa
    {
        "name": "Ağapark Plajı ve Sosyal Tesisleri",
        "category": "turistik",
        "subcategory": "plaj",
        "description": "Aliağa Belediyesi tarafından işletilen, mavi bayraklı, ince kumlu plaja sahip büyük bir tesis. İçinde yürüyüş yolları, kafeteryalar, çocuk oyun alanları ve şezlong kiralama hizmeti bulunur.",
        "tags": ["plaj", "deniz", "yüzme", "sosyal tesis", "belediye", "kum"],
    },
    {
        "name": "Yeni Şakran Sahili",
        "category": "turistik",
        "subcategory": "sahil",
        "description": "Yaz aylarında yazlıkçıların akınına uğrayan, uzun bir kordona sahip, sakin sularıyla bilinen plaj bölgesi. Akşam yürüyüşleri için idealdir.",
        "tags": ["sahil", "plaj", "kordon", "yürüyüş", "yüzme"],
    },
    {
        "name": "Kuş Cenneti (Çaltıdere Göleti)",
        "category": "turistik",
        "subcategory": "doga",
        "description": "Çaltıdere köyü sınırları içinde yer alan, flamingo, pelikan ve yaban ördekleri gibi pek çok kuş türüne ev sahipliği yapan doğal sulak alan.",
        "tags": ["doğa", "kuş gözlem", "flamingo", "gölet"],
    },
    {
        "name": "Uçansu Şelalesi",
        "category": "turistik",
        "subcategory": "doga",
        "description": "Aliağa Karakuzu köyüne yakın, özellikle ilkbahar aylarında gürül gürül akan ve etrafında harika kamp/piknik alanları bulunan doğa harikası şelale.",
        "tags": ["şelale", "doğa", "kamp", "piknik", "orman"],
    },
    {
        "name": "Sahil Parkı",
        "category": "turistik",
        "subcategory": "park",
        "description": "Aliağa ilçe merkezinin sahil bandı boyunca uzanan, palmiye ağaçları, yürüyüş yolları, çay bahçeleri ve çocuk parklarıyla dolu kordon boyu.",
        "tags": ["park", "yürüyüş", "kordon", "sahil", "deniz havası"],
    },
]

INSTITUTIONS = [
    # Kamu Binaları
    {
        "name": "Aliağa Kaymakamlığı",
        "category": "kamu",
        "phone": "0232 616 10 01",
        "address": "Kültür Mahallesi, Hükümet Konağı, Aliağa / İzmir",
        "description": "İlçenin mülki idare amirliği. Hükümet Konağı içerisinde yer alır.",
    },
    {
        "name": "Aliağa İlçe Nüfus Müdürlüğü",
        "category": "kamu",
        "phone": "0232 616 46 44",
        "address": "Kültür Mahallesi, Hükümet Konağı Zemin Kat, Aliağa",
        "description": "Kimlik, pasaport ve ehliyet yenileme işlemlerinin yapıldığı müdürlük.",
    },
    {
        "name": "Aliağa Vergi Dairesi",
        "category": "kamu",
        "phone": "0232 616 14 05",
        "address": "Yeni Mahalle, İstiklal Caddesi No:85, Aliağa",
        "description": "İlçenin vergi beyan, tahsilat ve sicil işlemlerini yürüten devlet dairesi.",
    },
    {
        "name": "Aliağa İlçe Emniyet Müdürlüğü",
        "category": "kamu",
        "phone": "0232 616 10 50",
        "address": "Kültür Mahallesi, Lozan Caddesi, Aliağa",
        "description": "İlçenin güvenlik, asayiş ve trafik hizmetlerinden sorumlu ana emniyet binası.",
    },
    # Sağlık
    {
        "name": "Aliağa Devlet Hastanesi",
        "category": "saglik",
        "phone": "0232 616 10 10",
        "address": "Yeni Mahalle, Rumeli Caddesi No:2, Aliağa",
        "description": "Aliağa'nın en büyük tam teşekküllü devlet hastanesi. 7/24 Acil Servis hizmeti mevcuttur.",
        "subcategory": "hastane",
    },
    {
        "name": "Aliağa Tıp Merkezi",
        "category": "saglik",
        "phone": "0232 616 77 77",
        "address": "Atatürk Mahallesi, Fevzi Paşa Caddesi, Aliağa",
        "description": "Aliağa merkezde yer alan, poliklinik ve laboratuvar hizmetleri veren özel sağlık kuruluşu.",
        "subcategory": "hastane",
    },
    # Eğitim: Liseler
    {
        "name": "Aliağa Mesleki ve Teknik Anadolu Lisesi (TÜPRAŞ Lisesi)",
        "category": "egitim",
        "phone": "0232 616 12 50",
        "address": "Yeni Mahalle, Lise Caddesi, Aliağa",
        "description": "Aliağa'nın sanayi yapısına uygun teknik personel yetiştiren en köklü meslek lisesi.",
        "subcategory": "lise",
    },
    {
        "name": "Aliağa Alp Oğuz Anadolu Lisesi",
        "category": "egitim",
        "phone": "0232 616 66 11",
        "address": "Siteler Mahallesi, Aliağa",
        "description": "İlçenin en başarılı ve popüler Anadolu Liselerinden biridir.",
        "subcategory": "lise",
    },
    {
        "name": "Aliağa Fen Lisesi",
        "category": "egitim",
        "address": "Yeni Şakran Mahallesi, Aliağa",
        "description": "Yüksek puanla öğrenci alan, sayısal ağırlıklı proje okulu.",
        "subcategory": "lise",
    },
    {
        "name": "TED Aliağa Koleji",
        "category": "egitim",
        "phone": "0232 616 82 82",
        "address": "Çakmaklı Mahallesi, Aliağa",
        "description": "Aliağa'daki en donanımlı özel okullardan (ilkokul, ortaokul, lise) biri.",
        "subcategory": "lise",
    },
    # Belediye Hizmetleri / Sosyal / Spor
    {
        "name": "Aliağa Gençlik Merkezi (AGM)",
        "category": "spor",
        "phone": "0232 616 19 80",
        "address": "Atatürk Mahallesi, Hürriyet Caddesi, Aliağa",
        "description": "İçinde yarı olimpik yüzme havuzu, fitness salonu, 3 salonlu sinema, pilates ve kafeterya bulunan devasa gençlik merkezi.",
    },
    {
        "name": "Aliağa Spor ve Yaşam Merkezi",
        "category": "spor",
        "address": "Örnekkent Mahallesi, Aliağa",
        "description": "Karate, güreş, dans salonları, kapalı spor salonu, basketbol ve futbol sahalarıyla büyük bir spor kompleksi.",
    },
    {
        "name": "ASEV (Aliağa Sanat Evi)",
        "category": "kultur",
        "address": "Kültür Mahallesi, Aliağa",
        "description": "Aliağa Belediyesi'ne bağlı sanat merkezi. Piyano, gitar, tiyatro, resim, halk oyunları kursları burada verilir.",
    },
    {
        "name": "Zeytinli Park Açıkhava Etkinlik Alanı",
        "category": "kultur",
        "address": "Atatürk Mahallesi, Sahil bandı, Aliağa",
        "description": "Özellikle yaz aylarında ünlü sanatçıların konser verdiği, yazlık sinema gösterimlerinin yapıldığı açık hava etkinlik alanı.",
    },
    {
        "name": "Aliağa Belediyesi Atatürk Kültür Merkezi",
        "category": "kultur",
        "address": "Merkez",
        "description": "Konferanslar, tiyatrolar ve resmi etkinliklere ev sahipliği yapan kapalı kültür salonu.",
    },
    # Kütüphaneler
    {
        "name": "Aliağa Kent Kitaplığı",
        "category": "kutuphane",
        "description": "Aliağa Belediyesi ana binası çevresinde, geniş kaynaklara sahip merkez kütüphane.",
    },
    {
        "name": "Aziz Sancar Kütüphanesi",
        "category": "kutuphane",
        "description": "Spor ve Yaşam Merkezi (Örnekkent) içerisinde ders çalışmak ve kitap okumak için sessiz bir kütüphane.",
    },
    {
        "name": "Nadir Nadi Kütüphanesi",
        "category": "kutuphane",
        "description": "Aliağa Gençlik Merkezi (AGM) içerisinde yer alan dijital ve basılı kaynak kütüphanesi.",
    },
    # Ulaşım & Kargo
    {
        "name": "Aliağa İZBAN İstasyonu",
        "category": "ulasim",
        "description": "İzmir banliyö sisteminin (İZBAN) kuzeydeki en son durağı. İzmir merkeze hızlı ulaşım sağlar.",
    },
    {
        "name": "Aliağa Otogarı (Eshot ve Minibüs Garajı)",
        "category": "ulasim",
        "description": "Şehir içi minibüslerin ve çevre ilçelere (Foça, Dikili, Bergama) giden otobüslerin kalkış noktası.",
    },
    {
        "name": "PTT Aliağa Merkez Şubesi",
        "category": "kargo",
        "phone": "0232 616 12 22",
        "address": "Kültür Mahallesi, Hükümet Caddesi, Aliağa",
        "description": "Kargo gönderimi, havale, e-devlet şifresi vb. posta işlemleri için ana PTT binası.",
    },
]

TAXI_STANDS = [
    {"name": "Merkez Taksi", "address": "Aliağa ilçe merkezi, İZBAN karşısı", "is_24h": True},
    {"name": "Meydan Taksi", "address": "Demokrasi Meydanı, Aliağa", "is_24h": True},
    {"name": "Hastane Taksi", "address": "Aliağa Devlet Hastanesi önü", "is_24h": True},
    {"name": "Şakran Taksi", "address": "Yeni Şakran Merkez", "is_24h": True},
]

POSTAL_CODES = [
    {"neighborhood": "Atatürk Mahallesi", "postal_code": "35800"},
    {"neighborhood": "Kültür Mahallesi", "postal_code": "35800"},
    {"neighborhood": "Yalı Mahallesi", "postal_code": "35800"},
    {"neighborhood": "Yeni Mahalle", "postal_code": "35800"},
    {"neighborhood": "Siteler Mahallesi", "postal_code": "35800"},
    {"neighborhood": "Örnekkent Mahallesi", "postal_code": "35800"},
    {"neighborhood": "Fatih Mahallesi", "postal_code": "35800"},
    {"neighborhood": "Mimar Sinan Mahallesi", "postal_code": "35800"},
    {"neighborhood": "Barbaros Mahallesi", "postal_code": "35800"},
    {"neighborhood": "Güzelhisar Mahallesi", "postal_code": "35800"},
    {"neighborhood": "Helvacı", "postal_code": "35820"},
    {"neighborhood": "Yeni Şakran", "postal_code": "35801"},
    {"neighborhood": "Çakmaklı", "postal_code": "35800"},
    {"neighborhood": "Bozköy", "postal_code": "35800"},
    {"neighborhood": "Kalabak", "postal_code": "35800"},
    {"neighborhood": "Samurlu", "postal_code": "35800"},
    {"neighborhood": "Aşağı Şakran", "postal_code": "35800"},
    {"neighborhood": "Karakuzu", "postal_code": "35800"},
    {"neighborhood": "Çaltıdere", "postal_code": "35800"},
]

CITY_KNOWLEDGE = [
    # Tarih ve Antik Kentler
    {
        "layer": "gezi",
        "title": "Aigai Antik Kenti ve Tarihçesi",
        "neighborhood": "Yunt Dağı Etekleri",
        "summary": "Aigai, Aiolis bölgesinin 12 kentinden biridir. Yunt Dağı'nda (Gün Dağı) sarp kayalıklar üzerine kurulmuştur. Keçi anlamına gelen Aigai ismi, kentin etrafındaki vahşi doğayı yansıtır. Pazaryeri (Agora) ve tiyatrosu günümüze oldukça sağlam ulaşmıştır.",
        "tags": ["antik kent", "tarih", "arkeoloji", "aigai"],
        "source_url": "https://www.aliaga.bel.tr/aliaga/antik-kentler",
        "last_verified_at": date.today(),
    },
    {
        "layer": "gezi",
        "title": "Kyme Antik Kenti Tarihi",
        "neighborhood": "Nemrut Limanı",
        "summary": "Batı Anadolu'daki en büyük Aiolis kentidir. Kyme, M.Ö. 11. yüzyılda kurulmuş olup, antik çağın en önemli liman kentlerinden biriydi. Deniz ticareti sayesinde zenginleşmiş, antik dünyada kendi adına sikke basan ilk şehirlerden olmuştur.",
        "tags": ["kyme", "antik kent", "tarih", "aiolis"],
        "source_url": "https://www.aliaga.bel.tr/aliaga/antik-kentler",
        "last_verified_at": date.today(),
    },
    {
        "layer": "gezi",
        "title": "Gryneion (Gyrneion) Apollon Tapınağı",
        "neighborhood": "Yeni Şakran",
        "summary": "Yeni Şakran sahil yolu üzerinde bulunur. Antik çağın önemli kehanet (bilicilik) merkezlerinden biriydi. Büyük İskender'in komutanı Parmenion tarafından M.Ö. 334'te yıkıldığı için tapınaktan günümüze az sayıda kalıntı ulaşmıştır.",
        "tags": ["gryneion", "apollon", "kehanet", "tarih", "şakran"],
        "source_url": "https://www.aliaga.bel.tr/aliaga/antik-kentler",
        "last_verified_at": date.today(),
    },
    # Doğa ve Plajlar
    {
        "layer": "gezi",
        "title": "Ağapark Sosyal Tesisleri ve Plajı",
        "neighborhood": "Aliağa Sahil",
        "summary": "Aliağa Belediyesi'nin büyük yatırımlarla halka kazandırdığı, mavi bayraklı muazzam bir sosyal tesis. İçinde yürüyüş yolları, restoranlar, tenis kortları, çocuk havuzları ve ince kumlu geniş bir plaj barındırır. Hafta sonu ailelerin favori noktasıdır.",
        "tags": ["ağapark", "plaj", "deniz", "yaz", "tesis", "belediye"],
        "source_url": "https://www.aliaga.bel.tr/agapark",
        "last_verified_at": date.today(),
    },
    {
        "layer": "gezi",
        "title": "Yeni Şakran ve Çandarlı Körfezi Sahili",
        "neighborhood": "Yeni Şakran",
        "summary": "Yeni Şakran sahil bandı, berrak denizi ve yazlık evleriyle ünlüdür. Kordon boyu uzun yürüyüşler için idealdir, rüzgar sörfü ve yelken sporlarına uygundur.",
        "tags": ["şakran", "plaj", "deniz", "kordon", "yürüyüş"],
        "source_url": "https://www.aliaga.bel.tr/turizm",
        "last_verified_at": date.today(),
    },
    {
        "layer": "gezi",
        "title": "Kuş Cenneti (Çaltıdere)",
        "neighborhood": "Çaltıdere",
        "summary": "Çaltıdere Köyü yakınlarındaki sulak alan, yüzlerce kuş türünün konaklama ve üreme noktasıdır. Flamingolar, pelikanlar ve gri balıkçıllar doğa fotoğrafçıları için harika manzaralar sunar.",
        "tags": ["çaltıdere", "kuş cenneti", "doğa", "fotoğraf", "flamingo"],
        "source_url": "https://www.aliaga.bel.tr/doga",
        "last_verified_at": date.today(),
    },
    {
        "layer": "gezi",
        "title": "Uçansu Şelalesi",
        "neighborhood": "Karakuzu",
        "summary": "Karakuzu köyü yakınlarındaki Uçansu Şelalesi, özellikle bahar aylarında suların yükselmesiyle harika bir görsel şölen yaratır. Çevresindeki ormanlık alan kamp ve piknik için oldukça uygundur.",
        "tags": ["şelale", "karakuzu", "doğa", "kamp", "piknik", "orman"],
        "source_url": "https://www.aliaga.bel.tr/doga",
        "last_verified_at": date.today(),
    },
    # Gastronomi
    {
        "layer": "gastronomi",
        "title": "Aliağa'nın Meşhur Yemekleri ve Tatları",
        "neighborhood": "Merkez",
        "summary": "Aliağa mutfağında Ege'nin zeytinyağlıları ve deniz ürünleri hakimdir. Özellikle radika, cibez, şevketi bostan, deniz börülcesi gibi otlar meşhurdur. Ayrıca İzmir-Çanakkale karayolu üzerindeki sac kavurma restoranları, Aliağa'nın gastronomik simgelerindendir.",
        "tags": ["gastronomi", "zeytinyağlı", "balık", "meze", "sac kavurma", "ot yemeği"],
        "source_url": "https://www.aliaga.bel.tr/gastronomi",
        "last_verified_at": date.today(),
    },
    # Ulaşım
    {
        "layer": "ulasim",
        "title": "Aliağa'ya Ulaşım: Karayolu ve Otoyol",
        "neighborhood": "Genel",
        "summary": "Aliağa, İzmir şehir merkezine yaklaşık 60 km uzaklıktadır. D-550 (İzmir-Çanakkale) Karayolu ile ulaşım sağlanır. Ayrıca yeni yapılan Kuzey Ege Otoyolu sayesinde İzmir Merkez, Karşıyaka ve Menemen üzerinden ulaşım 30 dakikaya kadar inmiştir.",
        "tags": ["ulaşım", "karayolu", "otoyol", "kuzey ege", "arabayla"],
        "source_url": "https://www.aliaga.bel.tr/ulasim",
        "last_verified_at": date.today(),
    },
    {
        "layer": "ulasim",
        "title": "Aliağa İZBAN ve Tren Ulaşımı",
        "neighborhood": "Merkez",
        "summary": "İzmir banliyö hattı İZBAN'ın kuzey aksındaki son istasyonu Aliağa'dır. Aliağa İZBAN istasyonundan kalkan trenlerle; Menemen, Çiğli, Karşıyaka, Alsancak, Şirinyer ve Adnan Menderes Havalimanı dahil olmak üzere İzmir'in her yerine kesintisiz raylı ulaşım mümkündür.",
        "tags": ["ulaşım", "izban", "tren", "banliyö", "havalimanı"],
        "source_url": "https://www.aliaga.bel.tr/ulasim",
        "last_verified_at": date.today(),
    },
    {
        "layer": "ulasim",
        "title": "Aliağa - Foça Otobüs ve Minibüsleri",
        "neighborhood": "Otogar",
        "summary": "Aliağa Otogarı'ndan ve İZBAN durağından kalkan ESHOT otobüsleri ve özel dolmuşlarla Yeni Foça, Eski Foça, Dikili, Çandarlı ve Bergama ilçelerine her saat ulaşım sağlanmaktadır.",
        "tags": ["ulaşım", "foça", "dikili", "bergama", "otobüs", "dolmuş"],
        "source_url": "https://www.aliaga.bel.tr/ulasim",
        "last_verified_at": date.today(),
    },
    # Ekonomi ve Sanayi
    {
        "layer": "ekonomi",
        "title": "Aliağa Ekonomisi ve Sanayi Bölgesi (ALOSBİ)",
        "neighborhood": "Sanayi Bölgesi",
        "summary": "Aliağa, Türkiye'nin en büyük petrokimya ve ağır sanayi merkezlerinden biridir. TÜPRAŞ İzmir Rafinerisi, PETKİM, STAR Rafineri ve çok sayıda demir-çelik fabrikası ile Türkiye ekonomisinde ihracat ve ithalatın kalbinin attığı devasa bir liman şehridir. ALOSBİ (Aliağa Organize Sanayi Bölgesi) büyük fabrikalara ev sahipliği yapar.",
        "tags": ["ekonomi", "sanayi", "petkim", "tüpraş", "rafineri", "demir çelik", "liman"],
        "source_url": "https://www.aliaga.bel.tr/ekonomi",
        "last_verified_at": date.today(),
    },
]
