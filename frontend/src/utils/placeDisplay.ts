import { Place } from "../types";

export type PlaceDisplayCategory = "food" | "coast" | "park" | "history" | "culture" | "shopping" | "service" | "other";

export type PlaceDetailItem = Partial<Place> & {
  id?: number | string;
  name: string;
  category?: string | null;
  source_url?: string | null;
  source_label?: string | null;
};

const CATEGORY_LABELS: Record<PlaceDisplayCategory, string> = {
  food: "Yeme içme",
  coast: "Sahil",
  park: "Park",
  history: "Tarih",
  culture: "Kültür",
  shopping: "Alışveriş",
  service: "Hizmet",
  other: "Diğer",
};

const CATEGORY_IMAGES: Record<PlaceDisplayCategory, string[]> = {
  food: [
    "https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?auto=format&fit=crop&w=1200&q=80",
    "https://images.unsplash.com/photo-1555396273-367ea4eb4db5?auto=format&fit=crop&w=1200&q=80",
    "https://images.unsplash.com/photo-1544148103-0773bf10d330?auto=format&fit=crop&w=1200&q=80",
  ],
  coast: [
    "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=1200&q=80",
    "https://images.unsplash.com/photo-1519046904884-53103b34b206?auto=format&fit=crop&w=1200&q=80",
    "https://images.unsplash.com/photo-1473116763249-2faaef81ccda?auto=format&fit=crop&w=1200&q=80",
  ],
  park: [
    "https://images.unsplash.com/photo-1441974231531-c6227db76b6e?auto=format&fit=crop&w=1200&q=80",
    "https://images.unsplash.com/photo-1519331379826-f10be5486c6f?auto=format&fit=crop&w=1200&q=80",
    "https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?auto=format&fit=crop&w=1200&q=80",
  ],
  history: [
    "https://images.unsplash.com/photo-1539650116574-75c0c6d73f6e?auto=format&fit=crop&w=1200&q=80",
    "https://images.unsplash.com/photo-1530841377377-3ff06c0ca713?auto=format&fit=crop&w=1200&q=80",
    "https://images.unsplash.com/photo-1575408264798-b50b252663e6?auto=format&fit=crop&w=1200&q=80",
  ],
  culture: [
    "https://images.unsplash.com/photo-1524995997946-a1c2e315a42f?auto=format&fit=crop&w=1200&q=80",
    "https://images.unsplash.com/photo-1524230572899-a752b3835840?auto=format&fit=crop&w=1200&q=80",
    "https://images.unsplash.com/photo-1513475382585-d06e58bcb0e0?auto=format&fit=crop&w=1200&q=80",
  ],
  shopping: [
    "https://images.unsplash.com/photo-1472851294608-062f824d29cc?auto=format&fit=crop&w=1200&q=80",
    "https://images.unsplash.com/photo-1528698827591-e19ccd7bc23d?auto=format&fit=crop&w=1200&q=80",
  ],
  service: [
    "https://images.unsplash.com/photo-1497366754035-f200968a6e72?auto=format&fit=crop&w=1200&q=80",
    "https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?auto=format&fit=crop&w=1200&q=80",
  ],
  other: [
    "https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?auto=format&fit=crop&w=1200&q=80",
    "https://images.unsplash.com/photo-1497366811353-6870744d04b2?auto=format&fit=crop&w=1200&q=80",
  ],
};

export function normalizeText(value?: string | null): string {
  return (value || "")
    .toLocaleLowerCase("tr-TR")
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .replace(/ı/g, "i")
    .replace(/ğ/g, "g")
    .replace(/ş/g, "s")
    .replace(/ç/g, "c")
    .replace(/ö/g, "o")
    .replace(/ü/g, "u");
}

function stableIndex(seed: string, length: number): number {
  if (length <= 1) return 0;
  let hash = 0;
  for (let i = 0; i < seed.length; i += 1) {
    hash = (hash * 31 + seed.charCodeAt(i)) >>> 0;
  }
  return hash % length;
}

export function categoryOfPlace(place: Partial<PlaceDetailItem>): PlaceDisplayCategory {
  // Curated premium places inside Aliağa (IDs 10001 to 10021)
  if (place.id && typeof place.id === "number" && place.id >= 10001 && place.id <= 10021) {
    const sub = place.subcategory || "";
    if (sub === "plaj" || sub === "sahil" || sub === "koy") {
      return "coast";
    }
    if (sub === "doga_alani" || sub === "selale" || sub === "kent_parki" || sub === "sahil_parki" || sub === "çamlık") {
      return "park";
    }
    if (sub === "antik_kent" || sub === "tarihi_koy") {
      return "history";
    }
    if (place.category === "kultur" || sub === "sanat_evi" || sub === "kutuphane" || sub === "genclik_merkezi") {
      return "culture";
    }
  }

  const catSub = normalizeText(
    [place.name, place.category, place.subcategory, ...(place.tags || [])].join(" ")
  );
  const text = normalizeText(
    [
      place.name,
      place.category,
      place.subcategory,
      place.description,
      ...(place.tags || []),
    ].join(" ")
  );

  // --- Keşfet dışı: hastane, okul, kamu, berber, tesisat vb. ---
  const nonDiscoverKeywords = [
    "saglik", "hastane", "eczane", "klinik", "dis", "doktor",
    "egitim", "okul", "lise", "universite", "anaokul", "kreş",
    "kamu", "kaymakamlık", "nufus", "tapu", "vergi", "noter", "mahkeme", "jandarma", "polis", "postane",
    "banka", "atm",
    "berber", "kuafor", "tesisatci", "elektrikci", "cilingir", "tamirci", "lastikci", "oto_tamir", "oto_yikama",
    "veteriner", "nakliyat", "temizlik", "kargo",
    "kurum:saglik", "kurum:egitim", "kurum:kamu",
  ];
  if (nonDiscoverKeywords.some((kw) => catSub.includes(kw))) return "other";

  // --- Keşfedilebilir kategoriler ---
  if (text.includes("restoran") || text.includes("lokanta") || text.includes("kafe") || text.includes("cafe") || text.includes("bar") || text.includes("pub") || text.includes("fast_food") || text.includes("ocakbasi") || text.includes("yeme") || text.includes("ice_cream") || text.includes("dondurma") || text.includes("balik") || text.includes("pide") || text.includes("kebap")) return "food";
  if (text.includes("sahil") || text.includes("plaj") || text.includes("deniz") || text.includes("liman") || text.includes("koy") || text.includes("marina") || text.includes("beach")) return "coast";
  if (text.includes("park") || text.includes("mesire") || text.includes("yesil") || text.includes("piknik") || text.includes("playground") || text.includes("garden")) return "park";
  if (text.includes("antik") || text.includes("tarih") || text.includes("aigai") || text.includes("kyme") || text.includes("muze") || text.includes("gryneion") || text.includes("myrina") || text.includes("arkeoloji") || text.includes("historic") || text.includes("tapınak")) return "history";
  if (text.includes("sanat") || text.includes("kultur") || text.includes("kutuphane") || text.includes("kitaplik") || text.includes("tiyatro") || text.includes("sinema") || text.includes("muzik") || text.includes("galeri")) return "culture";
  if (text.includes("market") || text.includes("magaza") || text.includes("alisveris")) return "shopping";
  if (text.includes("otel") || text.includes("konaklama") || text.includes("hotel") || text.includes("motel") || text.includes("pansiyon")) return "culture";

  return "culture";
}

