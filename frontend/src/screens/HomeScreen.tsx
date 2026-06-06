import React, { useCallback, useEffect, useMemo, useState, useRef } from "react";
import {
  ActivityIndicator,
  RefreshControl,
  ScrollView,
  StyleSheet,
  Text,
  TouchableOpacity,
  View,
  Animated,
  Platform,
} from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { LinearGradient } from "expo-linear-gradient";
import { Ionicons } from "@expo/vector-icons";
import { useNavigation } from "@react-navigation/native";

import { AppHeader } from "../components/AppHeader";
import { DataStatePanel } from "../components/DataStatePanel";
import { cityService, dailyDataService, pharmacyService, weatherService } from "../services/api";
import {
  CurrencyRate,
  Earthquake,
  FuelPrices,
  GoldPrice,
  IzbanSummary,
  Pharmacy,
  PrayerTimes,
  StreetMarket,
  UtilityOutage,
  WeatherData,
} from "../types";
import { borderRadius, colors, spacing, typography } from "../theme";
import { DataState, loadDataState, summarizeSources } from "../utils/dataState";

type IconName = keyof typeof Ionicons.glyphMap;

function ShimmerPlaceholder({ style }: { style: any }) {
  const opacity = useRef(new Animated.Value(0.25)).current;

  useEffect(() => {
    Animated.loop(
      Animated.sequence([
        Animated.timing(opacity, {
          toValue: 0.65,
          duration: 1000,
          useNativeDriver: Platform.OS !== "web",
        }),
        Animated.timing(opacity, {
          toValue: 0.25,
          duration: 1000,
          useNativeDriver: Platform.OS !== "web",
        }),
      ])
    ).start();
  }, []);

  return <Animated.View style={[style, { opacity, backgroundColor: "rgba(255, 255, 255, 0.08)" }]} />;
}

function HomeSkeletonLoader() {
  return (
    <ScrollView contentContainerStyle={styles.scrollContent} showsVerticalScrollIndicator={false}>
      {/* Hero Card Skeleton */}
      <View style={[styles.heroCard, { borderColor: "rgba(255, 255, 255, 0.05)", backgroundColor: "rgba(20,20,24,0.6)" }]}>
        <View style={{ flexDirection: "row", justifyContent: "space-between", marginBottom: spacing.md }}>
          <ShimmerPlaceholder style={{ width: 80, height: 16, borderRadius: 8 }} />
          <ShimmerPlaceholder style={{ width: 120, height: 24, borderRadius: 12 }} />
        </View>
        <ShimmerPlaceholder style={{ width: "65%", height: 38, borderRadius: 8, marginBottom: spacing.sm }} />
        <ShimmerPlaceholder style={{ width: "85%", height: 16, borderRadius: 8, marginBottom: spacing.lg }} />
        
        {/* Weather panel skeleton */}
        <View style={[styles.weatherPanelOuter, { borderColor: "rgba(255, 255, 255, 0.04)", backgroundColor: "rgba(255, 255, 255, 0.02)" }]}>
          <View style={{ flex: 1, gap: 8 }}>
            <ShimmerPlaceholder style={{ width: 110, height: 16, borderRadius: 8 }} />
            <ShimmerPlaceholder style={{ width: 60, height: 32, borderRadius: 8 }} />
            <ShimmerPlaceholder style={{ width: 90, height: 12, borderRadius: 8 }} />
          </View>
          <View style={{ alignItems: "flex-end", gap: 8 }}>
            <ShimmerPlaceholder style={{ width: 42, height: 42, borderRadius: 21 }} />
            <ShimmerPlaceholder style={{ width: 80, height: 14, borderRadius: 8 }} />
          </View>
        </View>
      </View>

      {/* Sinyal Grid Skeleton */}
      <View style={{ marginVertical: spacing.md }}>
        <ShimmerPlaceholder style={{ width: 120, height: 18, borderRadius: 8, marginBottom: spacing.md }} />
        <View style={styles.signalGrid}>
          {[1, 2, 3, 4].map((i) => (
            <View key={i} style={[styles.signalCard, { borderColor: "rgba(255, 255, 255, 0.04)", backgroundColor: "rgba(20, 20, 24, 0.6)", minHeight: 120 }]}>
              <View style={{ flexDirection: "row", gap: 12, alignItems: "center", marginBottom: spacing.sm }}>
                <ShimmerPlaceholder style={{ width: 32, height: 32, borderRadius: 16 }} />
                <ShimmerPlaceholder style={{ width: 60, height: 14, borderRadius: 8 }} />
              </View>
              <ShimmerPlaceholder style={{ width: "80%", height: 18, borderRadius: 8, marginBottom: 6 }} />
              <ShimmerPlaceholder style={{ width: "50%", height: 12, borderRadius: 8 }} />
            </View>
          ))}
        </View>
      </View>

      {/* Kısa Bilgiler Skeleton */}
      <View style={{ marginTop: spacing.md }}>
        <ShimmerPlaceholder style={{ width: 100, height: 18, borderRadius: 8, marginBottom: spacing.md }} />
        <View style={{ flexDirection: "row", gap: 12, marginBottom: spacing.xl }}>
          <ShimmerPlaceholder style={{ width: 120, height: 40, borderRadius: 20 }} />
          <ShimmerPlaceholder style={{ width: 100, height: 40, borderRadius: 20 }} />
          <ShimmerPlaceholder style={{ width: 110, height: 40, borderRadius: 20 }} />
        </View>
      </View>
    </ScrollView>
  );
}

