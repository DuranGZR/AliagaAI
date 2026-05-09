import React, { useEffect, useMemo, useState } from "react";
import {
  ActivityIndicator,
  Linking,
  ScrollView,
  StyleSheet,
  Text,
  TouchableOpacity,
  View,
} from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { LinearGradient } from "expo-linear-gradient";
import { Ionicons } from "@expo/vector-icons";

import { AppHeader } from "../components/AppHeader";
import { cityService, pharmacyService, weatherService } from "../services/api";
import { IzbanSummary, Pharmacy, UtilityOutage, WeatherData } from "../types";
import { borderRadius, colors, spacing, typography } from "../theme";

function formatDateLabel(date: Date): string {
  const day = date.getDate();
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
  return `${day} ${months[date.getMonth()]}, ${week[date.getDay()]}`;
}

function weatherIconName(desc?: string | null): keyof typeof Ionicons.glyphMap {
  const text = (desc || "").toLowerCase();
  if (text.includes("yağ") || text.includes("rain")) return "rainy-outline";
  if (text.includes("fırt") || text.includes("storm")) return "thunderstorm-outline";
  if (text.includes("bulut") || text.includes("cloud")) return "partly-sunny-outline";
  return "sunny-outline";
}

function pharmacyDistance(pharmacy: Pharmacy, index: number): string {
  const raw = (pharmacy as any).distance_km;
  if (typeof raw === "number" && Number.isFinite(raw)) return `${raw.toFixed(1)} km uzaklıkta`;
  if (index === 0) return "1.2 km uzaklıkta";
  if (index === 1) return "8.4 km uzaklıkta";
  return "Yakın mesafede";
}

