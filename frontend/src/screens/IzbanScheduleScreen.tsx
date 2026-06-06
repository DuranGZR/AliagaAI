import React, { useEffect, useMemo, useState, useCallback } from "react";
import {
  ActivityIndicator,
  ScrollView,
  StyleSheet,
  Text,
  TouchableOpacity,
  View,
  Platform,
} from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { Ionicons } from "@expo/vector-icons";
import { useNavigation } from "@react-navigation/native";

import { cityService } from "../services/api";
import { IzbanSchedule } from "../types";
import { borderRadius, colors, spacing, typography } from "../theme";

function formatTime(value?: string | null): string {
  if (!value) return "--:--";
  return value.slice(0, 5);
}

function formatDayType(value?: string | null): string {
  if (!value) return "Her gün";
  const norm = value.toLowerCase().trim();
  if (norm === "her_gun" || norm === "her gun" || norm === "hergun") return "Her gün";
  if (norm === "hafta_ici" || norm === "hafta ici" || norm === "haftaici") return "Hafta içi";
  if (norm === "hafta_sonu" || norm === "hafta sonu" || norm === "haftasonu") return "Hafta sonu";
  if (norm === "pazar") return "Pazar";
  return value;
}

export function IzbanScheduleScreen() {
  const navigation = useNavigation<any>();
  const [loading, setLoading] = useState(true);
  const [rows, setRows] = useState<IzbanSchedule[]>([]);
  const [loadError, setLoadError] = useState(false);
  const [activeTab, setActiveTab] = useState<"upcoming" | "all">("upcoming");
  const [nowTime, setNowTime] = useState(new Date());

  const loadData = useCallback(async () => {
    try {
      const data = await cityService.getIzbanSchedules(180);
      setRows(data);
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
    // Update current time every 30 seconds for live board calculations
    const clockTimer = setInterval(() => {
      setNowTime(new Date());
    }, 30000);
    return () => clearInterval(clockTimer);
  }, [loadData]);

  // Find the single next departure id (first departure whose time is in the future today)
  const nextId = useMemo(() => {
    const nowMins = nowTime.getHours() * 60 + nowTime.getMinutes();
    const futureRows = rows
      .filter((row) => {
        const [h, m] = (row.departure_time || "").split(":").map(Number);
        return Number.isFinite(h) && Number.isFinite(m) && h * 60 + m >= nowMins;
      })
      .sort((a, b) => {
        const [ah, am] = (a.departure_time || "").split(":").map(Number);
        const [bh, bm] = (b.departure_time || "").split(":").map(Number);
        return ah * 60 + am - (bh * 60 + bm);
      });
    return futureRows.length > 0 ? futureRows[0].id : rows[0]?.id;
  }, [rows, nowTime]);

  // Sort upcoming departures (including midnight wrap-around)
  const sortedUpcoming = useMemo(() => {
    if (!rows || rows.length === 0) return [];
    
    return [...rows]
      .map((row) => {
        const [h, m] = (row.departure_time || "").split(":").map(Number);
        const nowMins = nowTime.getHours() * 60 + nowTime.getMinutes();
        let minutesLeft = 99999;
        if (Number.isFinite(h) && Number.isFinite(m)) {
          const departureMins = h * 60 + m;
          minutesLeft = departureMins - nowMins;
          if (minutesLeft < 0) {
            minutesLeft += 1440; // Tomorrow
          }
        }
        return {
          ...row,
          minutesLeft,
        };
      })
      .sort((a, b) => a.minutesLeft - b.minutesLeft)
      .slice(0, 3);
  }, [rows, nowTime]);

  const directions = useMemo(() => {
    return Array.from(new Set(rows.map((row) => row.direction || "Tepeköy Yönü")));
  }, [rows]);

  return (
    <View style={styles.container}>
      <SafeAreaView style={styles.safeArea}>
        <View style={styles.header}>
          <TouchableOpacity style={styles.backButton} onPress={() => navigation.goBack()}>
            <Ionicons name="arrow-back" size={23} color={colors.text} />
          </TouchableOpacity>
          <View>
            <Text style={styles.headerTitle}>İZBAN Seferleri</Text>
            <Text style={styles.headerSub}>Aliağa kalkışlı günlük liste</Text>
          </View>
          <View style={{ width: 40 }} />
        </View>

        {loading ? (
          <View style={styles.center}>
            <ActivityIndicator size="large" color={colors.primary} />
          </View>
        ) : rows.length === 0 ? (
          <View style={styles.center}>
            <Text style={styles.emptyTitle}>{loadError ? "Sefer kaynağı yenilenemedi." : "Sefer verisi bulunamadı."}</Text>
            <Text style={styles.emptyText}>
              {loadError ? "İZBAN verisi için kaynak cevap vermedi. Daha sonra tekrar dene." : "Veri geldiğinde bu sayfa otomatik dolacak."}
            </Text>
          </View>
        ) : (
          <ScrollView contentContainerStyle={styles.content} showsVerticalScrollIndicator={false}>
            {/* Tab Selector */}
            <View style={styles.tabContainer}>
              <TouchableOpacity
                style={[styles.tabButton, activeTab === "upcoming" && styles.activeTabButton]}
                onPress={() => setActiveTab("upcoming")}
              >
                <Text style={[styles.tabText, activeTab === "upcoming" && styles.activeTabText]}>
                  Yaklaşan Seferler
                </Text>
              </TouchableOpacity>
              <TouchableOpacity
                style={[styles.tabButton, activeTab === "all" && styles.activeTabButton]}
                onPress={() => setActiveTab("all")}
              >
                <Text style={[styles.tabText, activeTab === "all" && styles.activeTabText]}>
                  Tüm Seferler
                </Text>
              </TouchableOpacity>
            </View>

            {activeTab === "upcoming" ? (
              <View>
                {/* Station LED Display Board */}
                <View style={styles.ledBoard}>
                  <View style={styles.ledHeader}>
                    <Text style={[styles.ledHeaderCol, { width: "22%" }]}>SAAT</Text>
                    <Text style={[styles.ledHeaderCol, { width: "53%" }]}>HEDEF / YÖN</Text>
                    <Text style={[styles.ledHeaderCol, { width: "25%", textAlign: "right" }]}>KALKIŞ</Text>
                  </View>

                  {sortedUpcoming.map((item, index) => {
                    let statusText = "";
                    if (item.minutesLeft === 0) {
                      statusText = "Kalkıyor";
                    } else if (item.minutesLeft < 60) {
                      statusText = `${item.minutesLeft} dk`;
                    } else {
                      const hrs = Math.floor(item.minutesLeft / 60);
                      const mins = item.minutesLeft % 60;
                      statusText = mins > 0 ? `${hrs}sa ${mins}dk` : `${hrs}sa`;
                    }

                    const isFirst = index === 0;

                    return (
                      <View key={item.id} style={[styles.ledRow, isFirst && styles.ledRowFirst]}>
                        <View style={styles.ledTimeCol}>
                          <Text style={[styles.ledText, styles.ledTime, isFirst && styles.ledActiveText]}>
                            {formatTime(item.departure_time)}
                          </Text>
                        </View>
                        <View style={styles.ledDestCol}>
                          <Text style={[styles.ledText, styles.ledDest, isFirst && styles.ledActiveText]} numberOfLines={1}>
                            {item.direction || "Tepeköy Yönü"}
                          </Text>
                          <Text style={styles.ledSubText}>
                            {index === 0 ? "ŞİMDİKİ SEFER" : index === 1 ? "SONRAKİ SEFER" : "3. SEFER"}
                          </Text>
                        </View>
                        <View style={styles.ledStatusCol}>
                          <Text style={[styles.ledText, styles.ledStatus, isFirst && styles.ledActiveText]}>
                            {statusText}
                          </Text>
                        </View>
                      </View>
                    );
                  })}
                </View>

                <Text style={styles.infoText}>
                  * İZBAN kalkış saatleri operasyonel nedenlerle değişiklik gösterebilir.
                </Text>
              </View>
            ) : (
              <View>
                {/* Summary Card */}
                <View style={styles.summaryCard}>
                  <Ionicons name="train" size={24} color={colors.info} />
                  <View style={styles.summaryBody}>
                    <Text style={styles.summaryTitle}>{rows.length} sefer kaydı</Text>
                    <Text style={styles.summaryText}>{directions.join(" / ")}</Text>
                  </View>
                </View>

                {/* All departures grid */}
                <View style={styles.timeGrid}>
                  {rows.map((row) => {
                    const isNext = row.id === nextId;
                    return (
                      <View key={row.id} style={[styles.timeCard, isNext && styles.nextCard]}>
                        <Text style={[styles.timeText, isNext && styles.nextTimeText]}>
                          {formatTime(row.departure_time)}
                        </Text>
                        <Text style={[styles.timeMeta, isNext && styles.nextTimeMeta]} numberOfLines={1}>
                          {isNext ? "Sıradaki" : formatDayType(row.day_type)}
                        </Text>
                      </View>
                    );
                  })}
                </View>
              </View>
            )}

            {/* Station Route Timeline */}
            <View style={styles.timelineSection}>
              <Text style={styles.timelineTitle}>İZBAN ALİAĞA GÜZERGAHI</Text>
              
              <View style={styles.timelineContainer}>
                <View style={styles.timelineLine} />

                {/* Node 1 */}
                <View style={styles.timelineNode}>
                  <View style={[styles.timelineDot, styles.timelineDotActive]} />
                  <View style={styles.timelineNodeInfo}>
                    <Text style={styles.stationName}>Aliağa İstasyonu</Text>
                    <Text style={styles.stationMeta}>Başlangıç İstasyonu · Merkez</Text>
                  </View>
                </View>

                {/* Node 2 */}
                <View style={styles.timelineNode}>
                  <View style={styles.timelineDot} />
                  <View style={styles.timelineNodeInfo}>
                    <Text style={styles.stationName}>Biçerova İstasyonu</Text>
                    <Text style={styles.stationMeta}>5.2 km · Aliağa OSB Bölgesi</Text>
                  </View>
                </View>

                {/* Node 3 */}
                <View style={styles.timelineNode}>
                  <View style={styles.timelineDot} />
                  <View style={styles.timelineNodeInfo}>
                    <Text style={styles.stationName}>Hatundere İstasyonu</Text>
                    <Text style={styles.stationMeta}>12.4 km · Menemen Bağlantısı</Text>
                  </View>
                </View>

                {/* Node 4 */}
                <View style={styles.timelineNode}>
                  <View style={styles.timelineDot} />
                  <View style={styles.timelineNodeInfo}>
                    <Text style={styles.stationName}>Menemen İstasyonu</Text>
                    <Text style={styles.stationMeta}>18.9 km · Aktarma Merkezi</Text>
                  </View>
                </View>
              </View>
            </View>
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
  center: { flex: 1, alignItems: "center", justifyContent: "center", padding: spacing.xl },
  emptyTitle: { ...typography.h3, color: colors.text, marginBottom: spacing.sm },
  emptyText: { ...typography.bodySmall, color: colors.textSecondary, textAlign: "center" },
  content: { padding: spacing.xl, paddingBottom: 110 },
  
  // Tab Selector
  tabContainer: {
    flexDirection: "row",
    backgroundColor: "rgba(255, 255, 255, 0.03)",
    borderRadius: borderRadius.md,
    padding: 4,
    marginBottom: spacing.lg,
    borderWidth: 1,
    borderColor: colors.borderLight,
  },
  tabButton: {
    flex: 1,
    paddingVertical: spacing.sm,
    alignItems: "center",
    justifyContent: "center",
    borderRadius: borderRadius.sm,
  },
  activeTabButton: {
    backgroundColor: colors.surfaceLight,
    borderWidth: 1,
    borderColor: "rgba(255, 255, 255, 0.05)",
  },
  tabText: {
    ...typography.bodyMedium,
    color: colors.textSecondary,
    fontWeight: "600",
  },
  activeTabText: {
    color: colors.primary,
    fontWeight: "700",
  },

  // Station LED Display Board
  ledBoard: {
    backgroundColor: "#0F0F11",
    borderRadius: borderRadius.lg,
    borderWidth: 1.5,
    borderColor: "#262529",
    padding: spacing.md,
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 6 },
    shadowOpacity: 0.4,
    shadowRadius: 8,
    elevation: 6,
    overflow: "hidden",
  },
  ledHeader: {
    flexDirection: "row",
    borderBottomWidth: 1,
    borderBottomColor: "#2A2A2E",
    paddingBottom: spacing.sm,
    marginBottom: spacing.sm,
  },
  ledHeaderCol: {
    color: "#807E85",
    fontSize: 10,
    fontWeight: "700",
    letterSpacing: 1,
  },
  ledRow: {
    flexDirection: "row",
    alignItems: "center",
    paddingVertical: spacing.md,
    borderBottomWidth: 1,
    borderBottomColor: "#1C1C1F",
  },
  ledRowFirst: {
    backgroundColor: "rgba(255, 184, 0, 0.02)",
  },
  ledText: {
    fontFamily: Platform.OS === "ios" ? "Courier New" : "monospace",
    color: "#E29A33", // Vintage Amber LED color
    fontWeight: "700",
  },
  ledTimeCol: {
    width: "22%",
  },
  ledTime: {
    fontSize: 18,
  },
  ledDestCol: {
    width: "53%",
  },
  ledDest: {
    fontSize: 15,
    letterSpacing: 0.5,
  },
  ledSubText: {
    fontSize: 9,
    color: "#807E85",
    fontWeight: "600",
    marginTop: 2,
    letterSpacing: 0.5,
  },
  ledStatusCol: {
    width: "25%",
    alignItems: "flex-end",
  },
  ledStatus: {
    fontSize: 15,
  },
  ledActiveText: {
    color: "#FFB800", // Brighter Amber
    textShadowColor: "rgba(255, 184, 0, 0.5)",
    textShadowOffset: { width: 0, height: 0 },
    textShadowRadius: 4,
  },
  infoText: {
    ...typography.captionSmall,
    color: colors.textTertiary,
    marginTop: spacing.md,
    fontStyle: "italic",
    textTransform: "none",
  },

  // Summary Card
  summaryCard: {
    flexDirection: "row",
    alignItems: "center",
    backgroundColor: colors.surface,
    borderRadius: borderRadius.lg,
    borderWidth: 1,
    borderColor: colors.borderLight,
    padding: spacing.lg,
    marginBottom: spacing.lg,
  },
  summaryBody: { flex: 1, marginLeft: spacing.md },
  summaryTitle: { ...typography.bodyMedium, color: colors.text },
  summaryText: { ...typography.bodySmall, color: colors.textSecondary, marginTop: 2 },
  
  // Grid times
  timeGrid: { flexDirection: "row", flexWrap: "wrap", gap: spacing.sm },
  timeCard: {
    width: "31.8%",
    minHeight: 70,
    justifyContent: "center",
    alignItems: "center",
    backgroundColor: "rgba(20,20,24,0.96)",
    borderRadius: borderRadius.md,
    borderWidth: 1,
    borderColor: colors.borderLight,
  },
  nextCard: {
    borderColor: colors.primary,
    backgroundColor: colors.primaryLight,
  },
  timeText: { fontSize: 18, lineHeight: 24, fontWeight: "700", color: colors.text },
  nextTimeText: { color: colors.primary },
  timeMeta: { ...typography.captionSmall, color: colors.textSecondary, marginTop: 2 },
  nextTimeMeta: { color: colors.primary, fontWeight: "600" },

  // Timeline
  timelineSection: {
    marginTop: spacing.xxl,
    borderTopWidth: 1,
    borderTopColor: colors.borderLight,
    paddingTop: spacing.xl,
  },
  timelineTitle: {
    ...typography.caption,
    color: colors.primary,
    marginBottom: spacing.lg,
    fontWeight: "700",
  },
  timelineContainer: {
    position: "relative",
    paddingLeft: spacing.lg,
  },
  timelineLine: {
    position: "absolute",
    left: 4,
    top: 6,
    bottom: 24,
    width: 2,
    backgroundColor: "rgba(200, 169, 110, 0.25)",
  },
  timelineNode: {
    flexDirection: "row",
    alignItems: "flex-start",
    marginBottom: spacing.lg,
    position: "relative",
  },
  timelineDot: {
    position: "absolute",
    left: -20,
    top: 4,
    width: 10,
    height: 10,
    borderRadius: 5,
    backgroundColor: colors.border,
    borderWidth: 2,
    borderColor: colors.background,
  },
  timelineDotActive: {
    backgroundColor: colors.primary,
    borderColor: colors.background,
    shadowColor: colors.primary,
    shadowOffset: { width: 0, height: 0 },
    shadowOpacity: 0.8,
    shadowRadius: 4,
  },
  timelineNodeInfo: {
    marginLeft: spacing.sm,
  },
  stationName: {
    ...typography.bodyMedium,
    color: colors.text,
  },
  stationMeta: {
    ...typography.captionSmall,
    color: colors.textSecondary,
    textTransform: "none",
    marginTop: 2,
  },
});
