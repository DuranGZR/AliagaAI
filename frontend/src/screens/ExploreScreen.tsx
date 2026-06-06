import React, { useCallback, useEffect, useMemo, useState } from "react";
import {
  ActivityIndicator,
  RefreshControl,
  ScrollView,
  StyleSheet,
  Text,
  TouchableOpacity,
  View,
} from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { LinearGradient } from "expo-linear-gradient";
import { Ionicons } from "@expo/vector-icons";
import { useNavigation } from "@react-navigation/native";

import { AppHeader } from "../components/AppHeader";
import { DataStatePanel } from "../components/DataStatePanel";
import { ExploreMap, MapRoute } from "../components/ExploreMap";
import { ReliableImage } from "../components/ReliableImage";
import { placeService, routeService } from "../services/api";
import { Place, Route } from "../types";
import { borderRadius, colors, spacing, typography } from "../theme";
import { DataState, loadDataState } from "../utils/dataState";
import { openExternalUrl } from "../utils/externalActions";

type IconName = keyof typeof Ionicons.glyphMap;
type ExploreFilter = "all" | "coast" | "history" | "culture" | "route";

const FILTERS: Array<{ key: ExploreFilter; label: string; icon: IconName }> = [
  { key: "all", label: "Tümü", icon: "sparkles-outline" },
  { key: "coast", label: "Doğa & Sahil", icon: "water-outline" },
  { key: "history", label: "Tarih", icon: "business-outline" },
  { key: "culture", label: "Kültür & Sanat", icon: "color-palette-outline" },
  { key: "route", label: "Rotalar", icon: "map-outline" },
];

const HERO_FALLBACK_IMAGE = "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=1200&q=80";