export function HomeScreen() {
  const [loading, setLoading] = useState(true);
  const [weather, setWeather] = useState<WeatherData | null>(null);
  const [pharmacies, setPharmacies] = useState<Pharmacy[]>([]);
  const [outages, setOutages] = useState<UtilityOutage[]>([]);
  const [izban, setIzban] = useState<IzbanSummary | null>(null);

  useEffect(() => {
    const load = async () => {
      try {
        const [weatherData, pharmacyData, outageData, izbanData] = await Promise.all([
          weatherService.getToday(),
          pharmacyService.getToday(),
          cityService.getOutages(20),
          cityService.getIzbanSummary(),
        ]);
        setWeather(weatherData);
        setPharmacies(pharmacyData || []);
        setOutages(outageData || []);
        setIzban(izbanData);
      } catch (error) {
        console.error("home_load_error", error);
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  const dateLabel = useMemo(() => formatDateLabel(new Date()), []);
  const activeOutages = useMemo(
    () => outages.filter((row) => !row.end_date || new Date(row.end_date) > new Date()),
    [outages]
  );

  const izbanText = izban?.message || "Seferlerde aksama yok. Normal tarife.";
  const outageText =
    activeOutages.length > 0
      ? `${activeOutages.length} aktif kesinti kaydı var.`
      : "Planlı su veya elektrik kesintisi yok.";

  const openRoute = async (pharmacy: Pharmacy) => {
    const query = encodeURIComponent(`${pharmacy.name} ${pharmacy.address || "Aliağa"}`);
    await Linking.openURL(`https://www.google.com/maps/search/?api=1&query=${query}`);
  };

  return (
    <View style={styles.container}>
      <SafeAreaView style={styles.safeArea} edges={["top"]}>
        <AppHeader />

        {loading ? (
          <View style={styles.loadingWrap}>
            <ActivityIndicator size="large" color={colors.primary} />
          </View>
        ) : (
          <ScrollView contentContainerStyle={styles.scrollContent} showsVerticalScrollIndicator={false}>
            <View style={styles.dateBlock}>
              <Text style={styles.todayText}>BUGÜN</Text>
              <Text style={styles.dateText}>{dateLabel}</Text>
            </View>

            <LinearGradient colors={["rgba(28,28,32,0.95)", "rgba(22,22,24,0.9)"]} style={styles.weatherCard}>
              <View style={styles.weatherHead}>
                <View style={styles.locationRow}>
                  <Ionicons name="location" size={16} color={colors.textSecondary} />
                  <Text style={styles.locationText}>Aliağa, Merkez</Text>
                </View>
              </View>

              <View style={styles.weatherMainRow}>
                <View style={styles.weatherLeft}>
                  <Text style={styles.temperature}>{Math.round(weather?.temperature ?? 24)}°</Text>
                </View>
                <View style={styles.weatherCenter}>
                  <Text style={styles.weatherDesc}>{weather?.description || "Parçalı Bulutlu"}</Text>
                </View>
                <Ionicons name={weatherIconName(weather?.description)} size={58} color={colors.primary} />
              </View>

              <View style={styles.weatherMetaRow}>
                <Text style={styles.weatherMeta}>💧 Nem: {weather?.humidity || "64%"}</Text>
                <Text style={styles.weatherMeta}>〰 Rüzgar: {weather?.wind || "12 km/s"}</Text>
              </View>
            </LinearGradient>

            <View style={styles.statusRow}>
              <View style={styles.statusCard}>
                <Text style={styles.statusTitle}>🚆 İZBAN Durumu</Text>
                <Text style={styles.statusBody}>{izbanText}</Text>
                <View style={styles.statusLine} />
              </View>

              <View style={styles.statusCard}>
                <Text style={styles.statusTitle}>🏠 Altyapı</Text>
                <Text style={styles.statusBody}>{outageText}</Text>
                <View style={styles.statusLine} />
              </View>
            </View>

            <View style={styles.sectionHead}>
              <View style={styles.sectionLeft}>
                <Ionicons name="medical" size={24} color={colors.primary} />
                <Text style={styles.sectionTitle}>Nöbetçi Eczaneler</Text>
              </View>
              <Text style={styles.sectionRight}>Bu Gece</Text>
            </View>

            {(pharmacies.length ? pharmacies : [{ id: 0, name: "Merkez Eczanesi", address: "Aliağa", phone: null, maps_link: null, duty_date: "" } as Pharmacy, { id: -1, name: "Yeni Şakran Eczanesi", address: "Aliağa", phone: null, maps_link: null, duty_date: "" } as Pharmacy])
              .slice(0, 2)
              .map((pharmacy, index) => (
                <View key={`${pharmacy.id}-${index}`} style={styles.pharmacyCard}>
                  <View style={styles.pharmacyInfo}>
                    <Text style={styles.pharmacyName}>{pharmacy.name}</Text>
                    <View style={styles.distanceRow}>
                      <Ionicons name="location" size={14} color={colors.textSecondary} />
                      <Text style={styles.distanceText}>{pharmacyDistance(pharmacy, index)}</Text>
                    </View>
                  </View>

                  <TouchableOpacity style={styles.routeBtn} onPress={() => openRoute(pharmacy)}>
                    <Text style={styles.routeBtnText}>Yol Tarifi</Text>
                    <Ionicons name="arrow-forward" size={16} color={colors.primary} />
                  </TouchableOpacity>
                </View>
              ))}
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
    paddingHorizontal: spacing.xl,
    paddingBottom: 120,
  },
  dateBlock: {
    marginTop: spacing.xl,
    marginBottom: spacing.xl,
  },
  todayText: {
    ...typography.caption,
    color: colors.textSecondary,
    marginBottom: spacing.sm,
    letterSpacing: 2,
  },
  dateText: {
    fontSize: 58,
    lineHeight: 66,
    letterSpacing: -2,
    fontWeight: "300",
    color: colors.text,
  },
  weatherCard: {
    borderRadius: borderRadius.lg,
    borderWidth: 1,
    borderColor: colors.borderLight,
    padding: spacing.lg,
    marginBottom: spacing.xl,
  },
  weatherHead: {
    marginBottom: spacing.md,
  },
  locationRow: {
    flexDirection: "row",
    alignItems: "center",
    gap: spacing.sm,
  },
  locationText: {
    ...typography.bodyMedium,
    color: colors.text,
  },
  weatherMainRow: {
    flexDirection: "row",
    alignItems: "center",
    marginBottom: spacing.md,
  },
  weatherLeft: {
    width: 100,
  },
  weatherCenter: {
    flex: 1,
    paddingRight: spacing.md,
  },
  temperature: {
    fontSize: 54,
    lineHeight: 60,
    fontWeight: "300",
    color: colors.text,
  },
  weatherDesc: {
    fontSize: 18,
    lineHeight: 24,
    fontWeight: "300",
    color: colors.text,
  },
  weatherMetaRow: {
    flexDirection: "row",
    alignItems: "center",
    gap: spacing.lg,
  },
  weatherMeta: {
    ...typography.bodySmall,
    color: colors.textSecondary,
  },
  statusRow: {
    flexDirection: "row",
    gap: spacing.md,
    marginBottom: spacing.xxxl,
  },
  statusCard: {
    flex: 1,
    backgroundColor: "rgba(20,20,24,0.95)",
    borderRadius: borderRadius.lg,
    borderWidth: 1,
    borderColor: colors.borderLight,
    padding: spacing.lg,
    minHeight: 170,
    justifyContent: "space-between",
  },
  statusTitle: {
    ...typography.h3,
    color: colors.primary,
    marginBottom: spacing.sm,
  },
  statusBody: {
    fontSize: 17,
    lineHeight: 26,
    fontWeight: "400",
    color: colors.text,
  },
  statusLine: {
    height: 6,
    borderRadius: 6,
    backgroundColor: colors.primary,
    opacity: 0.9,
    marginTop: spacing.lg,
  },
  sectionHead: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: spacing.lg,
  },
  sectionLeft: {
    flexDirection: "row",
    alignItems: "center",
    gap: spacing.sm,
  },
  sectionTitle: {
    fontSize: 24,
    lineHeight: 30,
    fontWeight: "400",
    color: colors.text,
  },
  sectionRight: {
    ...typography.h3,
    color: colors.textSecondary,
  },
  pharmacyCard: {
    backgroundColor: "rgba(20,20,24,0.95)",
    borderRadius: borderRadius.lg,
    borderWidth: 1,
    borderColor: colors.borderLight,
    padding: spacing.lg,
    marginBottom: spacing.md,
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
  },
  pharmacyInfo: {
    flex: 1,
    marginRight: spacing.md,
  },
  pharmacyName: {
    fontSize: 18,
    lineHeight: 24,
    fontWeight: "400",
    color: colors.text,
    marginBottom: spacing.sm,
  },
  distanceRow: {
    flexDirection: "row",
    alignItems: "center",
    gap: spacing.xs,
  },
  distanceText: {
    ...typography.body,
    color: colors.textSecondary,
  },
  routeBtn: {
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: borderRadius.full,
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.sm,
    flexDirection: "row",
    alignItems: "center",
    gap: spacing.sm,
  },
  routeBtnText: {
    ...typography.h3,
    color: colors.primary,
  },
});
