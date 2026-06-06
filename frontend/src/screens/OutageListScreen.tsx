import React, { useEffect, useMemo, useState, useCallback } from "react";
import { ActivityIndicator, ScrollView, StyleSheet, Text, TouchableOpacity, View } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { Ionicons } from "@expo/vector-icons";
import { useNavigation } from "@react-navigation/native";

import { cityService } from "../services/api";
import { UtilityOutage } from "../types";
import { borderRadius, colors, spacing, typography } from "../theme";

function formatDateTime(value?: string | null): string {
  if (!value) return "Belirsiz";
  const date = new Date(value);
  if (!Number.isFinite(date.getTime())) return "Belirsiz";
  return date.toLocaleString("tr-TR", {
    day: "2-digit",
    month: "short",
    hour: "2-digit",
    minute: "2-digit",
  });
}

function getOutageStatus(row: UtilityOutage): "ongoing" | "upcoming" | "completed" {
  const now = new Date();
  const start = row.start_date ? new Date(row.start_date) : null;
  const end = row.end_date ? new Date(row.end_date) : null;

  if (start && start > now) {
    return "upcoming";
  }
  if (end && end < now) {
    return "completed";
  }
  return "ongoing";
}

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

function cleanDescription(type: string, desc?: string | null): { reason: string; affected: string; duration: string } {
  const text = desc || "";
  let reason = "";
  let affected = "";
  let duration = "";

  const isWater = (type || "").toLowerCase().includes("su");

  if (isWater) {
    // İZSU format
    const parts = text.split(/kurum\s+açıklaması\s*:/i);
    const mainText = parts[1] || text;
    
    const reasonPart = mainText.split(/ilçe|su\s+kesintisinin|etkilenen/i)[0];
    reason = reasonPart ? reasonPart.replace(/[-–\s]+$/, "").trim() : "";

    const durationMatch = text.match(/suresi\s*:\s*([^]+?)(?=etkilenen|$)/i) || text.match(/süresi\s*:\s*([^]+?)(?=etkilenen|$)/i) || text.match(/(\d+\s*saat)/i);
    duration = durationMatch ? durationMatch[1].trim() : "";

    const affectedMatch = text.match(/etkilenen\s+yerleşimler\s*:\s*([^]+?)(?=arıza|$)/i) || text.match(/kesintiden\s+etkilenen\s+yerler\s*:\s*([^]+?)$/i);
    affected = affectedMatch ? affectedMatch[1].trim() : "";
  } else {
    // GDZ Elektrik format
    const parts = text.split(/kesinti\s+açıklaması\s*:/i);
    const mainText = parts[1] || text;

    const reasonPart = mainText.split(/hesaplanan|süre|başlangıç|il\s+ismi/i)[0];
    reason = reasonPart ? reasonPart.replace(/[-–\s]+$/, "").trim() : "";

    const durationMatch = text.match(/ne\s+kadar\s*\?\s*:\s*([^]+?)(?=elektrik|başlangıç|$)/i) || text.match(/(\d+\s*saat)/i);
    duration = durationMatch ? durationMatch[1].trim() : "";

    // Extract mahalle list if possible
    const mahalleMatches = text.match(/([A-ZÇĞİÖŞÜa-zçğıöşü]+\s*Mah\.)/gi) || text.match(/([A-ZÇĞİÖŞÜa-zçğıöşü]+\s*Mahallesi)/gi);
    if (mahalleMatches) {
      affected = Array.from(new Set(mahalleMatches)).join(", ");
    }
  }

  // Fallbacks
  if (!reason) {
    reason = text.length > 100 ? text.substring(0, 100) + "..." : text;
  }
  if (!duration) {
    const durationAlt = text.match(/(\d+\s*(?:saat|dakika|gun))/i);
    duration = durationAlt ? durationAlt[1] : "Belirtilmemiş";
  }
  if (!affected) {
    const mahalleMatches = text.match(/([A-ZÇĞİÖŞÜa-zçğıöşü]+\s*Mah\.)/gi) || text.match(/([A-ZÇĞİÖŞÜa-zçğıöşü]+\s*Mahallesi)/gi);
    affected = mahalleMatches ? Array.from(new Set(mahalleMatches)).join(", ") : "Aliağa Merkez";
  }

  // Formatting cleanup
  reason = reason.charAt(0).toUpperCase() + reason.slice(1);
  reason = reason.replace(/[\s,.-]+$/, "").trim();
  affected = affected.replace(/[\s,.-]+$/, "").trim();
  duration = duration.replace(/[\s,.-]+$/, "").trim();

  // If reason is just a date prefix, strip it
  reason = reason.replace(/^\d+\s+[A-Za-zĞİÖŞÜçğıöşü]+\s+\d+\s+[^:]+Kesintisi\s*/gi, "").trim();
  reason = reason.charAt(0).toUpperCase() + reason.slice(1);

  return { reason, affected, duration };
}

