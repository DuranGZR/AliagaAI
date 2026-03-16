# AliağaAI - Ürün Bağlamı

## 🧐 Hangi Problemi Çözüyoruz?

Günümüzde kullanıcılar, Aliağa gibi küçük yerleşim bölgelerine ait "spesifik ve anlık" bilgileri aramak için Google gibi genel amaçlı arama motorlarını kullanmaktadır. Ancak bu sistemler:
*   Küçük ilçelerin güncel yerel bilgilerini doğru indeksleyemeyebilir.
*   Arama sonuçları SEO odaklı, reklam dolu veya eski bilgiler barındırır.
*   "Nöbetçi eczane", "Aileyle gidilecek restoran" veya "Hafta sonu etkinlikleri" gibi *bağlam* gerektiren soruları doğru anlayamaz.

Sonuç olarak kullanıcılar, basit bir yerel bilgiye ulaşmak için onlarca site gezmek zorunda kalır.

## 💡 Çözüm: AliağaAI (Mobil Şehir Rehberi)

AliağaAI, kullanıcının niyetini anlayan, sadece **Aliağa'ya özel** filtreli ve temiz yerel veritabanını kullanan, doğrudan ve reklamsız yanıt veren hibrit bir akıllı şehir rehberidir. Mobil uygulama formatında tasarlandığı için kullanıcıya her an erişilebilir bir pratiklik sunar.

### Temel Prensipler
1.  **Yerellik:** Her şey Aliağa sınırları (ve gelecekte çevre ilçeler) içerisindedir.
2.  **Kararı AI Vermez:** AI uydurma (halüsinasyon) yapmaz. Sistemin arka planı (SQL + RAG) veriyi kesin ve net bir şekilde bulur; AI, sadece bu veriyi doğal bir insan dilinde, kullanıcıya hitap edecek şekilde paketleyip sunar.
3.  **Hız ve Pratiklik:** Kullanıcı soruyu sorar (yazarak veya sesle - mobil app), net cevabı ve mekanların/etkinliklerin temel bilgisini (harita, saatler vb.) anında alır.

## 📊 Veri Kaynakları ve Yönetimi

Uygulamanın gücü, içerdiği filtrelenmiş ve zenginleştirilmiş verilerden gelir. İki tür veri kaynağı kullanılmaktadır:

1.  **Otomatik Veriler (Scraping/API):**
    *   Belediye Duyuruları
    *   Haberler ve Etkinlikler
    *   Nöbetçi Eczaneler
    *   *(Bu veriler belirli periyotlarda otomatik olarak güncellenir)*
2.  **Manuel Veriler (Küratörlü):**
    *   Restoranlar ve Kafeler (Mekan özellikleri: sessiz, deniz kenarı, aileye uygun vb.)
    *   Turistik ve tarihi yerler.

**Yönetim Paneli (Admin Panel):**
Sistemin dinamik kalabilmesi için mekan ekleme, veri düzenleme, kategori yönetimi ve içerik güncelleme yapılabilen bir web tabanlı Admin Paneli mevcuttur.

## 🚀 Kullanıcı Deneyimi ve Gelecek Geliştirmeler

**MVP'de Sunulan Deneyim:**
*   Soru sorma alanı (Chat / Arama çubuğu).
*   Gelen direkt, anlaşılır yanıt.
*   Önerilen mekanların yapılandırılmış (kart) görünümü.

**Gelecek Geliştirmeler (Roadmap):**
*   **Konum Bazlı Öneriler:** Uygulamanın, cihazın konumunu kullanarak en yakındaki açık mekanları önermesi.
*   **Harita Entegrasyonu:** Sonuçların doğrudan uygulama içi bir haritada gösterilmesi.
*   **Kullanıcı Yorum Sistemi:** Mekanlara kullanıcı bazlı geri dönüşlerin (yorum, puan) eklenmesi.
*   **Farklı İlçelere Genişleme:** Altyapının "İlçemin Rehberi" modeliyle Menemen, Foça, Karşıyaka gibi bölgelere scale edilmesi.