const WEEK_DAYS = ["pazar", "pazartesi", "salı", "çarşamba", "perşembe", "cuma", "cumartesi"];
const AUTO_REFRESH_MS = 5 * 60 * 1000;

const PRAYER_ORDER: Array<{ key: keyof PrayerTimes; label: string }> = [
  { key: "fajr", label: "Sabah" },
  { key: "dhuhr", label: "Öğle" },
  { key: "asr", label: "İkindi" },
  { key: "maghrib", label: "Akşam" },
  { key: "isha", label: "Yatsı" },
];

const INTENT_ACTIONS: Array<{
  icon: IconName;
  title: string;
  detail: string;
  prompt: string;
  tone: string;
}> = [
  {
    icon: "navigate-outline",
    title: "Bir yere gideceğim",
    detail: "Rota, İZBAN, taksi",
    prompt:
      "Aliağa içinde bir yere gitmek istiyorum. Gideceğim yeri sor, sonra İZBAN, taksi, yürüme ve yol tarifi seçenekleriyle en pratik planı çıkar.",
    tone: colors.info,
  },
  {
    icon: "sparkles-outline",
    title: "Günümü planlayacağım",
    detail: "İşler, rota, zaman",
    prompt:
      "Aliağa'da bugün günümü planlamak istiyorum. Önce ne yapmak istediğimi sor; sonra zaman, rota, ulaşım, nöbetçi eczane, pazar ve şehir bilgilerine göre kısa ve uygulanabilir bir plan çıkar.",
    tone: colors.tertiary,
  },
  {
    icon: "search-outline",
    title: "Bir şey arıyorum",
    detail: "Yer, kurum, hizmet",
    prompt:
      "Aliağa'da bir yer, kurum, hizmet veya bilgi arıyorum. Ne aradığımı sor ve uygun sonuçları adres, telefon, konum veya kaynak bilgisiyle getir.",
    tone: colors.primary,
  },
];

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

function formatDateLabel(date: Date): string {
  const months = [
    "Ocak",
    "Şubat",
    "Mart",
    "Nisan",
    "Mayıs",
    "Haziran",
    "Temmuz",
    "Ağustos",
    "Eylül",
    "Ekim",
    "Kasım",
    "Aralık",
  ];
  const week = ["Paz", "Pts", "Sal", "Çar", "Per", "Cum", "Cts"];
  return `${date.getDate()} ${months[date.getMonth()]}, ${week[date.getDay()]}`;
}

function weatherIconName(desc?: string | null): IconName {
  const text = normalizeText(desc);
  if (text.includes("yag") || text.includes("rain") || text.includes("cisil")) return "rainy-outline";
  if (text.includes("firt") || text.includes("storm") || text.includes("gokgur") || text.includes("simsek")) return "thunderstorm-outline";
  if (text.includes("kar") || text.includes("snow")) return "snow-outline";
  if (text.includes("kapali") || text.includes("overcast") || text.includes("sis") || text.includes("pus") || text.includes("duman")) return "cloudy-outline";
  if (text.includes("bulut") || text.includes("cloud")) {
    if (text.includes("cok") || text.includes("most")) return "cloudy-outline";
    return "partly-sunny-outline";
  }
  return "sunny-outline";
}

function getWeatherGradient(desc?: string | null): [string, string] {
  const text = normalizeText(desc);
  if (
    text.includes("yag") ||
    text.includes("rain") ||
    text.includes("firt") ||
    text.includes("storm") ||
    text.includes("kar") ||
    text.includes("snow") ||
    text.includes("gokgur") ||
    text.includes("simsek")
  ) {
    return ["rgba(30, 36, 42, 0.95)", "rgba(15, 17, 20, 0.95)"];
  }
  if (
    text.includes("bulut") ||
    text.includes("cloud") ||
    text.includes("kapali") ||
    text.includes("overcast") ||
    text.includes("sis") ||
    text.includes("pus")
  ) {
    return ["rgba(42, 38, 34, 0.95)", "rgba(18, 18, 18, 0.95)"];
  }
  return ["rgba(56, 46, 32, 0.95)", "rgba(20, 16, 12, 0.95)"];
}