const CURATED_PLACES: Place[] = [
  {
    id: 10001,
    name: "Agapark Plajı ve Rekreasyon Alanı",
    category: "turistik",
    subcategory: "plaj",
    description: "Aliağa'nın göz bebeği olan Ağapark, mavi bayraklı geniş kumsalı, yemyeşil piknik alanları, spor sahaları, modern çocuk oyun parkları, bisiklet ve yürüyüş yolları ile şık sahil kafelerini bir arada sunan, ailenizle tam gün keyifle vakit geçirebileceğiniz 170 dönümlük devasa bir rekreasyon ve plaj kompleksidir.",
    address: "Yalı Mahallesi, Agapark Tesisleri, Aliağa",
    phone: "02326161980",
    rating: 4.8,
    tags: ["plaj", "sahil", "sosyal tesis", "agapark", "mavi bayrak"],
    latitude: 38.8250,
    longitude: 26.9650,
    image_url: "https://images.unsplash.com/photo-1506929562872-bb421503ef21?auto=format&fit=crop&w=800&q=80",
  },
  {
    id: 10002,
    name: "Kyme Antik Kenti",
    category: "turistik",
    subcategory: "antik_kent",
    description: "Çakmaklı köyü yakınlarında, Nemrut Körfezi kıyısında yer alan Kyme, antik dönemde Batı Anadolu'nun en büyük ve en güçlü 12 Aiolis kentinin başkentiydi. Ege deniz ticaretinin kalbinde yer alan ve kendi adına ilk gümüş sikkeyi basan bu zengin liman kenti, günümüze ulaşan sütunları ve taş kalıntılarıyla tarih meraklıları için büyüleyici bir açık hava müzesidir.",
    address: "Nemrut Körfezi Bölgesi, Aliağa",
    phone: null,
    rating: 4.5,
    tags: ["antik kent", "tarih", "arkeoloji", "kyme", "aiolis"],
    latitude: 38.7600,
    longitude: 26.9360,
    image_url: "https://images.unsplash.com/photo-1508849789987-4e5333c12b78?auto=format&fit=crop&w=800&q=80",
  },
  {
    id: 10003,
    name: "Aliağa Kuş Cenneti ve Güzelhisar Deltası",
    category: "turistik",
    subcategory: "doga_alani",
    description: "Güzelhisar Çayı'nın Ege Denizi ile birleştiği deltada yer alan bu koruma altındaki eşsiz sulak alan, göç yolları üzerinde hayati bir duraktır. Başta görkemli pembe flamingo sürüleri olmak üzere, pelikanlar, gri balıkçıllar ve 100'ü aşkın göçmen kuş türüne ev sahipliği yapar. Doğa fotoğrafçılığı ve kuş gözlemciliği için olağanüstü bir manzaraya sahiptir.",
    address: "Çaltılıdere Mahallesi, Aliağa",
    phone: null,
    rating: 4.7,
    tags: ["kuş cenneti", "flamingo", "doğa", "delta", "kuş gözlemi"],
    latitude: 38.8040,
    longitude: 26.9695,
    image_url: "https://images.unsplash.com/photo-1513836279014-a89f7a76ae86?auto=format&fit=crop&w=800&q=80",
  },
  {
    id: 10004,
    name: "Uçansu Şelalesi",
    category: "turistik",
    subcategory: "selale",
    description: "Karakuzu köyü yakınlarındaki derin ve yeşil bir vadide saklanan Uçansu (Suuçuran) Şelalesi, yaklaşık 30 metreden dökülen buz gibi sularıyla doğaseverleri karşılar. Özellikle ilkbahar aylarında gürleşen debisi, çevresindeki çam ormanı yolları ve huzurlu kamp/piknik alanlarıyla Aliağa'nın en önemli gizli doğa kaçış rotasıdır.",
    address: "Karakuzu Köyü, Şelale Mevkii, Aliağa",
    phone: null,
    rating: 4.9,
    tags: ["şelale", "doğa", "kamp", "karakuzu", "şelale"],
    latitude: 38.7408,
    longitude: 27.1679,
    image_url: "https://images.unsplash.com/photo-1455218873509-8097305ee378?auto=format&fit=crop&w=800&q=80",
  },
  {
    id: 10005,
    name: "Gryneion Antik Kenti",
    category: "turistik",
    subcategory: "antik_kent",
    description: "Yeni Şakran sahilinde bir yarımada üzerinde bulunan Gryneion, antik dünyada kehanetleri ve geleceği öngören Apollon Tapınağı ile ün salmış kutsal bir liman şehriydi. Günümüze ulaşan rıhtım kalıntıları, tapınak temelleri ve denize uzanan tarihi izleriyle hem tarih meraklıları hem de gün batımı izlemek isteyenler için harika bir yerdir.",
    address: "Yeni Şakran Mahallesi, Sahil Mevkii, Aliağa",
    phone: null,
    rating: 4.3,
    tags: ["antik kent", "tarih", "apollon tapınağı", "gryneion", "kehanet"],
    latitude: 38.8744,
    longitude: 27.0692,
    image_url: "https://images.unsplash.com/photo-1505118380757-91f5f5632de0?auto=format&fit=crop&w=800&q=80",
  },
  {
    id: 10006,
    name: "Myrina Antik Kenti",
    category: "turistik",
    subcategory: "antik_kent",
    description: "Güzelhisar Çayı'nın (antik Pythikos) denize döküldüğü tepelerde kurulu olan Myrina, antik dönemde pişmiş topraktan yapılmış sanatsal heykelcikleri (terrakotta) ile Akdeniz dünyasında büyük bir üne sahipti. Antik tiyatro kalıntıları, liman rıhtımı ve çay yatağı boyunca yayılan tarihi surları ile Aiolis birliğinin en hareketli limanlarından biriydi.",
    address: "Çaltılıdere Mahallesi, Kalabak Çayı Mevkii, Aliağa",
    phone: null,
    rating: 4.2,
    tags: ["antik kent", "tarih", "arkeoloji", "myrina", "terrakotta"],
    latitude: 38.8453,
    longitude: 26.9844,
    image_url: "https://images.unsplash.com/photo-1533105079780-92b9be482077?auto=format&fit=crop&w=800&q=80",
  },
  {
    id: 10007,
    name: "Güzelhisar Köyü Taş Evleri ve Mesire Alanı",
    category: "turistik",
    subcategory: "tarihi_koy",
    description: "Aliağa'nın en köklü ve tarihi yerleşimlerinden olan Güzelhisar, Osmanlı ve Bizans izlerini taşıyan kale surları, dar sokakları süsleyen asırlık taş evleri ve köy meydanındaki dev çınar ağaçları ile yaşayan bir kültür mirasıdır. Köyün hemen yanındaki gölgelik mesire alanları ve geleneksel köy kahvesi keyifli bir dinlenme durağı sunar.",
    address: "Güzelhisar Köyü, Aliağa",
    phone: null,
    rating: 4.6,
    tags: ["tarihi köy", "taş evler", "kültür", "güzelhisar", "mesire alanı"],
    latitude: 38.7762,
    longitude: 27.0177,
    image_url: "https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?auto=format&fit=crop&w=800&q=80",
  },
  {
    id: 10008,
    name: "Aliağa Kent Parkı",
    category: "turistik",
    subcategory: "kent_parki",
    description: "Yeni Mahalle'de yer alan 110 bin metrekarelik bu devasa rekreasyon parkı, Aliağa'nın akciğeri konumundadır. Modern ışıklı süs havuzları, bisiklet ve koşu parkurları, mini futbol/basketbol sahaları, çocuk oyun kompleksleri ve geniş çim alanlarıyla modern kent yaşamında dinlenmek ve spor yapmak isteyenlerin ana buluşma noktasıdır.",
    address: "Kültür Mahallesi, Fevzi Paşa Caddesi, Aliağa",
    phone: null,
    rating: 4.8,
    tags: ["kent parkı", "yeşil alan", "spor", "yürüyüş yolu", "rekreasyon"],
    latitude: 38.7908,
    longitude: 26.9759,
    image_url: "https://images.unsplash.com/photo-1502082553048-f009c37129b9?auto=format&fit=crop&w=800&q=80",
  },
  {
    id: 10009,
    name: "Avcı Ramadan Çocuk Oyun ve Rekreasyon Alanı",
    category: "turistik",
    subcategory: "sahil_parki",
    description: "Yalı Mahallesi sahil şeridinde denize sıfır konumda uzanan Avcı Ramadan Parkı, modern çocuk oyun alanları, geniş piknik çimleri, amfitiyatrosu, bisiklet yolları ve sahil kafeleriyle gün boyu esen tatlı deniz meltemi eşliğinde dinlenmek, denizi seyretmek ve ailenizle yürüyüş yapmak için harika bir sahil parkıdır.",
    address: "Yalı Mahallesi, Sahil Şeridi, Aliağa",
    phone: null,
    rating: 4.7,
    tags: ["sahil parkı", "yürüyüş", "çocuk parkı", "avcı ramadan", "deniz manzarası"],
    latitude: 38.8043,
    longitude: 26.9662,
    image_url: "https://images.unsplash.com/photo-1473116763249-2faaef81ccda?auto=format&fit=crop&w=800&q=80",
  },
  {
    id: 10010,
    name: "Yeni Şakran Sahili ve Plajı",
    category: "turistik",
    subcategory: "sahil",
    description: "İlçe merkezinin kuzeyinde yer alan Yeni Şakran, kilometrelerce uzanan kumsalı, tertemiz denizi, palmiyelerle süslü modern kordon boyu ve taze Ege balıkları sunan sahil restoranlarıyla yaz aylarının vazgeçilmez tatil beldesidir. Akşamüstü gün batımı yürüyüşleri için eşsiz bir atmosfere sahiptir.",
    address: "Yeni Şakran Mahallesi, Sahil Yolu, Aliağa",
    phone: null,
    rating: 4.6,
    tags: ["sahil", "plaj", "yeni şakran", "kumsal", "yürüyüş yolu"],
    latitude: 38.8870,
    longitude: 27.0600,
    image_url: "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=800&q=80",
  },
  {
    id: 10011,
    name: "Köstem Koyu",
    category: "turistik",
    subcategory: "koy",
    description: "Çaltılıdere sınırlarında, kalabalıklardan uzaklaşmak ve doğa ile baş başa kalmak isteyenler için adeta saklı bir cennettir. Turkuaz renkli berrak denizi, rüzgardan korunan doğal körfez yapısı ve çam ağaçlarının denize kadar uzandığı sakin atmosferiyle denize girmek ve kamp yapmak için mükemmeldir.",
    address: "Köstem Mevkii, Yeni Şakran, Aliağa",
    phone: null,
    rating: 4.5,
    tags: ["koy", "doğal plaj", "sakin", "köstem koyu", "deniz"],
    latitude: 38.8589,
    longitude: 27.0088,
    image_url: "https://images.unsplash.com/photo-1501785888041-af3ef285b470?auto=format&fit=crop&w=800&q=80",
  },
  {
    id: 10012,
    name: "Aliağa Çamlık Rekreasyon Alanı",
    category: "turistik",
    subcategory: "çamlık",
    description: "Aliağa şehir merkezine hakim bir tepe üzerinde yer alan bu çam ormanı, şehirden uzaklaşmadan doğayla kucaklaşma imkanı sunar. Bol oksijenli çam havası, piknik masaları, çocuk parkları ve tüm Aliağa Körfezi ile sanayi limanlarını panoramik olarak izleyebileceğiniz muhteşem seyir terasıyla ünlüdür.",
    address: "Atatürk Mahallesi, Çamlık Yolu, Aliağa",
    phone: null,
    rating: 4.6,
    tags: ["çamlık", "piknik alanı", "orman", "seyir terası", "manzara"],
    latitude: 38.7998,
    longitude: 26.9790,
    image_url: "https://images.unsplash.com/photo-1473448912268-2022ce9509d8?auto=format&fit=crop&w=800&q=80",
  },
  {
    id: 10013,
    name: "Karakuzu Köyü ve Doğa Vadisi",
    category: "turistik",
    subcategory: "doga_alani",
    description: "Aliağa'nın doğusundaki dağlık bölgede kurulu Karakuzu köyü, zeytinlikler ve çam ormanlarıyla kaplı yeşil vadisiyle ünlüdür. Temiz dağ havası, geleneksel köy yaşantısı, yürüyüş ve dağ bisikleti parkurları ile doğa tutkunlarının, fotoğrafçıların ve kampçıların her mevsim uğrak yeridir.",
    address: "Karakuzu Köyü, Aliağa",
    phone: null,
    rating: 4.7,
    tags: ["doğa", "köy", "trekking", "karakuzu", "kamp"],
    latitude: 38.7610,
    longitude: 27.1080,
    image_url: "https://images.unsplash.com/photo-1506744038136-46273834b3fb?auto=format&fit=crop&w=800&q=80",
  },
  {
    id: 10014,
    name: "Aliağa Sanat Evi (ASEM)",
    category: "kultur",
    subcategory: "sanat_evi",
    description: "Aliağa'nın sanatsal ve kültürel kalbi olan ASEM; resimden müziğe, tiyatrodan el sanatlarına kadar geniş yelpazede eğitimler ve atölyeler sunar. Periyodik sergiler, tiyatro oyunları ve kültürel etkinliklerle ilçe sakinlerini sanatla buluşturan modern bir sanat merkezidir.",
    address: "Kültür Mahallesi, İstiklal Caddesi, Aliağa",
    phone: null,
    rating: 4.5,
    tags: ["sanat evi", "kültür", "sergi", "tiyatro", "eğitim"],
    latitude: 38.7985,
    longitude: 26.9715,
    image_url: "https://images.unsplash.com/photo-1513364776144-60967b0f800f?auto=format&fit=crop&w=800&q=80",
  },
  {
    id: 10015,
    name: "Aliağa Kent Kitaplığı ve Kent Arşivi",
    category: "kultur",
    subcategory: "kutuphane",
    description: "Aliağa'nın tarihi, arkeolojisi ve sosyal geçmişine dair binlerce eserin yer aldığı arşiv ve çalışma kütüphanesidir. Antik Kyme ve Aigai kazı raporları ve yerel belgelerle kent belleğini korurken, modern ve sessiz çalışma salonlarıyla öğrencilerin ve araştırmacıların odak noktasıdır.",
    address: "Kültür Mahallesi, Hükümet Konağı Arkası, Aliağa",
    phone: null,
    rating: 4.7,
    tags: ["kütüphane", "arşiv", "kitaplık", "kültür", "çalışma alanı"],
    latitude: 38.7985,
    longitude: 26.9658,
    image_url: "https://images.unsplash.com/photo-1507842217343-583bb7270b66?auto=format&fit=crop&w=800&q=80",
  },
  {
    id: 10016,
    name: "Aliağa Gençlik Merkezi",
    category: "kultur",
    subcategory: "genclik_merkezi",
    description: "Gençlerin ihtiyaçlarına göre tasarlanmış bu devasa kompleks; en son teknoloji sinema salonları, yarı olimpik kapalı yüzme havuzu, tam donanımlı fitness merkezi, dans/spor salonları, kütüphanesi ve sosyal kafeleriyle Aliağa gençliğinin spor, eğitim ve eğlenceyi bir arada bulduğu en popüler sosyal merkezdir.",
    address: "Fatih Mahallesi, Atatürk Caddesi No:42, Aliağa",
    phone: "02326162530",
    rating: 4.8,
    tags: ["gençlik merkezi", "havuz", "sinema", "spor", "yaşam merkezi"],
    latitude: 38.8028,
    longitude: 26.9665,
    image_url: "https://images.unsplash.com/photo-1517838277536-f5f99be501cd?auto=format&fit=crop&w=800&q=80",
  },
  {
    id: 10017,
    name: "Karanlık Koy (Tavşan Adası Karşısı)",
    category: "turistik",
    subcategory: "koy",
    description: "Yeni Şakran'ın hemen kuzeyinde, Tavşan Adası'nın tam karşısında yer alan Karanlık Koy, korunaklı yapısı sayesinde daima dalgasız, havuz berraklığındaki deniziyle bilinir. Doğallığını kaybetmemiş plajıyla çadır kampı kurmak, dalış yapmak ve zıpkınla balık avlamak isteyenlerin vazgeçilmez bakir koydur.",
    address: "Yeni Şakran Mevkii, Tavşan Adası Karşısı, Aliağa",
    phone: null,
    rating: 4.6,
    tags: ["koy", "kamp", "sakin", "deniz", "tavşan adası"],
    latitude: 38.8950,
    longitude: 27.0500,
    image_url: "https://images.unsplash.com/photo-1537905569824-f89f14cceb68?auto=format&fit=crop&w=800&q=80",
  },
  {
    id: 10018,
    name: "Plajlar Bölgesi (Ön Plajlar)",
    category: "turistik",
    subcategory: "plaj",
    description: "Aliağa şehir merkezine en yakın konumda, Yalı Mahallesi boyunca uzanan Ön Plajlar, sığ ve dalgasız deniziyle çocuklu aileler için son derece güvenlidir. Kumsalının hemen gerisindeki palmiyeli yürüyüş yolları, kafeteryaları ve geniş yeşil park alanlarıyla yaz günlerinde deniz keyfinin, akşamları ise sahil yürüyüşlerinin kalbidir.",
    address: "Yalı Mahallesi, Plaj Caddesi, Aliağa",
    phone: null,
    rating: 4.5,
    tags: ["plaj", "sahil", "yürüyüş yolu", "halk plajı", "aliağa merkez"],
    latitude: 38.8315,
    longitude: 26.9697,
    image_url: "https://images.unsplash.com/photo-1519046904884-53103b34b206?auto=format&fit=crop&w=800&q=80",
  },
  {
    id: 10019,
    name: "Şakran Bölgeler Parkı",
    category: "turistik",
    subcategory: "kent_parki",
    description: "Yeni Şakran girişinde yer alan bu geniş park; yemyeşil bakımlı çimleri, rengarenk çiçekleri, açık hava spor alanları, güvenli çocuk oyun parkurları ve yürüyüş yollayla Şakran sakinlerinin akşamüstü çaylarını içip sohbet ettiği, çocukların güvenle oynadığı en büyük mahalle parkı ve yeşil rekreasyon alanıdır.",
    address: "Yeni Şakran Mahallesi, Giriş Parkı, Aliağa",
    phone: null,
    rating: 4.6,
    tags: ["park", "rekreasyon", "yeni şakran", "yeşil alan", "çocuk parkı"],
    latitude: 38.8817,
    image_url: "https://images.unsplash.com/photo-1541432901042-2d8bd64b4a9b?auto=format&fit=crop&w=800&q=80",
  },
  {
    id: 10020,
    name: "Aigai Antik Kenti",
    category: "turistik",
    subcategory: "antik_kent",
    description: "Aiolis bölgesinin en görkemli dağ kentlerinden biri olan Aigai, yüksek kayalıklar üzerine kurulmuş sarsılmaz surları ve eşsiz bir mühendislik harikası olan devasa üç katlı agorasıyla büyüleyicidir. Binlerce yıl öncesine ait tiyatro ve Bouleuterion kalıntıları arasında yürürken, sadece tarihin değil, bölgenin uçsuz bucaksız vadilerine açılan muhteşem manzaranın da tadını çıkaracaksınız.",
    address: "Köseler Köyü Mevkii, Aliağa Sınırı Yakını",
    phone: null,
    rating: 4.8,
    tags: ["antik kent", "tarih", "arkeoloji", "aigai", "yuntdağı"],
    latitude: 38.8338,
    longitude: 27.1934,
    image_url: "https://images.unsplash.com/photo-1524492412937-b28074a5d7da?auto=format&fit=crop&w=800&q=80",
  },
  {
    id: 10021,
    name: "Güzelhisar Baraj Gölü Seyir Tepesi",
    category: "turistik",
    subcategory: "doga_alani",
    description: "Aliağa Güzelhisar Barajı'na yukarıdan bakan, çam ormanlarıyla kaplı yüksek bir manzara noktasıdır. Kuşbakışı göl görünümü, serin çam havası ve huzurlu sessizliğiyle doğa fotoğrafçıları ve kampçıların favori duraklarındandır.",
    address: "Güzelhisar Baraj Yolu, Aliağa",
    phone: null,
    rating: 4.7,
    tags: ["manzara", "baraj", "doğa", "seyir tepesi", "güzelhisar"],
    latitude: 38.7953,
    longitude: 27.1206,
    image_url: "https://images.unsplash.com/photo-1504280390367-361c6d9f38f4?auto=format&fit=crop&w=800&q=80",
  }
];