export function OutageListScreen() {
  const navigation = useNavigation<any>();
  const [loading, setLoading] = useState(true);
  const [rows, setRows] = useState<UtilityOutage[]>([]);
  const [loadError, setLoadError] = useState(false);

  const loadData = useCallback(async () => {
    try {
      setRows(await cityService.getOutages(80));
      setLoadError(false);
    } catch {
      setRows([]);
      setLoadError(true);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void loadData();
  }, [loadData]);

  const ongoingOutages = useMemo(() => rows.filter(r => getOutageStatus(r) === "ongoing"), [rows]);
  const upcomingOutages = useMemo(() => rows.filter(r => getOutageStatus(r) === "upcoming"), [rows]);
  const completedOutages = useMemo(() => rows.filter(r => getOutageStatus(r) === "completed"), [rows]);

  // Sort: ongoing first, then upcoming, then completed
  const sortedOutages = useMemo(() => {
    return [...ongoingOutages, ...upcomingOutages, ...completedOutages];
  }, [ongoingOutages, upcomingOutages, completedOutages]);

  return (
    <View style={styles.container}>
      <SafeAreaView style={styles.safeArea}>
        <View style={styles.header}>
          <TouchableOpacity style={styles.backButton} onPress={() => navigation.goBack()}>
            <Ionicons name="arrow-back" size={23} color={colors.text} />
          </TouchableOpacity>
          <View>
            <Text style={styles.headerTitle}>Kesinti Uyarıları</Text>
            <Text style={styles.headerSub}>Su ve elektrik kayıtları</Text>
          </View>
          <View style={{ width: 40 }} />
        </View>

        {loading ? (
          <View style={styles.center}>
            <ActivityIndicator size="large" color={colors.primary} />
          </View>
        ) : sortedOutages.length === 0 ? (
          <View style={styles.center}>
            <Text style={styles.emptyTitle}>{loadError ? "Kesinti kaynağı yenilenemedi." : "Kesinti kaydı yok."}</Text>
            <Text style={styles.emptyText}>
              {loadError ? "Su ve elektrik kesinti kaynağı cevap vermedi." : "Aktif veya geçmiş kesinti verisi bulunamadı."}
            </Text>
          </View>
        ) : (
          <ScrollView contentContainerStyle={styles.content} showsVerticalScrollIndicator={false}>
            {sortedOutages.map((row) => {
              const status = getOutageStatus(row);
              const isWater = (row.type || "").toLowerCase().includes("su");
              const { reason, affected, duration } = cleanDescription(row.type || "altyapı", row.description);

              return (
                <View
                  key={row.id}
                  style={[
                    styles.outageCard,
                    isWater ? styles.waterCard : styles.electricityCard,
                    status === "completed" && styles.completedCard,
                  ]}
                >
                  {/* Top Header Row */}
                  <View style={styles.cardHeader}>
                    <View style={styles.typeBadge}>
                      <Ionicons
                        name={isWater ? "water" : "flash"}
                        size={16}
                        color={isWater ? "#3498db" : "#f1c40f"}
                      />
                      <Text style={[styles.typeText, isWater ? styles.waterText : styles.electricityText]}>
                        {isWater ? "Su Kesintisi" : "Elektrik Kesintisi"}
                      </Text>
                    </View>

                    {/* Status Badge */}
                    <View
                      style={[
                        styles.statusBadge,
                        status === "ongoing" && styles.statusOngoing,
                        status === "upcoming" && styles.statusUpcoming,
                        status === "completed" && styles.statusCompleted,
                      ]}
                    >
                      <Text
                        style={[
                          styles.statusText,
                          status === "ongoing" && styles.textOngoing,
                          status === "upcoming" && styles.textUpcoming,
                          status === "completed" && styles.textCompleted,
                        ]}
                      >
                        {status === "ongoing" ? "SÜRÜYOR" : status === "upcoming" ? "PLANLI" : "SONA ERDİ"}
                      </Text>
                    </View>
                  </View>

                  {/* Reason / Title */}
                  <Text style={styles.outageReason}>{reason}</Text>

                  {/* Details block */}
                  <View style={styles.detailsBlock}>
                    {/* Affected neighborhood */}
                    <View style={styles.detailItem}>
                      <Ionicons name="location-outline" size={15} color={colors.textTertiary} />
                      <Text style={styles.detailText} numberOfLines={2}>
                        <Text style={styles.detailLabel}>Etkilenen: </Text>
                        {affected || row.neighborhood || "Aliağa Merkez"}
                      </Text>
                    </View>

                    {/* Duration */}
                    <View style={styles.detailItem}>
                      <Ionicons name="time-outline" size={15} color={colors.textTertiary} />
                      <Text style={styles.detailText}>
                        <Text style={styles.detailLabel}>Tahmini Süre: </Text>
                        {duration}
                      </Text>
                    </View>
                  </View>

                  {/* Horizontal Timeline Line */}
                  <View style={styles.timelineRow}>
                    <View style={styles.timelinePoint}>
                      <Text style={styles.timelineTime}>{formatDateTime(row.start_date)}</Text>
                      <Text style={styles.timelineLabel}>Başlangıç</Text>
                    </View>
                    <View style={styles.timelineConnector} />
                    <View style={[styles.timelinePoint, { alignItems: "flex-end" }]}>
                      <Text style={styles.timelineTime}>{formatDateTime(row.end_date)}</Text>
                      <Text style={styles.timelineLabel}>Planlanan Bitiş</Text>
                    </View>
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
  center: { flex: 1, justifyContent: "center", alignItems: "center", padding: spacing.xl },
  emptyTitle: { ...typography.h3, color: colors.text, marginBottom: spacing.sm },
  emptyText: { ...typography.bodySmall, color: colors.textSecondary, textAlign: "center" },
  content: { padding: spacing.xl, paddingBottom: 110 },

  // Outage Cards
  outageCard: {
    backgroundColor: "rgba(20, 20, 24, 0.96)",
    borderRadius: borderRadius.lg,
    borderWidth: 1,
    padding: spacing.lg,
    marginBottom: spacing.md,
  },
  electricityCard: {
    borderColor: "rgba(241, 196, 15, 0.15)",
    backgroundColor: "rgba(241, 196, 15, 0.02)",
  },
  waterCard: {
    borderColor: "rgba(52, 152, 219, 0.15)",
    backgroundColor: "rgba(52, 152, 219, 0.02)",
  },
  completedCard: {
    borderColor: colors.borderLight,
    backgroundColor: colors.surface,
    opacity: 0.7,
  },

  // Card Header
  cardHeader: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: spacing.md,
  },
  typeBadge: {
    flexDirection: "row",
    alignItems: "center",
    gap: 4,
  },
  typeText: {
    ...typography.caption,
    fontWeight: "700",
    letterSpacing: 0.5,
  },
  electricityText: {
    color: "#f1c40f",
  },
  waterText: {
    color: "#3498db",
  },

  // Status Badge
  statusBadge: {
    paddingHorizontal: spacing.sm,
    paddingVertical: 3,
    borderRadius: 4,
  },
  statusOngoing: {
    backgroundColor: "rgba(231, 76, 60, 0.12)",
  },
  statusUpcoming: {
    backgroundColor: "rgba(241, 196, 15, 0.12)",
  },
  statusCompleted: {
    backgroundColor: "rgba(255, 255, 255, 0.08)",
  },
  statusText: {
    fontSize: 9,
    fontWeight: "700",
    letterSpacing: 0.5,
  },
  textOngoing: {
    color: "#e74c3c",
  },
  textUpcoming: {
    color: "#f1c40f",
  },
  textCompleted: {
    color: colors.textSecondary,
  },

  // Reason & details
  outageReason: {
    ...typography.bodyMedium,
    color: colors.text,
    fontWeight: "600",
    marginBottom: spacing.md,
    lineHeight: 22,
  },
  detailsBlock: {
    backgroundColor: "rgba(255, 255, 255, 0.02)",
    borderRadius: borderRadius.md,
    padding: spacing.md,
    gap: spacing.sm,
    marginBottom: spacing.md,
  },
  detailItem: {
    flexDirection: "row",
    alignItems: "flex-start",
    gap: spacing.sm,
  },
  detailLabel: {
    fontWeight: "600",
    color: colors.textSecondary,
  },
  detailText: {
    ...typography.bodySmall,
    color: colors.text,
    flex: 1,
    lineHeight: 18,
  },

  // Timeline Row
  timelineRow: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    borderTopWidth: 1,
    borderTopColor: "rgba(255, 255, 255, 0.05)",
    paddingTop: spacing.md,
    marginTop: 4,
  },
  timelinePoint: {
    flex: 1,
  },
  timelineTime: {
    ...typography.bodySmall,
    fontWeight: "700",
    color: colors.text,
  },
  timelineLabel: {
    ...typography.captionSmall,
    color: colors.textTertiary,
    marginTop: 2,
    textTransform: "none",
  },
  timelineConnector: {
    width: 24,
    height: 1,
    backgroundColor: "rgba(255, 255, 255, 0.1)",
    marginHorizontal: spacing.sm,
  },
});
