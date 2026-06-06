import React, { useEffect, useState } from "react";
import { ActivityIndicator, ScrollView, StyleSheet, Text, TouchableOpacity, View } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { Ionicons } from "@expo/vector-icons";
import { useNavigation } from "@react-navigation/native";

import { weatherService } from "../services/api";
import { WeatherData } from "../types";
import { borderRadius, colors, spacing, typography } from "../theme";

function formatTemperature(value?: number | null): string {
  return typeof value === "number" && Number.isFinite(value) ? `${Math.round(value)}°` : "--°";
}

function formatFreshness(value?: string | null): string {
  if (!value) return "Veri bekleniyor";
  const date = new Date(value);
  if (!Number.isFinite(date.getTime())) return "Veri bekleniyor";
  return date.toLocaleString("tr-TR", {
    day: "2-digit",
    month: "short",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export function WeatherDetailScreen() {
  const navigation = useNavigation<any>();
  const [loading, setLoading] = useState(true);
  const [weather, setWeather] = useState<WeatherData | null>(null);
  const [loadError, setLoadError] = useState(false);

  useEffect(() => {
    const load = async () => {
      try {
        setWeather(await weatherService.getToday());
        setLoadError(false);
      } catch {
        setWeather(null);
        setLoadError(true);
      } finally {
        setLoading(false);
      }
    };
    void load();
  }, []);

  return (
    <View style={styles.container}>
      <SafeAreaView style={styles.safeArea}>
        <View style={styles.header}>
          <TouchableOpacity style={styles.backButton} onPress={() => navigation.goBack()}>
            <Ionicons name="arrow-back" size={23} color={colors.text} />
          </TouchableOpacity>
          <View>
            <Text style={styles.headerTitle}>Hava Durumu</Text>
            <Text style={styles.headerSub}>Aliağa günlük hava özeti</Text>
          </View>
          <View style={{ width: 40 }} />
        </View>

        {loading ? (
          <View style={styles.center}>
            <ActivityIndicator size="large" color={colors.primary} />
          </View>
        ) : (
          <ScrollView contentContainerStyle={styles.content} showsVerticalScrollIndicator={false}>
            <View style={styles.heroCard}>
              <View>
                <Text style={styles.city}>Aliağa, Merkez</Text>
                <Text style={styles.description}>{weather?.description || "Hava verisi yok"}</Text>
              </View>
              <Text style={styles.temperature}>{formatTemperature(weather?.temperature)}</Text>
            </View>

            <View style={styles.metricGrid}>
              <Metric icon="thermometer-outline" label="En düşük" value={formatTemperature(weather?.min_temp)} />
              <Metric icon="thermometer" label="En yüksek" value={formatTemperature(weather?.max_temp)} />
              <Metric icon="water-outline" label="Nem" value={weather?.humidity || "Yok"} />
              <Metric icon="flag-outline" label="Rüzgar" value={weather?.wind || "Yok"} />
            </View>

            <View style={styles.noteCard}>
              <Text style={styles.noteTitle}>{loadError ? "Veri durumu" : "Son güncelleme"}</Text>
              <Text style={styles.noteText}>
                {loadError ? "Hava durumu kaynağı cevap vermedi. Ana ekran bir sonraki yenilemede tekrar dener." : formatFreshness(weather?.fetched_at)}
              </Text>
            </View>
          </ScrollView>
        )}
      </SafeAreaView>
    </View>
  );
}

function Metric({
  icon,
  label,
  value,
}: {
  icon: keyof typeof Ionicons.glyphMap;
  label: string;
  value: string;
}) {
  return (
    <View style={styles.metricCard}>
      <Ionicons name={icon} size={17} color={colors.primary} />
      <Text style={styles.metricLabel}>{label}</Text>
      <Text style={styles.metricValue}>{value}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.background },
  safeArea: { flex: 1 },
  header: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    paddingHorizontal: spacing.xl,
    paddingVertical: spacing.md,
    borderBottomWidth: 1,
    borderBottomColor: colors.borderLight,
  },
  backButton: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: colors.surfaceLight,
    justifyContent: "center",
    alignItems: "center",
  },
  headerTitle: { ...typography.h3, color: colors.text, textAlign: "center" },
  headerSub: { ...typography.captionSmall, color: colors.textSecondary, textAlign: "center", marginTop: 2 },
  center: { flex: 1, alignItems: "center", justifyContent: "center" },
  content: { padding: spacing.xl, paddingBottom: 110 },
  heroCard: {
    minHeight: 138,
    borderRadius: borderRadius.lg,
    borderWidth: 1,
    borderColor: colors.borderLight,
    backgroundColor: "rgba(20,20,24,0.96)",
    padding: spacing.lg,
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: spacing.lg,
  },
  city: { ...typography.caption, color: colors.primary, marginBottom: spacing.sm },
  description: { ...typography.h3, color: colors.text, maxWidth: 170 },
  temperature: { fontSize: 52, lineHeight: 58, fontWeight: "300", color: colors.text },
  metricGrid: { flexDirection: "row", flexWrap: "wrap", gap: spacing.sm },
  metricCard: {
    width: "48.4%",
    minHeight: 94,
    borderRadius: borderRadius.md,
    borderWidth: 1,
    borderColor: colors.borderLight,
    backgroundColor: colors.surface,
    padding: spacing.md,
  },
  metricLabel: { ...typography.captionSmall, color: colors.textSecondary, marginTop: spacing.sm },
  metricValue: { ...typography.bodyMedium, color: colors.text, fontWeight: "700", marginTop: 2 },
  noteCard: {
    borderRadius: borderRadius.lg,
    borderWidth: 1,
    borderColor: colors.borderLight,
    backgroundColor: "rgba(20,20,24,0.75)",
    padding: spacing.lg,
    marginTop: spacing.lg,
  },
  noteTitle: { ...typography.bodyMedium, color: colors.text, marginBottom: spacing.xs },
  noteText: { ...typography.bodySmall, color: colors.textSecondary },
});