export function labelForPlaceCategory(category: PlaceDisplayCategory): string {
  return CATEGORY_LABELS[category];
}

export function imageForPlace(place: Partial<PlaceDetailItem>): string {
  if (place.image_url) return place.image_url;
  const category = categoryOfPlace(place);
  const pool = CATEGORY_IMAGES[category];
  return pool[stableIndex(`${place.id || ""}-${place.name || ""}`, pool.length)];
}

export function hasUsefulDescription(description?: string | null): boolean {
  const text = normalizeText(description);
  return Boolean(
    text &&
      text.length > 42 &&
      !text.includes("osm kaynak") &&
      !text.includes("kategori:") &&
      !text.includes("resmi/acik veri kaynaklari")
  );
}

export function descriptionForPlace(place: Partial<PlaceDetailItem>): string {
  if (hasUsefulDescription(place.description)) return place.description as string;

  const category = labelForPlaceCategory(categoryOfPlace(place));
  const address = place.address ? ` Adres bilgisi: ${place.address}.` : "";
  const phone = place.phone ? ` Telefon bilgisi kayitli.` : "";
  return `${place.name || "Bu nokta"}, Aliağa içinde ${category.toLocaleLowerCase("tr-TR")} kategorisinde listelenen bir kayıttır.${address}${phone}`;
}

export function tagsForPlace(place: Partial<PlaceDetailItem>): string[] {
  const category = labelForPlaceCategory(categoryOfPlace(place));
  const rawTags = Array.isArray(place.tags) ? place.tags.filter(Boolean) : [];
  return Array.from(new Set([category, ...(place.subcategory ? [place.subcategory] : []), ...rawTags])).slice(0, 5);
}

export function isPlaceUsefulForExplore(place: Place): boolean {
  if (!place.name) return false;
  const text = normalizeText([place.name, place.category, place.subcategory, ...(place.tags || [])].join(" "));
  if (text.includes("bilinmeyen")) return false;
  if (categoryOfPlace(place) === "other") return false;
  if (text.includes("diger") && !place.address && !place.phone) return false;
  return true;
}

/** Veritabanındaki ham kategori/subcategory bilgisini temiz Türkçe etikete çevirir. */
export function translateCategory(category?: string | null, subcategory?: string | null): string {
  const raw = normalizeText(category);
  const sub = normalizeText(subcategory);
  const combined = `${raw} ${sub}`;

  if (combined.includes("restoran") || combined.includes("lokanta") || combined.includes("fast_food")) return "Restoran";
  if (combined.includes("kafe") || combined.includes("cafe") || combined.includes("bar") || combined.includes("pub")) return "Kafe & Bar";
  if (combined.includes("sahil") || combined.includes("plaj") || combined.includes("beach")) return "Sahil";
  if (combined.includes("park") || combined.includes("mesire") || combined.includes("playground")) return "Park";
  if (combined.includes("antik") || combined.includes("tarih") || combined.includes("historic") || combined.includes("turistik")) return "Tarih & Turizm";
  if (combined.includes("kultur") || combined.includes("sanat")) return "Kültür";
  if (combined.includes("kutuphane") || combined.includes("kitaplik")) return "Kütüphane";
  if (combined.includes("saglik") || combined.includes("hastane") || combined.includes("eczane")) return "Sağlık";
  if (combined.includes("egitim") || combined.includes("okul") || combined.includes("lise")) return "Eğitim";
  if (combined.includes("kamu") || combined.includes("kurum")) return "Kamu Kurumu";
  if (combined.includes("spor") || combined.includes("fitness")) return "Spor";
  if (combined.includes("otel") || combined.includes("konaklama")) return "Konaklama";
  if (combined.includes("ulasim") || combined.includes("transport")) return "Ulaşım";
  if (combined.includes("market") || combined.includes("magaza") || combined.includes("alisveris")) return "Alışveriş";
  if (combined.includes("banka")) return "Banka";
  if (combined.includes("atm")) return "ATM";

  return category || "Diğer";
}