function routeToDetailParams(route: Route) {
  return {
    id: String(route.id),
    name: route.title,
    category: route.eyebrow,
    address: "Aliağa",
    description: route.description,
    rating: null,
    tags: route.tags || [],
    image_url: route.image_url || undefined,
  };
}

const AUTO_REFRESH_MS = 10 * 60 * 1000;

const FALLBACK_IMAGES: Record<Exclude<ExploreFilter, "all" | "events" | "route">, string[]> = {
  coast: [
    "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=1000&q=80",
    "https://images.unsplash.com/photo-1519046904884-53103b34b206?auto=format&fit=crop&w=1000&q=80",
    "https://images.unsplash.com/photo-1473116763249-2faaef81ccda?auto=format&fit=crop&w=1000&q=80",
  ],
  history: [
    "https://images.unsplash.com/photo-1530841377377-3ff06c0ca713?auto=format&fit=crop&w=1000&q=80",
    "https://images.unsplash.com/photo-1539650116574-75c0c6d73f6e?auto=format&fit=crop&w=1000&q=80",
    "https://images.unsplash.com/photo-1575408264798-b50b252663e6?auto=format&fit=crop&w=1000&q=80",
  ],
  culture: [
    "https://images.unsplash.com/photo-1524230572899-a752b3835840?auto=format&fit=crop&w=1000&q=80",
    "https://images.unsplash.com/photo-1524995997946-a1c2e315a42f?auto=format&fit=crop&w=1000&q=80",
    "https://images.unsplash.com/photo-1513475382585-d06e58bcb0e0?auto=format&fit=crop&w=1000&q=80",
  ],
};