function formatTemperature(value?: number | null): string {
  return typeof value === "number" && Number.isFinite(value) ? `${Math.round(value)}°` : "--°";
}

function formatMoney(value?: number | null): string {
  return typeof value === "number" && Number.isFinite(value) ? `${value.toFixed(2)} TL` : "Bekleniyor";
}

function formatShortDateTime(value?: string | null): string {
  if (!value) return "";
  const date = new Date(value);
  if (!Number.isFinite(date.getTime())) return "";
  return date.toLocaleString("tr-TR", {
    day: "2-digit",
    month: "short",
    hour: "2-digit",
    minute: "2-digit",
  });
}

function parseDateOnly(value?: string | null): Date | null {
  if (!value) return null;
  const match = /^(\d{4})-(\d{2})-(\d{2})/.exec(value);
  if (match) {
    const [, year, month, day] = match;
    return new Date(Number(year), Number(month) - 1, Number(day));
  }
  const date = new Date(value);
  return Number.isFinite(date.getTime()) ? date : null;
}

function isTodayDate(value?: string | null): boolean {
  const date = parseDateOnly(value);
  if (!date) return false;
  const now = new Date();
  return (
    date.getFullYear() === now.getFullYear() &&
    date.getMonth() === now.getMonth() &&
    date.getDate() === now.getDate()
  );
}

function formatDateOnly(value?: string | null): string {
  const date = parseDateOnly(value);
  if (!date) return "";
  return date.toLocaleDateString("tr-TR", { day: "2-digit", month: "short" });
}

function isOlderThan(value?: string | null, hours = 24): boolean {
  if (!value) return false;
  const date = new Date(value);
  if (!Number.isFinite(date.getTime())) return false;
  return Date.now() - date.getTime() > hours * 60 * 60 * 1000;
}

function getFreshnessLabel(value?: string | null): string {
  if (!value) return "Veri bekleniyor";
  const label = formatShortDateTime(value);
  return isOlderThan(value, 24) ? `Son veri ${label}` : `Güncel ${label}`;
}

function getNextMarketInfo(markets: StreetMarket[]): { value: string; detail: string } {
  if (markets.length === 0) return { value: "Pazar verisi hazırlanıyor", detail: "Haftalık bilgi bekleniyor" };
  const now = new Date();
  for (let offset = 0; offset < 7; offset += 1) {
    const dayIndex = (now.getDay() + offset) % 7;
    const dayKey = normalizeText(WEEK_DAYS[dayIndex]);
    const matches = markets.filter((market) => normalizeText(market.day_of_week).includes(dayKey));
    if (matches.length > 0) {
      const first = matches[0];
      const prefix = offset === 0 ? "Bugün" : offset === 1 ? "Yarın" : WEEK_DAYS[dayIndex];
      return {
        value: matches.length === 1 ? `${prefix}: ${first.name}` : `${prefix}: ${matches.length} pazar`,
        detail: first.neighborhood || first.address || "Haftalık pazar bilgisi",
      };
    }
  }
  return { value: `${markets.length} pazar kaydı`, detail: "Haftalık bilgi" };
}

function getNextPrayer(prayer: PrayerTimes | null): string {
  if (!prayer) return "Vakit bekleniyor";

  const now = new Date();
  const nowMinutes = now.getHours() * 60 + now.getMinutes();
  let lastKnown: { label: string; time: string } | null = null;

  for (const item of PRAYER_ORDER) {
    const time = prayer[item.key];
    if (typeof time !== "string") continue;
    const [hourRaw, minuteRaw] = time.split(":");
    const hour = Number(hourRaw);
    const minute = Number(minuteRaw);
    if (!Number.isFinite(hour) || !Number.isFinite(minute)) continue;
    lastKnown = { label: item.label, time };
    if (hour * 60 + minute >= nowMinutes) {
      return `${item.label} ${time}`;
    }
  }

  return lastKnown ? `${lastKnown.label} ${lastKnown.time}` : "Vakit bekleniyor";
}

function firstCurrency(currencies: CurrencyRate[], code: string): CurrencyRate | undefined {
  return currencies.find((item) => normalizeText(item.code) === normalizeText(code));
}

function gramGold(golds: GoldPrice[]): GoldPrice | undefined {
  return golds.find((item) => normalizeText(item.name).includes("gram")) || golds[0];
}

function getLatestEarthquake(earthquakes: Earthquake[]): string {
  const latest = earthquakes[0];
  if (!latest) return "Kayıt yok";
  const magnitude = typeof latest.magnitude === "number" && Number.isFinite(latest.magnitude)
    ? latest.magnitude.toFixed(1)
    : "--";
  return `${magnitude} ${latest.location || ""}`.trim();
}

function getOutageLabel(outages: UtilityOutage[]): string {
  return outages.length > 0 ? `${outages.length} kayıt` : "Planlı yok";
}

