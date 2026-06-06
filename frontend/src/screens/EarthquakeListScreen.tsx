import React, { useEffect, useMemo, useState } from "react";
import { ActivityIndicator, ScrollView, StyleSheet, Text, TouchableOpacity, View } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { Ionicons } from "@expo/vector-icons";
import { useNavigation } from "@react-navigation/native";

import { dailyDataService } from "../services/api";
import { Earthquake } from "../types";
import { borderRadius, colors, spacing, typography } from "../theme";

/* ── Aliağa merkez koordinatları ── */
const ALIAGA_LAT = 38.7997;
const ALIAGA_LON = 26.9691;
const PROXIMITY_KM = 100;

/* ── Haversine mesafe hesaplama (km) ── */
function getDistanceKm(lat1: number, lon1: number, lat2: number, lon2: number): number {
  const R = 6371;
  const dLat = ((lat2 - lat1) * Math.PI) / 180;
  const dLon = ((lon2 - lon1) * Math.PI) / 180;
  const a =
    Math.sin(dLat / 2) ** 2 +
    Math.cos((lat1 * Math.PI) / 180) * Math.cos((lat2 * Math.PI) / 180) * Math.sin(dLon / 2) ** 2;
  return R * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
}

/* ── Büyüklük renk skalası ── */
function getMagnitudeColors(mag: number | null | undefined): { bg: string; text: string; border: string } {
  const m = typeof mag === "number" && Number.isFinite(mag) ? mag : 0;
  if (m >= 5.0) return { bg: "rgba(220, 60, 60, 0.22)", text: "#E85454", border: "rgba(220, 60, 60, 0.45)" };
  if (m >= 4.0) return { bg: "rgba(230, 140, 40, 0.22)", text: "#E8943A", border: "rgba(230, 140, 40, 0.40)" };
  if (m >= 3.0) return { bg: "rgba(200, 169, 110, 0.20)", text: colors.primary, border: "rgba(200, 169, 110, 0.40)" };
  return { bg: "rgba(120, 160, 120, 0.18)", text: "#8CB88C", border: "rgba(120, 160, 120, 0.32)" };
}

function formatDateTime(value?: string | null): string {
  if (!value) return "Zaman bilgisi yok";
  const date = new Date(value);
  if (!Number.isFinite(date.getTime())) return "Zaman bilgisi yok";
  return date.toLocaleString("tr-TR", {
    day: "2-digit",
    month: "short",
    hour: "2-digit",
    minute: "2-digit",
  });
}

function formatDepth(value?: number | null): string {
  return typeof value === "number" && Number.isFinite(value) ? `${value.toFixed(1)} km` : "Yok";
}

function formatMagnitude(value?: number | null): string {
  return typeof value === "number" && Number.isFinite(value) ? value.toFixed(1) : "--";
}

export function EarthquakeListScreen() {
  const navigation = useNavigation<any>();
  const [loading, setLoading] = useState(true);
  const [rows, setRows] = useState<Earthquake[]>([]);
  const [loadError, setLoadError] = useState(false);

  useEffect(() => {
    const load = async () => {
      try {
        setRows(await dailyDataService.getEarthquakes());
        setLoadError(false);
      } catch {
        setRows([]);
        setLoadError(true);
      } finally {
        setLoading(false);
      }
    };
    void load();
  }, []);

  /* ── Proximity hesaplama: her deprem için mesafe ── */
  const enrichedRows = useMemo(() => {
    return rows.map((row) => {
      const dist =
        typeof row.latitude === "number" && typeof row.longitude === "number"
          ? getDistanceKm(ALIAGA_LAT, ALIAGA_LON, row.latitude, row.longitude)
          : null;
      return { ...row, distanceKm: dist, isNearby: dist !== null && dist <= PROXIMITY_KM };
    });
  }, [rows]);

  const nearbyCount = useMemo(() => enrichedRows.filter((r) => r.isNearby).length, [enrichedRows]);

  return (
    <View style={styles.container}>
      <SafeAreaView style={styles.safeArea}>
        <View style={styles.header}>
          <TouchableOpacity style={styles.backButton} onPress={() => navigation.goBack()}>
            <Ionicons name="arrow-back" size={23} color={colors.text} />
          </TouchableOpacity>
          <View>
            <Text style={styles.headerTitle}>Deprem Bilgileri</Text>
            <Text style={styles.headerSub}>Son kayıtlar ve detaylar</Text>
          </View>
          <View style={{ width: 40 }} />
        </View>

        {loading ? (
          <View style={styles.center}>
            <ActivityIndicator size="large" color={colors.primary} />
          </View>
        ) : rows.length === 0 ? (
          <View style={styles.center}>
            <Text style={styles.emptyTitle}>{loadError ? "Deprem kaynağı yenilenemedi." : "Deprem kaydı yok."}</Text>
            <Text style={styles.emptyText}>
              {loadError ? "Kaynak cevap vermedi. Daha sonra tekrar dene." : "Kaynak güncellendiğinde bu sayfa otomatik dolacak."}
            </Text>
          </View>
        ) : (
          <ScrollView contentContainerStyle={styles.content} showsVerticalScrollIndicator={false}>
            {/* ── Proximity alert banner ── */}
            {nearbyCount > 0 && (
              <View style={styles.alertBanner}>
                <View style={styles.alertIconWrap}>
                  <Ionicons name="warning" size={20} color="#E85454" />
                </View>
                <View style={{ flex: 1 }}>
                  <Text style={styles.alertTitle}>
                    Yakın Sarsıntı Uyarısı
                  </Text>
                  <Text style={styles.alertText}>
                    Son kayıtlarda Aliağa'ya {PROXIMITY_KM} km veya daha yakın {nearbyCount} deprem tespit edildi.
                  </Text>
                </View>
              </View>
            )}

            {enrichedRows.map((row) => {
              const magColors = getMagnitudeColors(row.magnitude);
              return (
                <View
                  key={row.id}
                  style={[
                    styles.earthquakeCard,
                    row.isNearby && styles.nearbyCard,
                  ]}
                >
                  <View style={styles.cardTop}>
                    <View
                      style={[
                        styles.magnitudeBadge,
                        { backgroundColor: magColors.bg, borderColor: magColors.border, borderWidth: 1.5 },
                      ]}
                    >
                      <Text style={[styles.magnitudeText, { color: magColors.text }]}>
                        {formatMagnitude(row.magnitude)}
                      </Text>
                    </View>
                    <View style={styles.cardBody}>
                      <Text style={styles.location}>{row.location || "Konum bilgisi yok"}</Text>
                      <Text style={styles.time}>{formatDateTime(row.event_date)}</Text>
                    </View>
                  </View>

                  {/* ── Proximity etiketi ── */}
                  {row.isNearby && row.distanceKm !== null && (
                    <View style={styles.proximityTag}>
                      <Ionicons name="locate" size={13} color="#E85454" />
                      <Text style={styles.proximityText}>
                        Aliağa'ya {row.distanceKm.toFixed(0)} km — Yakın sarsıntı bölgesi
                      </Text>
                    </View>
                  )}

                  <View style={styles.metaRow}>
                    <Meta icon="analytics-outline" label="Derinlik" value={formatDepth(row.depth)} />
                    <Meta icon="radio-outline" label="Kaynak" value={row.source || "Bilinmiyor"} />
                    {row.distanceKm !== null && (
                      <Meta icon="navigate-outline" label="Mesafe" value={`${row.distanceKm.toFixed(0)} km`} />
                    )}
                  </View>
                </View>
              );
            })}
          </ScrollView>
        )}
      </SafeAreaView>
    </View>
  );
}