function normalizeText(value?: string | null): string {
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

function relativeDate(input?: string | null): string {
  if (!input) return "Tarih bekleniyor";
  const date = new Date(input);
  if (!Number.isFinite(date.getTime())) return "Tarih bekleniyor";
  return date.toLocaleDateString("tr-TR", {
    day: "2-digit",
    month: "short",
    weekday: "short",
  });
}

function categoryOfPlace(place: Place): Exclude<ExploreFilter, "all" | "events" | "route"> | "other" {
  if (place.id && typeof place.id === "number" && place.id >= 10001 && place.id <= 10021) {
    const sub = place.subcategory || "";
    if (sub === "plaj" || sub === "sahil" || sub === "koy" || sub === "doga_alani" || sub === "selale" || sub === "kent_parki" || sub === "sahil_parki" || sub === "çamlık") {
      return "coast";
    }
    if (sub === "antik_kent" || sub === "tarihi_koy") {
      return "history";
    }
    if (place.category === "kultur" || sub === "sanat_evi" || sub === "kutuphane" || sub === "genclik_merkezi") {
      return "culture";
    }
  }
  return "other";
}

function labelForFilter(key: ExploreFilter): string {
  return FILTERS.find((item) => item.key === key)?.label || "Keşif";
}

function stableImageIndex(seed: string, length: number): number {
  if (length <= 1) return 0;
  let hash = 0;
  for (let index = 0; index < seed.length; index += 1) {
    hash = (hash * 31 + seed.charCodeAt(index)) >>> 0;
  }
  return hash % length;
}

function imageForPlace(place: Place): string {
  return place.image_url || fallbackImageForPlace(place);
}

function fallbackImageForPlace(place: Place): string {
  const key = categoryOfPlace(place);
  const pool = FALLBACK_IMAGES[key as keyof typeof FALLBACK_IMAGES] || FALLBACK_IMAGES.culture;
  return pool[stableImageIndex(`${place.id}-${place.name}`, pool.length)];
}

function isDiscoverablePlace(place: Place): boolean {
  return place.id >= 10001 && place.id <= 10021;
}

function getDistance(lat1: number, lon1: number, lat2: number, lon2: number): number {
  const R = 6371; // km
  const dLat = (lat2 - lat1) * Math.PI / 180;
  const dLon = (lon2 - lon1) * Math.PI / 180;
  const a =
    Math.sin(dLat / 2) * Math.sin(dLat / 2) +
    Math.cos(lat1 * Math.PI / 180) *
      Math.cos(lat2 * Math.PI / 180) *
      Math.sin(dLon / 2) *
      Math.sin(dLon / 2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  return R * c;
}

function placeToDetailParams(place: Place) {
  return {
    ...place,
    image_url: imageForPlace(place),
    tags: place.tags || [labelForFilter((categoryOfPlace(place) as ExploreFilter) || "all")],
  };
}

export function ExploreScreen() {
  const navigation = useNavigation<any>();
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [places, setPlaces] = useState<Place[]>([]);
  const [routes, setRoutes] = useState<Route[]>([]);
  const [selectedFilter, setSelectedFilter] = useState<ExploreFilter>("all");
  const [selectedRouteId, setSelectedRouteId] = useState<string | null>(null);
  const [userCoords, setUserCoords] = useState<{ latitude: number; longitude: number } | null>(null);

  useEffect(() => {
    if (typeof navigator !== "undefined" && navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (pos) => {
          setUserCoords({
            latitude: pos.coords.latitude,
            longitude: pos.coords.longitude,
          });
        },
        () => {},
        { enableHighAccuracy: true, timeout: 8000 }
      );
    }
  }, []);

  const load = useCallback(async (isRefresh = false) => {
    if (isRefresh) {
      setRefreshing(true);
    } else {
      setLoading(true);
    }

    try {
      const [placeRows, routeRows] = await Promise.all([
        loadDataState(() => placeService.getAll(undefined, 500), [] as Place[]),
        loadDataState(() => routeService.getAll(), [] as Route[]),
      ]);
      
      const backendData = placeRows.data || [];
      const combined = [...CURATED_PLACES];
      const seenNames = new Set(CURATED_PLACES.map((p) => p.name.toLowerCase()));
      for (const p of backendData) {
        if (!seenNames.has(p.name.toLowerCase())) {
          seenNames.add(p.name.toLowerCase());
          combined.push(p);
        }
      }
      setPlaces(combined);
      setRoutes(routeRows.data || []);
      if (routeRows.data && routeRows.data.length > 0) {
        setSelectedRouteId(String(routeRows.data[0].id));
      }
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, []);

  useEffect(() => {
    void load();
    const timer = setInterval(() => void load(true), AUTO_REFRESH_MS);
    return () => clearInterval(timer);
  }, [load]);

  const explorePlaces = useMemo(() => {
    let list = [...places].filter(isDiscoverablePlace);
    if (userCoords) {
      return list.sort((a, b) => {
        if (a.latitude && a.longitude && b.latitude && b.longitude) {
          const distA = getDistance(userCoords.latitude, userCoords.longitude, a.latitude, a.longitude);
          const distB = getDistance(userCoords.latitude, userCoords.longitude, b.latitude, b.longitude);
          return distA - distB;
        }
        return 0;
      });
    }
    return list.sort((a, b) => a.name.localeCompare(b.name, "tr-TR"));
  }, [places, userCoords]);

  const selectedPlaces = useMemo(() => {
    if (selectedFilter === "all") return explorePlaces;
    if (selectedFilter === "route") return [];
    return explorePlaces.filter((place) => categoryOfPlace(place) === selectedFilter);
  }, [explorePlaces, selectedFilter]);

  const naturePlaces = useMemo(
    () => explorePlaces.filter((p) => {
      const sub = p.subcategory || "";
      return sub === "plaj" || sub === "sahil" || sub === "koy" || sub === "doga_alani" || sub === "selale" || sub === "kent_parki" || sub === "sahil_parki" || sub === "çamlık";
    }).slice(0, 12),
    [explorePlaces]
  );

  const cultureAndHistoryPlaces = useMemo(
    () => explorePlaces.filter((p) => {
      const sub = p.subcategory || "";
      const cat = p.category || "";
      return sub === "antik_kent" || sub === "tarihi_koy" || cat === "kultur" || sub === "sanat_evi" || sub === "kutuphane" || sub === "genclik_merkezi";
    }).slice(0, 12),
    [explorePlaces]
  );

  const spotlightPlaces = useMemo(() => {
    if (selectedFilter === "route") return [];
    return (selectedPlaces.length > 0 ? selectedPlaces : explorePlaces).slice(0, 16);
  }, [selectedPlaces, explorePlaces, selectedFilter]);

  const mapRoutes: MapRoute[] = useMemo(
    () =>
      routes.map((r) => ({
        id: String(r.id),
        title: r.title,
        icon: r.icon || "map-outline",
        duration: r.duration || "2-3 saat",
        coordinates: (r.stops || []).map((s) => ({ latitude: s.latitude, longitude: s.longitude })),
      })),
    [routes]
  );

  return (
    <View style={styles.container}>
      <SafeAreaView style={styles.safeArea} edges={["top"]}>
        <AppHeader />

        {loading ? (
          <View style={styles.loadingWrap}>
            <ActivityIndicator size="large" color={colors.primary} />
          </View>
        ) : (
          <ScrollView
            contentContainerStyle={styles.scrollContent}
            showsVerticalScrollIndicator={false}
            refreshControl={
              <RefreshControl
                refreshing={refreshing}
                onRefresh={() => void load(true)}
                tintColor={colors.primary}
                colors={[colors.primary]}
              />
            }
          >
            <View style={styles.introRow}>
              <View style={styles.introCopy}>
                <Text style={styles.pageTitle}>Keşfet</Text>
                <Text style={styles.pageSubtitle}>Rota, mekan ve kültür önerileri.</Text>
              </View>
              <View style={styles.livePill}>
                <Ionicons name="sparkles-outline" size={14} color={colors.primary} />
                <Text style={styles.livePillText}>Canlı</Text>
              </View>
            </View>

            <ExploreMap
              places={explorePlaces}
              selectedFilter={selectedFilter}
              routes={mapRoutes}
              activeRouteId={selectedRouteId}
            />

            <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={styles.filterRow}>
              {FILTERS.map((filter) => {
                const active = selectedFilter === filter.key;
                return (
                  <TouchableOpacity
                    key={filter.key}
                    style={[styles.filterChip, active && styles.filterChipActive]}
                    onPress={() => setSelectedFilter(filter.key)}
                  >
                    <Ionicons name={filter.icon} size={14} color={active ? colors.primary : colors.textSecondary} />
                    <Text style={[styles.filterText, active && styles.filterTextActive]}>{filter.label}</Text>
                  </TouchableOpacity>
                );
              })}
            </ScrollView>

            {selectedFilter === "route" ? (
              <RouteRail
                navigation={navigation}
                routes={routes}
                selectedRouteId={selectedRouteId}
                onSelectRoute={setSelectedRouteId}
              />
            ) : (
              <Section title={selectedFilter === "all" ? "ÖNE ÇIKAN KEŞİFLER" : labelForFilter(selectedFilter).toUpperCase()} action={`${spotlightPlaces.length} öneri`}>
                {spotlightPlaces.length === 0 ? (
                  <EmptyPanel title="Kayıt bekleniyor" text="Bu kategori için mekan verisi geldiğinde kartlar dolacak." />
                ) : (
                  <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={styles.placeRow}>
                    {spotlightPlaces.map((place) => (
                      <PlaceCard key={place.id} place={place} userCoords={userCoords} onPress={() => navigation.navigate("PlaceDetail", placeToDetailParams(place))} />
                    ))}
                  </ScrollView>
                )}
              </Section>
            )}

            {selectedFilter !== "route" && routes.length > 0 && (
              <RouteRail navigation={navigation} routes={routes} />
            )}

            <Section title="DOĞA VE SAHİL" action={`${naturePlaces.length} nokta`}>
              <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={styles.compactRow}>
                {naturePlaces.map((place) => (
                  <CompactPlaceCard key={place.id} place={place} userCoords={userCoords} onPress={() => navigation.navigate("PlaceDetail", placeToDetailParams(place))} />
                ))}
              </ScrollView>
            </Section>

            <Section title="TARİH VE KÜLTÜR" action={`${cultureAndHistoryPlaces.length} öneri`}>
              <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={styles.compactRow}>
                {cultureAndHistoryPlaces.map((place) => (
                  <CompactPlaceCard key={place.id} place={place} userCoords={userCoords} onPress={() => navigation.navigate("PlaceDetail", placeToDetailParams(place))} />
                ))}
              </ScrollView>
            </Section>
          </ScrollView>
        )}
      </SafeAreaView>
    </View>
  );
}

function Section({
  title,
  action,
  children,
}: {
  title: string;
  action?: string;
  children: React.ReactNode;
}) {
  return (
    <View style={styles.section}>
      <View style={styles.sectionHeader}>
        <Text style={styles.sectionTitle}>{title}</Text>
        {action ? <Text style={styles.sectionAction}>{action}</Text> : null}
      </View>
      {children}
    </View>
  );
}

function PlaceCard({
  place,
  onPress,
  userCoords,
}: {
  place: Place;
  onPress: () => void;
  userCoords?: { latitude: number; longitude: number } | null;
}) {
  const key = categoryOfPlace(place);
  const distance = useMemo(() => {
    if (userCoords && place.latitude && place.longitude) {
      return getDistance(userCoords.latitude, userCoords.longitude, place.latitude, place.longitude);
    }
    return null;
  }, [userCoords, place.latitude, place.longitude]);

  return (
    <TouchableOpacity style={styles.placeCard} activeOpacity={0.9} onPress={onPress}>
      <ReliableImage
        uri={place.image_url || undefined}
        fallbackUri={fallbackImageForPlace(place)}
        style={styles.placeImage}
        resizeMode="cover"
        label="Mekan görseli"
      />
      <LinearGradient colors={["rgba(0,0,0,0)", "rgba(0,0,0,0.45)", "rgba(0,0,0,0.95)"]} style={styles.placeOverlay} />
      <View style={styles.placeTag}>
        <Text style={styles.placeTagText}>{labelForFilter(key as ExploreFilter).toUpperCase()}</Text>
      </View>
      <View style={styles.placeContent}>
        <Text style={styles.placeCategory}>
          {distance ? `📍 ${distance.toFixed(1)} km uzaklıkta · ` : ""}
          {place.subcategory || labelForFilter(key as ExploreFilter)}
        </Text>
        <Text style={styles.placeTitle} numberOfLines={2}>{place.name}</Text>
        <Text style={styles.placeDesc} numberOfLines={3}>{place.description || place.address || "Aliağa"}</Text>
        <Text style={styles.placeMeta} numberOfLines={1}>{place.address || "Aliağa"}</Text>
      </View>
    </TouchableOpacity>
  );
}

function CompactPlaceCard({
  place,
  onPress,
  userCoords,
}: {
  place: Place;
  onPress: () => void;
  userCoords?: { latitude: number; longitude: number } | null;
}) {
  const key = categoryOfPlace(place);
  const distance = useMemo(() => {
    if (userCoords && place.latitude && place.longitude) {
      return getDistance(userCoords.latitude, userCoords.longitude, place.latitude, place.longitude);
    }
    return null;
  }, [userCoords, place.latitude, place.longitude]);

  return (
    <TouchableOpacity style={styles.compactCard} activeOpacity={0.88} onPress={onPress}>
      <ReliableImage
        uri={place.image_url || undefined}
        fallbackUri={fallbackImageForPlace(place)}
        style={styles.compactImage}
        resizeMode="cover"
        label="Mekan"
      />
      <View style={styles.compactBody}>
        <Text style={styles.cardEyebrow}>
          {labelForFilter(key as ExploreFilter)}
          {distance ? ` · 📍 ${distance.toFixed(1)} km` : ""}
        </Text>
        <Text style={styles.compactTitle} numberOfLines={2}>{place.name}</Text>
        <Text style={styles.compactMeta} numberOfLines={2}>{place.description || place.address || place.category || "Aliağa"}</Text>
      </View>
    </TouchableOpacity>
  );
}

function RouteRail({
  navigation,
  routes,
  selectedRouteId,
  onSelectRoute,
}: {
  navigation: any;
  routes: Route[];
  selectedRouteId?: string | null;
  onSelectRoute?: (id: string) => void;
}) {
  const isSelectMode = Boolean(onSelectRoute);
  const actionLabel = isSelectMode ? "Seç / Detay için tekrar dokun" : "Plan hazır";

  return (
    <Section title="ROTA ÖNERİLERİ" action={actionLabel}>
      <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={styles.routeRow}>
        {routes.map((route) => {
          const isSelected = selectedRouteId === String(route.id);
          return (
            <TouchableOpacity
              key={route.id}
              style={[
                styles.routeCard,
                isSelected && { borderColor: colors.primary, borderWidth: 2 },
              ]}
              activeOpacity={0.9}
              onPress={() => {
                if (isSelectMode && onSelectRoute) {
                  if (isSelected) {
                    navigation.navigate("PlaceDetail", routeToDetailParams(route));
                  } else {
                    onSelectRoute(String(route.id));
                  }
                } else {
                  navigation.navigate("PlaceDetail", routeToDetailParams(route));
                }
              }}
            >
              <ReliableImage
                uri={route.image_url || undefined}
                fallbackUri={HERO_FALLBACK_IMAGE}
                style={styles.routeImage}
                resizeMode="cover"
                label="Rota"
              />
              <LinearGradient colors={["rgba(0,0,0,0)", "rgba(0,0,0,0.45)", "rgba(0,0,0,0.95)"]} style={styles.routeOverlay} />
              <View style={styles.routeContent}>
                <View style={styles.routeBadge}>
                  <Ionicons name={(route.icon || "map-outline") as any} size={14} color={colors.primary} />
                  <Text style={styles.routeBadgeText}>{route.duration || "2-3 saat"}</Text>
                </View>
                <Text style={styles.routeEyebrow}>{route.eyebrow || "Keşif Rotaları"}</Text>
                <Text style={styles.routeTitle} numberOfLines={2}>{route.title}</Text>
                <Text style={styles.routeDesc} numberOfLines={2}>{route.description}</Text>
              </View>
            </TouchableOpacity>
          );
        })}
      </ScrollView>
    </Section>
  );
}

function EmptyPanel({ title, text }: { title: string; text: string }) {
  return (
    <View style={styles.emptyPanel}>
      <Ionicons name="image-outline" size={22} color={colors.textTertiary} />
      <View style={styles.emptyBody}>
        <Text style={styles.emptyTitle}>{title}</Text>
        <Text style={styles.emptyText}>{text}</Text>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.background },
  safeArea: { flex: 1 },
  loadingWrap: { flex: 1, justifyContent: "center", alignItems: "center" },
  scrollContent: {
    paddingHorizontal: spacing.lg,
    paddingTop: 80,
    paddingBottom: 140,
  },
  introRow: {
    flexDirection: "row",
    alignItems: "flex-start",
    justifyContent: "space-between",
    gap: spacing.md,
    marginTop: spacing.lg,
    marginBottom: spacing.md,
  },
  introCopy: {
    flex: 1,
  },
  pageTitle: {
    fontSize: 38,
    lineHeight: 44,
    fontWeight: "800",
    color: colors.text,
    letterSpacing: 0,
  },
  pageSubtitle: {
    ...typography.bodySmall,
    color: colors.textSecondary,
    marginTop: spacing.xs,
  },
  livePill: {
    minHeight: 32,
    borderRadius: borderRadius.full,
    borderWidth: 1,
    borderColor: "rgba(200,169,110,0.22)",
    backgroundColor: "rgba(200,169,110,0.08)",
    paddingHorizontal: spacing.sm,
    flexDirection: "row",
    alignItems: "center",
    gap: spacing.xs,
    marginTop: spacing.xs,
  },
  livePillText: {
    ...typography.captionSmall,
    color: colors.textSecondary,
    textTransform: "none",
  },
  cardEyebrow: {
    ...typography.captionSmall,
    color: colors.primary,
    marginBottom: spacing.xs,
  },

  filterRow: {
    gap: spacing.sm,
    paddingBottom: spacing.xl,
  },
  filterChip: {
    height: 40,
    borderRadius: borderRadius.full,
    borderWidth: 1,
    borderColor: "rgba(255,255,255,0.08)",
    backgroundColor: "rgba(30,30,34,0.82)",
    paddingHorizontal: spacing.md,
    flexDirection: "row",
    alignItems: "center",
    gap: spacing.xs,
  },
  filterChipActive: {
    borderColor: "rgba(200,169,110,0.72)",
    backgroundColor: "rgba(200,169,110,0.12)",
  },
  filterText: { ...typography.bodySmall, color: colors.textSecondary, fontWeight: "600" },
  filterTextActive: { color: colors.primary },
  section: {
    marginBottom: spacing.xxl,
  },
  sectionHeader: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    borderBottomWidth: 1,
    borderBottomColor: "rgba(200,169,110,0.12)",
    paddingBottom: spacing.sm,
    marginBottom: spacing.md,
  },
  sectionTitle: { ...typography.caption, color: colors.primary, letterSpacing: 1.7 },
  sectionAction: { ...typography.captionSmall, color: colors.textTertiary, textTransform: "none" },

  placeRow: { gap: spacing.md, paddingRight: spacing.xl },
  placeCard: {
    width: 248,
    height: 316,
    borderRadius: borderRadius.xl,
    borderWidth: 1,
    borderColor: "rgba(200,169,110,0.16)",
    overflow: "hidden",
    backgroundColor: "rgba(20,20,24,0.96)",
  },
  placeImage: { ...StyleSheet.absoluteFillObject },
  placeOverlay: { ...StyleSheet.absoluteFillObject },
  placeTag: {
    position: "absolute",
    top: spacing.md,
    right: spacing.md,
    borderRadius: borderRadius.full,
    backgroundColor: "rgba(0,0,0,0.54)",
    borderWidth: 1,
    borderColor: "rgba(255,255,255,0.22)",
    paddingHorizontal: spacing.sm,
    paddingVertical: 4,
  },
  placeTagText: { ...typography.captionSmall, color: colors.text },
  placeContent: { position: "absolute", left: spacing.lg, right: spacing.lg, bottom: spacing.lg },
  placeCategory: { ...typography.captionSmall, color: colors.primary, marginBottom: spacing.xs },
  placeTitle: { fontSize: 21, lineHeight: 27, fontWeight: "800", color: colors.text },
  placeDesc: { ...typography.bodySmall, color: "rgba(255,255,255,0.78)", marginTop: spacing.sm },
  placeMeta: { ...typography.captionSmall, color: colors.textSecondary, marginTop: spacing.xs },
  routeRow: { gap: spacing.md, paddingRight: spacing.xl },
  routeCard: {
    width: 292,
    height: 218,
    borderRadius: borderRadius.xl,
    borderWidth: 1,
    borderColor: "rgba(200,169,110,0.16)",
    overflow: "hidden",
    backgroundColor: "rgba(20,20,24,0.96)",
  },
  routeImage: { ...StyleSheet.absoluteFillObject },
  routeOverlay: { ...StyleSheet.absoluteFillObject },
  routeContent: { position: "absolute", left: spacing.lg, right: spacing.lg, bottom: spacing.lg },
  routeBadge: {
    alignSelf: "flex-start",
    borderRadius: borderRadius.full,
    backgroundColor: "rgba(0,0,0,0.52)",
    borderWidth: 1,
    borderColor: "rgba(255,255,255,0.16)",
    paddingHorizontal: spacing.sm,
    paddingVertical: 5,
    flexDirection: "row",
    alignItems: "center",
    gap: spacing.xs,
    marginBottom: spacing.md,
  },
  routeBadgeText: { ...typography.captionSmall, color: colors.text },
  routeEyebrow: { ...typography.captionSmall, color: colors.primary, marginBottom: 2 },
  routeTitle: { ...typography.h3, color: colors.text, fontWeight: "800" },
  routeDesc: { ...typography.bodySmall, color: colors.textSecondary, marginTop: spacing.xs },
  compactRow: { gap: spacing.md, paddingRight: spacing.xl },
  compactCard: {
    width: 230,
    minHeight: 112,
    borderRadius: borderRadius.lg,
    borderWidth: 1,
    borderColor: colors.borderLight,
    backgroundColor: "rgba(20,20,24,0.96)",
    overflow: "hidden",
    flexDirection: "row",
  },
  compactImage: {
    width: 92,
    height: "100%",
  },
  compactBody: {
    flex: 1,
    padding: spacing.md,
    justifyContent: "center",
  },
  compactTitle: { ...typography.bodySmall, color: colors.text, fontWeight: "700" },
  compactMeta: { ...typography.captionSmall, color: colors.textSecondary, marginTop: spacing.xs },
  emptyPanel: {
    minHeight: 98,
    borderRadius: borderRadius.lg,
    borderWidth: 1,
    borderColor: colors.borderLight,
    backgroundColor: colors.surface,
    padding: spacing.lg,
    flexDirection: "row",
    alignItems: "center",
  },
  emptyBody: { flex: 1, marginLeft: spacing.md },
  emptyTitle: { ...typography.bodyMedium, color: colors.text, fontWeight: "700" },
  emptyText: { ...typography.bodySmall, color: colors.textSecondary, marginTop: 2 },
});