function getOutageDetail(outages: UtilityOutage[]): string {
  const first = outages[0];
  if (!first) return "Planlı kesinti görünmüyor";
  return first.neighborhood || first.district || first.description || "Detay bekleniyor";
}

type SignalCardProps = {
  icon: IconName;
  title: string;
  value: string;
  detail: string;
  tone?: "primary" | "info" | "success" | "warning";
  onPress?: () => void;
};

type HomeSourceKey =
  | "weather"
  | "pharmacy"
  | "outage"
  | "izban"
  | "market"
  | "prayer"
  | "fuel"
  | "currency"
  | "gold"
  | "earthquake";

type HomeSourceStates = Record<HomeSourceKey, DataState<unknown>>;

function SignalCard({ icon, title, value, detail, tone = "primary", onPress }: SignalCardProps) {
  const toneColor =
    tone === "info"
      ? colors.info
      : tone === "success"
        ? colors.success
        : tone === "warning"
          ? colors.warning
          : colors.primary;

  return (
    <TouchableOpacity
      accessibilityRole={onPress ? "button" : undefined}
      activeOpacity={onPress ? 0.85 : 1}
      disabled={!onPress}
      onPress={onPress}
      style={[styles.signalCard, { borderColor: `${toneColor}2F` }]}
    >
      <View style={styles.signalHead}>
        <View style={[styles.signalIcon, { backgroundColor: `${toneColor}20` }]}>
          <Ionicons name={icon} size={18} color={toneColor} />
        </View>
        {onPress ? (
          <View style={styles.signalArrow}>
            <Ionicons name="chevron-forward" size={15} color={colors.textSecondary} />
          </View>
        ) : null}
      </View>
      <View style={styles.signalTextWrap}>
        <Text style={styles.signalTitle}>{title}</Text>
        <Text style={styles.signalValue} numberOfLines={1}>
          {value}
        </Text>
        <Text style={styles.signalDetail} numberOfLines={1}>
          {detail}
        </Text>
      </View>
    </TouchableOpacity>
  );
}

function InfoPill({
  icon,
  title,
  value,
  onPress,
}: {
  icon: IconName;
  title: string;
  value: string;
  onPress?: () => void;
}) {
  return (
    <TouchableOpacity
      accessibilityRole={onPress ? "button" : undefined}
      activeOpacity={onPress ? 0.85 : 1}
      disabled={!onPress}
      onPress={onPress}
      style={styles.infoPill}
    >
      <View style={styles.infoPillIcon}>
        <Ionicons name={icon} size={15} color={colors.primary} />
      </View>
      <Text style={styles.infoPillTitle}>{title}</Text>
      <Text style={styles.infoPillValue} numberOfLines={1}>
        {value}
      </Text>
    </TouchableOpacity>
  );
}

function SectionHeader({ title, meta }: { title: string; meta?: string }) {
  return (
    <View style={styles.sectionHeader}>
      <Text style={styles.sectionTitle}>{title}</Text>
      {meta ? <Text style={styles.sectionMeta}>{meta}</Text> : null}
    </View>
  );
}