function Meta({
  icon,
  label,
  value,
}: {
  icon: keyof typeof Ionicons.glyphMap;
  label: string;
  value: string;
}) {
  return (
    <View style={styles.metaItem}>
      <Ionicons name={icon} size={15} color={colors.textTertiary} />
      <Text style={styles.metaLabel}>{label}</Text>
      <Text style={styles.metaValue}>{value}</Text>
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
  center: { flex: 1, alignItems: "center", justifyContent: "center", padding: spacing.xl },
  emptyTitle: { ...typography.h3, color: colors.text, marginBottom: spacing.sm },
  emptyText: { ...typography.bodySmall, color: colors.textSecondary, textAlign: "center" },
  content: { padding: spacing.xl, paddingBottom: 110 },

  /* ── Alert banner ── */
  alertBanner: {
    flexDirection: "row",
    alignItems: "center",
    backgroundColor: "rgba(220, 60, 60, 0.12)",
    borderWidth: 1,
    borderColor: "rgba(220, 60, 60, 0.35)",
    borderRadius: borderRadius.lg,
    padding: spacing.lg,
    marginBottom: spacing.lg,
    gap: spacing.md,
  },
  alertIconWrap: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: "rgba(220, 60, 60, 0.18)",
    justifyContent: "center",
    alignItems: "center",
  },
  alertTitle: {
    ...typography.bodyMedium,
    color: "#E85454",
    fontWeight: "800",
    marginBottom: 2,
  },
  alertText: {
    ...typography.captionSmall,
    color: "rgba(232, 84, 84, 0.8)",
    textTransform: "none",
  },

  /* ── Card ── */
  earthquakeCard: {
    borderRadius: borderRadius.lg,
    borderWidth: 1,
    borderColor: colors.borderLight,
    backgroundColor: "rgba(20,20,24,0.96)",
    padding: spacing.lg,
    marginBottom: spacing.md,
  },
  nearbyCard: {
    borderColor: "rgba(220, 60, 60, 0.40)",
    backgroundColor: "rgba(220, 60, 60, 0.06)",
  },
  cardTop: { flexDirection: "row", alignItems: "center", marginBottom: spacing.md },
  magnitudeBadge: {
    width: 46,
    height: 46,
    borderRadius: 23,
    justifyContent: "center",
    alignItems: "center",
    marginRight: spacing.md,
  },
  magnitudeText: { ...typography.bodyMedium, fontWeight: "800" },
  cardBody: { flex: 1 },
  location: { ...typography.bodyMedium, color: colors.text, fontWeight: "700" },
  time: { ...typography.bodySmall, color: colors.textSecondary, marginTop: 2 },

  /* ── Proximity tag ── */
  proximityTag: {
    flexDirection: "row",
    alignItems: "center",
    gap: spacing.xs,
    backgroundColor: "rgba(220, 60, 60, 0.10)",
    borderRadius: borderRadius.sm,
    paddingHorizontal: spacing.sm,
    paddingVertical: spacing.xs,
    marginBottom: spacing.md,
    alignSelf: "flex-start",
  },
  proximityText: {
    ...typography.captionSmall,
    color: "#E85454",
    fontWeight: "700",
    textTransform: "none",
  },

  /* ── Meta row ── */
  metaRow: { flexDirection: "row", gap: spacing.sm },
  metaItem: {
    flex: 1,
    borderRadius: borderRadius.md,
    backgroundColor: "rgba(255,255,255,0.035)",
    borderWidth: 1,
    borderColor: colors.borderLight,
    padding: spacing.sm,
  },
  metaLabel: { ...typography.captionSmall, color: colors.textSecondary, marginTop: spacing.xs },
  metaValue: { ...typography.bodySmall, color: colors.text, fontWeight: "700", marginTop: 2 },
});