export function HomeScreen() {
  const navigation = useNavigation<any>();
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [sourceStates, setSourceStates] = useState<HomeSourceStates | null>(null);
  const [weather, setWeather] = useState<WeatherData | null>(null);
  const [pharmacies, setPharmacies] = useState<Pharmacy[]>([]);
  const [outages, setOutages] = useState<UtilityOutage[]>([]);
  const [izban, setIzban] = useState<IzbanSummary | null>(null);
  const [markets, setMarkets] = useState<StreetMarket[]>([]);
  const [prayer, setPrayer] = useState<PrayerTimes | null>(null);
  const [fuel, setFuel] = useState<FuelPrices | null>(null);
  const [currencies, setCurrencies] = useState<CurrencyRate[]>([]);
  const [golds, setGolds] = useState<GoldPrice[]>([]);
  const [earthquakes, setEarthquakes] = useState<Earthquake[]>([]);

  const load = useCallback(async (isRefresh = false) => {
    if (isRefresh) {
      setRefreshing(true);
    } else {
      setLoading(true);
    }

    try {
      const [
        weatherState,
        pharmacyState,
        outageState,
        izbanState,
        marketState,
        prayerState,
        fuelState,
        currencyState,
        goldState,
        earthquakeState,
      ] = await Promise.all([
        loadDataState(() => weatherService.getToday(), null),
        loadDataState(() => pharmacyService.getToday(), [] as Pharmacy[]),
        loadDataState(() => cityService.getOutages(20), [] as UtilityOutage[]),
        loadDataState(() => cityService.getIzbanSummary(), null),
        loadDataState(() => cityService.getMarkets(50), [] as StreetMarket[]),
        loadDataState(() => dailyDataService.getPrayerTimes(), null),
        loadDataState(() => dailyDataService.getFuelPrices(), null),
        loadDataState(() => dailyDataService.getCurrency(), [] as CurrencyRate[]),
        loadDataState(() => dailyDataService.getGold(), [] as GoldPrice[]),
        loadDataState(() => dailyDataService.getEarthquakes(), [] as Earthquake[]),
      ]);

      setWeather(weatherState.data);
      setPharmacies(pharmacyState.data);
      setOutages(outageState.data);
      setIzban(izbanState.data);
      setMarkets(marketState.data);
      setPrayer(prayerState.data);
      setFuel(fuelState.data);
      setCurrencies(currencyState.data);
      setGolds(goldState.data);
      setEarthquakes(earthquakeState.data);
      setSourceStates({
        weather: weatherState,
        pharmacy: pharmacyState,
        outage: outageState,
        izban: izbanState,
        market: marketState,
        prayer: prayerState,
        fuel: fuelState,
        currency: currencyState,
        gold: goldState,
        earthquake: earthquakeState,
      });
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

  const nextMarket = useMemo(() => getNextMarketInfo(markets), [markets]);
  const activeOutages = useMemo(
    () =>
      outages.filter((row) => {
        if (!row.end_date) return true;
        const endDate = new Date(row.end_date);
        return !Number.isFinite(endDate.getTime()) || endDate > new Date();
      }),
    [outages]
  );
  const usd = useMemo(() => firstCurrency(currencies, "USD"), [currencies]);
  const gold = useMemo(() => gramGold(golds), [golds]);
  const sourceSummary = useMemo(
    () => summarizeSources(sourceStates ? Object.values(sourceStates) : []),
    [sourceStates]
  );

  const dateLabel = useMemo(() => formatDateLabel(new Date()), []);
  const weatherRange =
    typeof weather?.min_temp === "number" && typeof weather?.max_temp === "number"
      ? `${Math.round(weather.min_temp)}° / ${Math.round(weather.max_temp)}°`
      : "Aralık yok";
  const firstPharmacy = pharmacies[0];
  const hasTodayPharmacy = firstPharmacy ? isTodayDate(firstPharmacy.duty_date) : false;
  const pharmacySourceStatus = sourceStates?.pharmacy.status;
  const pharmacyDetail = firstPharmacy
    ? hasTodayPharmacy
      ? `${pharmacies.length} bugünkü nöbetçi`
      : `Son kayıt ${formatDateOnly(firstPharmacy.duty_date)}`
    : pharmacySourceStatus === "error"
      ? "Kaynak cevap vermedi"
      : "Son kayıt bekleniyor";
  const izbanFreshness =
    izban?.updated_at && isOlderThan(izban.updated_at, 48)
      ? `Eski veri ${formatShortDateTime(izban.updated_at)}`
      : getFreshnessLabel(izban?.updated_at);
  const heroStatus =
    activeOutages.length > 0
      ? `${activeOutages.length} kesinti uyarısı`
      : sourceSummary.error > 0
        ? `${sourceSummary.error} kaynak yenilenemedi`
        : firstPharmacy
        ? "Günlük veriler hazır"
        : "Veriler güncelleniyor";
  const heroSummary =
    activeOutages.length > 0
      ? "Planlı kesintileri kontrol et, rota ve günlük işleri ona göre ayarla."
      : sourceSummary.error > 0
        ? "Bazı kaynaklar anlık cevap vermedi; eldeki veriler ve eksik alanlar ayrı gösteriliyor."
        : firstPharmacy
        ? "Hava, nöbetçi eczane, ulaşım ve günlük şehir verisi tek bakışta hazır."
        : "Şehir akışı yükleniyor; kritik bilgiler geldikçe burada öne çıkar.";
  const openIntent = (prompt: string) => {
    navigation.navigate("Chat", {
      presetPrompt: prompt,
      presetPromptId: `${Date.now()}`,
    });
  };

  return (
    <View style={styles.container}>
      <SafeAreaView style={styles.safeArea} edges={["top"]}>
        <AppHeader />

        {loading ? (
          <HomeSkeletonLoader />
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
            <LinearGradient
              colors={["rgba(31,31,35,0.98)", "rgba(14,14,16,0.98)", "rgba(9,9,10,0.96)"]}
              locations={[0, 0.58, 1]}
              style={styles.heroCard}
            >
              <View style={styles.heroGlow} />
              <View style={styles.heroHeader}>
                <View style={styles.heroKickerRow}>
                  <View style={styles.kickerMark} />
                  <Text style={styles.todayText}>BUGÜN</Text>
                </View>
                <View style={styles.statusBadge}>
                  <Ionicons
                    name={activeOutages.length > 0 ? "alert-circle-outline" : "checkmark-circle-outline"}
                    size={14}
                    color={colors.primary}
                  />
                  <Text style={styles.statusBadgeText}>{heroStatus}</Text>
                </View>
              </View>

              <Text style={styles.dateText}>{dateLabel}</Text>
              <Text style={styles.heroSummary}>{heroSummary}</Text>

              <TouchableOpacity
                accessibilityRole="button"
                activeOpacity={0.88}
                onPress={() => navigation.navigate("WeatherDetail")}
                style={styles.weatherPanelOuter}
              >
                <LinearGradient
                  colors={getWeatherGradient(weather?.description)}
                  start={{ x: 0, y: 0 }}
                  end={{ x: 1, y: 1 }}
                  style={styles.weatherPanelInner}
                >
                  <View style={styles.weatherPanelLeft}>
                    <View style={styles.locationRow}>
                      <Ionicons name="location" size={14} color={colors.primary} />
                      <Text style={styles.locationText}>Aliağa, Merkez</Text>
                    </View>
                    <Text style={styles.temperature}>{formatTemperature(weather?.temperature)}</Text>
                    <Text style={styles.updateText}>{getFreshnessLabel(weather?.fetched_at)}</Text>
                  </View>

                  <View style={styles.weatherPanelRight}>
                    <Ionicons name={weatherIconName(weather?.description)} size={48} color={colors.primary} />
                    <Text style={styles.weatherDesc} numberOfLines={1}>
                      {weather?.description || "Hava verisi yok"}
                    </Text>
                    <Text style={styles.weatherRange}>{weatherRange}</Text>
                  </View>
                </LinearGradient>
              </TouchableOpacity>
            </LinearGradient>

            <SectionHeader title="ŞEHİR DURUMU" meta="Canlı sinyaller" />
            {sourceSummary.error > 0 ? (
              <View style={styles.statePanelWrap}>
                <DataStatePanel
                  tone="warning"
                  title="Bazı canlı kaynaklar yenilenemedi"
                  text={`${sourceSummary.ready} kaynak güncel cevap verdi. Aşağıdaki kartlar hata, boş ve eski veriyi ayrı gösterir.`}
                />
              </View>
            ) : sourceSummary.empty > 0 ? (
              <View style={styles.statePanelWrap}>
                <DataStatePanel
                  tone="info"
                  title="Bazı veri alanları boş döndü"
                  text="Bu durum hata değil; kaynakta kayıt yoksa kartlar beklenen boş durum mesajını gösterir."
                />
              </View>
            ) : null}

            <View style={styles.signalGrid}>
              <SignalCard
                icon="medical-outline"
                title="Eczane"
                value={pharmacySourceStatus === "error" ? "Kaynak yenilenemedi" : firstPharmacy?.name || "Son veri bekleniyor"}
                detail={pharmacyDetail}
                tone={hasTodayPharmacy ? "success" : "warning"}
                onPress={() => navigation.navigate("PharmacyList")}
              />
              <SignalCard
                icon="train-outline"
                title="İZBAN"
                value={izban?.next_departure ? `Sonraki ${izban.next_departure}` : "Saat bekleniyor"}
                detail={izbanFreshness}
                tone="info"
                onPress={() => navigation.navigate("IzbanSchedule")}
              />
              <SignalCard
                icon="flash-outline"
                title="Kesinti"
                value={getOutageLabel(activeOutages)}
                detail={getOutageDetail(activeOutages)}
                tone={activeOutages.length > 0 ? "warning" : "success"}
                onPress={() => navigation.navigate("OutageList")}
              />
              <SignalCard
                icon="basket-outline"
                title="Pazar"
                value={nextMarket.value}
                detail={nextMarket.detail}
                onPress={() => navigation.navigate("MarketList")}
              />
            </View>

            <SectionHeader title="KISA BİLGİLER" meta="Günlük takip" />
            <ScrollView
              horizontal
              showsHorizontalScrollIndicator={false}
              contentContainerStyle={styles.infoStrip}
            >
              <InfoPill
                icon="time-outline"
                title="Namaz"
                value={getNextPrayer(prayer)}
                onPress={() => navigation.navigate("PrayerTimes")}
              />
              <InfoPill
                icon="car-outline"
                title="Benzin"
                value={formatMoney(fuel?.gasoline)}
                onPress={() => navigation.navigate("MarketRates")}
              />
              <InfoPill
                icon="trending-up-outline"
                title="USD"
                value={formatMoney(usd?.selling || usd?.buying)}
                onPress={() => navigation.navigate("MarketRates")}
              />
              <InfoPill
                icon="diamond-outline"
                title="Gram"
                value={formatMoney(gold?.selling || gold?.buying)}
                onPress={() => navigation.navigate("MarketRates")}
              />
              <InfoPill
                icon="pulse-outline"
                title="Deprem"
                value={getLatestEarthquake(earthquakes)}
                onPress={() => navigation.navigate("EarthquakeList")}
              />
            </ScrollView>

            <View style={styles.intentCard}>
              <LinearGradient
                colors={["rgba(200,169,110,0.16)", "rgba(255,255,255,0.03)", "rgba(255,255,255,0)"]}
                start={{ x: 0, y: 0 }}
                end={{ x: 1, y: 1 }}
                style={styles.intentGlow}
              />
              <View style={styles.intentHead}>
                <View>
                  <Text style={styles.intentTitle}>AKILLI AKSİYONLAR</Text>
                  <Text style={styles.intentSubtitle}>AI, Aliağa içinde doğru akışı başlatsın.</Text>
                </View>
                <View style={styles.intentChip}>
                  <Ionicons name="hardware-chip-outline" size={18} color={colors.primary} />
                </View>
              </View>
              <View style={styles.intentList}>
                {INTENT_ACTIONS.map((action) => (
                  <TouchableOpacity
                    key={action.title}
                    accessibilityRole="button"
                    activeOpacity={0.86}
                    style={styles.intentButton}
                    onPress={() => openIntent(action.prompt)}
                  >
                    <View style={[styles.intentIcon, { backgroundColor: `${action.tone}22` }]}>
                      <Ionicons name={action.icon} size={17} color={action.tone} />
                    </View>
                    <View style={styles.intentBody}>
                      <Text style={styles.intentButtonTitle}>{action.title}</Text>
                      <Text style={styles.intentButtonDetail}>{action.detail}</Text>
                    </View>
                    <Ionicons name="arrow-forward" size={16} color={colors.textTertiary} />
                  </TouchableOpacity>
                ))}
              </View>
            </View>
          </ScrollView>
        )}
      </SafeAreaView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
  },
  safeArea: {
    flex: 1,
  },
  loadingWrap: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
  },
  scrollContent: {
    paddingHorizontal: spacing.lg,
    paddingTop: 80,
    paddingBottom: 140,
    ...Platform.select({
      web: {
        maxWidth: 720,
        alignSelf: "center",
        width: "100%",
      } as any,
    }),
  },
  heroCard: {
    position: "relative",
    overflow: "hidden",
    borderRadius: borderRadius.xl,
    borderWidth: 1,
    borderColor: "rgba(200,169,110,0.24)",
    padding: spacing.lg,
    marginTop: spacing.lg,
    marginBottom: spacing.xl,
  },
  heroGlow: {
    position: "absolute",
    top: -70,
    right: -58,
    width: 170,
    height: 170,
    borderRadius: 85,
    backgroundColor: "rgba(200,169,110,0.14)",
  },
  heroHeader: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    gap: spacing.md,
    marginBottom: spacing.md,
  },
  heroKickerRow: {
    flexDirection: "row",
    alignItems: "center",
    gap: spacing.sm,
  },
  kickerMark: {
    width: 7,
    height: 7,
    borderRadius: 4,
    backgroundColor: colors.primary,
  },
  todayText: {
    ...typography.caption,
    color: colors.primary,
    letterSpacing: 1.8,
  },
  statusBadge: {
    minHeight: 30,
    maxWidth: 176,
    flexDirection: "row",
    alignItems: "center",
    gap: spacing.xs,
    borderRadius: borderRadius.full,
    borderWidth: 1,
    borderColor: "rgba(200,169,110,0.24)",
    backgroundColor: "rgba(200,169,110,0.08)",
    paddingHorizontal: spacing.sm,
  },
  statusBadgeText: {
    ...typography.captionSmall,
    color: colors.textSecondary,
    textTransform: "none",
  },
  dateText: {
    fontFamily: "Outfit_800ExtraBold",
    fontSize: 32,
    lineHeight: 38,
    color: colors.text,
    letterSpacing: -0.5,
  },
  heroSummary: {
    ...typography.bodySmall,
    color: colors.textSecondary,
    maxWidth: 296,
    marginTop: spacing.xs,
    marginBottom: spacing.lg,
  },
  weatherPanelOuter: {
    minHeight: 132,
    borderRadius: borderRadius.lg,
    overflow: "hidden",
    borderWidth: 1,
    borderColor: "rgba(255,255,255,0.09)",
  },
  weatherPanelInner: {
    flex: 1,
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "stretch",
    padding: spacing.lg,
  },
  weatherPanelLeft: {
    flex: 1,
    justifyContent: "space-between",
    paddingRight: spacing.md,
  },
  weatherPanelRight: {
    width: 134,
    alignItems: "flex-end",
    justifyContent: "space-between",
  },
  locationRow: {
    flexDirection: "row",
    alignItems: "center",
    gap: spacing.xs,
  },
  locationText: {
    ...typography.captionSmall,
    color: colors.text,
    textTransform: "none",
  },
  updateText: {
    ...typography.captionSmall,
    color: colors.textTertiary,
    textTransform: "none",
  },
  temperature: {
    fontSize: 56,
    lineHeight: 62,
    fontWeight: "300",
    color: colors.text,
  },
  weatherDesc: {
    maxWidth: 132,
    fontSize: 15,
    lineHeight: 20,
    fontWeight: "700",
    color: colors.text,
    textAlign: "right",
    textTransform: "capitalize",
  },
  weatherRange: {
    ...typography.captionSmall,
    color: colors.textSecondary,
    textAlign: "right",
    textTransform: "none",
  },
  sectionHeader: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    marginBottom: spacing.sm,
  },
  sectionTitle: {
    ...typography.caption,
    color: colors.primary,
    letterSpacing: 1.5,
  },
  sectionMeta: {
    ...typography.captionSmall,
    color: colors.textTertiary,
    textTransform: "none",
  },
  statePanelWrap: {
    marginBottom: spacing.md,
  },
  signalGrid: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: spacing.sm,
    marginBottom: spacing.xl,
  },
  signalCard: {
    width: "48.5%",
    minHeight: 126,
    justifyContent: "space-between",
    backgroundColor: "rgba(23,23,26,0.88)",
    borderRadius: borderRadius.lg,
    borderWidth: 1,
    padding: spacing.md,
  },
  signalHead: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    marginBottom: spacing.sm,
  },
  signalIcon: {
    width: 36,
    height: 36,
    borderRadius: 18,
    justifyContent: "center",
    alignItems: "center",
  },
  signalArrow: {
    width: 28,
    height: 28,
    borderRadius: 14,
    alignItems: "center",
    justifyContent: "center",
    backgroundColor: "rgba(255,255,255,0.05)",
  },
  signalTextWrap: {
    minWidth: 0,
  },
  signalTitle: {
    ...typography.captionSmall,
    color: colors.textSecondary,
    marginBottom: 2,
  },
  signalValue: {
    fontSize: 17,
    lineHeight: 22,
    fontWeight: "800",
    color: colors.text,
  },
  signalDetail: {
    ...typography.captionSmall,
    color: colors.textSecondary,
    marginTop: 2,
  },
  infoStrip: {
    gap: spacing.sm,
    paddingBottom: spacing.xl,
  },
  infoPill: {
    width: 132,
    minHeight: 92,
    backgroundColor: "rgba(24,24,27,0.82)",
    borderWidth: 1,
    borderColor: "rgba(255,255,255,0.08)",
    borderRadius: borderRadius.lg,
    padding: spacing.md,
  },
  infoPillIcon: {
    width: 26,
    height: 26,
    borderRadius: 13,
    alignItems: "center",
    justifyContent: "center",
    backgroundColor: colors.primaryLight,
  },
  infoPillTitle: {
    ...typography.captionSmall,
    color: colors.textSecondary,
    marginTop: spacing.sm,
  },
  infoPillValue: {
    ...typography.bodySmall,
    color: colors.text,
    fontWeight: "700",
    marginTop: 2,
  },
  intentCard: {
    position: "relative",
    overflow: "hidden",
    backgroundColor: "rgba(19,19,22,0.94)",
    borderRadius: borderRadius.xl,
    borderWidth: 1,
    borderColor: "rgba(200,169,110,0.2)",
    padding: spacing.lg,
  },
  intentGlow: {
    position: "absolute",
    top: 0,
    left: 0,
    right: 0,
    height: 110,
  },
  intentHead: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "flex-start",
    marginBottom: spacing.md,
  },
  intentTitle: {
    ...typography.captionSmall,
    color: colors.primary,
    letterSpacing: 1.4,
  },
  intentSubtitle: {
    ...typography.bodySmall,
    color: colors.textSecondary,
    marginTop: spacing.xs,
  },
  intentChip: {
    width: 38,
    height: 38,
    borderRadius: 19,
    alignItems: "center",
    justifyContent: "center",
    borderWidth: 1,
    borderColor: "rgba(200,169,110,0.25)",
    backgroundColor: "rgba(200,169,110,0.08)",
  },
  intentList: {
    gap: spacing.sm,
  },
  intentButton: {
    minHeight: 64,
    borderRadius: borderRadius.lg,
    backgroundColor: "rgba(255,255,255,0.045)",
    borderWidth: 1,
    borderColor: "rgba(255,255,255,0.075)",
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
    flexDirection: "row",
    alignItems: "center",
  },
  intentIcon: {
    width: 34,
    height: 34,
    borderRadius: 17,
    justifyContent: "center",
    alignItems: "center",
    marginRight: spacing.md,
  },
  intentBody: {
    flex: 1,
    minWidth: 0,
  },
  intentButtonTitle: {
    ...typography.bodySmall,
    color: colors.text,
    fontWeight: "700",
  },
  intentButtonDetail: {
    ...typography.captionSmall,
    color: colors.textSecondary,
    marginTop: 2,
  },
});
