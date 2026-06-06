import React, { useEffect, useMemo, useState } from "react";
import { ActivityIndicator, ScrollView, StyleSheet, Text, TouchableOpacity, View } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { Ionicons } from "@expo/vector-icons";
import { useNavigation } from "@react-navigation/native";
import { LinearGradient } from "expo-linear-gradient";

import { dailyDataService } from "../services/api";
import { DataStatePanel } from "../components/DataStatePanel";
import { PrayerTimes } from "../types";
import { borderRadius, colors, spacing, typography } from "../theme";
import { DataState, loadDataState } from "../utils/dataState";

const PRAYERS: Array<{ key: keyof PrayerTimes; label: string; icon: keyof typeof Ionicons.glyphMap }> = [
  { key: "fajr", label: "Sabah", icon: "moon-outline" },
  { key: "dhuhr", label: "Öğle", icon: "sunny" },
  { key: "asr", label: "İkindi", icon: "partly-sunny-outline" },
  { key: "maghrib", label: "Akşam", icon: "cloudy-night-outline" },
  { key: "isha", label: "Yatsı", icon: "moon" },
];

export function PrayerTimesScreen() {
  const navigation = useNavigation<any>();
  const [loading, setLoading] = useState(true);
  const [prayer, setPrayer] = useState<PrayerTimes | null>(null);
  const [state, setState] = useState<DataState<PrayerTimes | null> | null>(null);
  const [countdownText, setCountdownText] = useState<string>("Hesaplanıyor...");

  useEffect(() => {
    const load = async () => {
      const dataState = await loadDataState(() => dailyDataService.getPrayerTimes(), null);
      setState(dataState);
      setPrayer(dataState.data);
      setLoading(false);
    };
    void load();
  }, []);

  // Active Vakit countdown timer
  useEffect(() => {
    const timer = setInterval(() => {
      if (!prayer) return;
      
      // Find next prayer time
      let nextItem = null;
      const now = new Date();
      const nowMin = now.getHours() * 60 + now.getMinutes();
      
      for (const item of PRAYERS) {
        const val = prayer[item.key];
        if (typeof val !== "string") continue;
        const [h, m] = val.split(":");
        const pMin = Number(h) * 60 + Number(m);
        if (pMin > nowMin) {
          nextItem = { item, time: val };
          break;
        }
      }
      
      // If all passed today, next is Fajr tomorrow
      if (!nextItem) {
        nextItem = { item: PRAYERS[0], time: prayer[PRAYERS[0].key] as string };
      }
      
      const [h, m] = nextItem.time.split(":");
      const target = new Date();
      target.setHours(Number(h), Number(m), 0, 0);
      
      let diffMs = target.getTime() - now.getTime();
      if (diffMs < 0) {
        diffMs += 24 * 60 * 60 * 1000; // tomorrow
      }
      
      const totalSec = Math.floor(diffMs / 1000);
      const hours = Math.floor(totalSec / 3600);
      const minutes = Math.floor((totalSec % 3600) / 60);
      const seconds = totalSec % 60;
      
      setCountdownText(
        `${nextItem.item.label} vaktine: ${hours > 0 ? `${hours} sa ` : ""}${minutes} dk ${seconds} sn kaldı`
      );
    }, 1000);
    
    return () => clearInterval(timer);
  }, [prayer]);

  const nextPrayerKey = useMemo(() => {
    if (!prayer) return null;
    const now = new Date();
    const nowMinutes = now.getHours() * 60 + now.getMinutes();
    for (const item of PRAYERS) {
      const value = prayer[item.key];
      if (typeof value !== "string") continue;
      const [hourRaw, minuteRaw] = value.split(":");
      const hour = Number(hourRaw);
      const minute = Number(minuteRaw);
      if (Number.isFinite(hour) && Number.isFinite(minute) && hour * 60 + minute >= nowMinutes) {
        return item.key;
      }
    }
    return PRAYERS[0].key;
  }, [prayer]);

  return (
    <View style={styles.container}>
      <SafeAreaView style={styles.safeArea}>
        <View style={styles.header}>
          <TouchableOpacity style={styles.backButton} onPress={() => navigation.goBack()}>
            <Ionicons name="arrow-back" size={23} color={colors.text} />
          </TouchableOpacity>
          <View>
            <Text style={styles.headerTitle}>Namaz Vakitleri</Text>
            <Text style={styles.headerSub}>İzmir / Aliağa için 5 vakit</Text>
          </View>
          <View style={{ width: 40 }} />
        </View>

        {loading ? (
          <View style={styles.center}>
            <ActivityIndicator size="large" color={colors.primary} />
          </View>
        ) : !prayer ? (
          <View style={styles.center}>
            <DataStatePanel
              tone={state?.status === "error" ? "warning" : "info"}
              title={state?.status === "error" ? "Namaz vakti kaynağı cevap vermedi" : "Namaz vakti bekleniyor"}
              text="Veri yenilendiğinde ana ekranda sıradaki vakit adı ve saati birlikte gösterilir."
            />
          </View>
        ) : (
          <ScrollView contentContainerStyle={styles.content} showsVerticalScrollIndicator={false}>
            <View style={styles.topCard}>
              <LinearGradient
                colors={["rgba(200, 169, 110, 0.12)", "rgba(10, 10, 10, 0.5)"]}
                start={{ x: 0, y: 0 }}
                end={{ x: 1, y: 1 }}
                style={styles.topCardGradient}
              >
                <View style={styles.dialRingContainer}>
                  {/* Outer glow ring */}
                  <View style={styles.dialRingOuter}>
                    <View style={styles.dialRingInner}>
                      <Ionicons name="time" size={22} color={colors.primary} />
                      <Text style={styles.dialPrayerName}>
                        {PRAYERS.find((p) => p.key === nextPrayerKey)?.label || ""}
                      </Text>
                    </View>
                  </View>
                  <Text style={styles.dialCountdown}>{countdownText}</Text>
                </View>
              </LinearGradient>
            </View>

            <View style={styles.prayerList}>
              {PRAYERS.map((item) => {
                const active = item.key === nextPrayerKey;
                return (
                  <View key={item.key} style={[styles.prayerRow, active && styles.prayerRowActive]}>
                    <View style={styles.prayerIcon}>
                      <Ionicons name={item.icon} size={18} color={colors.primary} />
                    </View>
                    <View style={styles.prayerCopy}>
                      <Text style={styles.prayerLabel}>{item.label}</Text>
                      {active ? <Text style={styles.prayerMeta}>Sıradaki vakit</Text> : null}
                    </View>
                    <Text style={styles.prayerTime}>{(prayer?.[item.key] as string | null) || "--:--"}</Text>
                  </View>
                );
              })}
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
  center: { flex: 1, justifyContent: "center", alignItems: "center" },
  content: { padding: spacing.xl },
  prayerRow: {
    flexDirection: "row",
    alignItems: "center",
    backgroundColor: colors.surface,
    borderRadius: borderRadius.lg,
    borderWidth: 1,
    borderColor: colors.borderLight,
    padding: spacing.lg,
    marginBottom: spacing.md,
  },
  prayerRowActive: {
    borderColor: colors.primary,
    backgroundColor: "rgba(200,169,110,0.12)",
  },
  prayerIcon: {
    width: 36,
    height: 36,
    borderRadius: 18,
    backgroundColor: colors.primaryLight,
    justifyContent: "center",
    alignItems: "center",
    marginRight: spacing.md,
  },
  prayerCopy: { flex: 1 },
  prayerLabel: { ...typography.bodyMedium, color: colors.text },
  prayerMeta: { ...typography.captionSmall, color: colors.primary, marginTop: 2, textTransform: "none" },
  prayerTime: { fontSize: 24, lineHeight: 30, fontWeight: "700", color: colors.primary },
  noteCard: {
    borderRadius: borderRadius.lg,
    backgroundColor: "rgba(20,20,24,0.75)",
    borderWidth: 1,
    borderColor: colors.borderLight,
    padding: spacing.lg,
    marginTop: spacing.md,
  },
  noteTitle: { ...typography.bodyMedium, color: colors.text, marginBottom: spacing.xs },
  noteText: { ...typography.bodySmall, color: colors.textSecondary },
  topCard: {
    borderRadius: borderRadius.lg,
    overflow: "hidden",
    borderWidth: 1.2,
    borderColor: "rgba(200, 169, 110, 0.25)",
    marginBottom: spacing.lg,
  },
  topCardGradient: {
    padding: spacing.lg,
  },
  dialRingContainer: {
    alignItems: "center",
    justifyContent: "center",
    paddingVertical: spacing.md,
  },
  dialRingOuter: {
    width: 80,
    height: 80,
    borderRadius: 40,
    borderWidth: 2.5,
    borderColor: colors.primary,
    justifyContent: "center",
    alignItems: "center",
    marginBottom: spacing.md,
    shadowColor: colors.primary,
    shadowOpacity: 0.45,
    shadowRadius: 14,
    shadowOffset: { width: 0, height: 0 },
    elevation: 8,
  },
  dialRingInner: {
    width: 68,
    height: 68,
    borderRadius: 34,
    backgroundColor: "rgba(200, 169, 110, 0.10)",
    justifyContent: "center",
    alignItems: "center",
  },
  dialPrayerName: {
    ...typography.captionSmall,
    color: colors.primary,
    fontWeight: "700",
    marginTop: 2,
    textTransform: "none",
  },
  dialCountdown: {
    ...typography.bodyMedium,
    color: colors.text,
    fontWeight: "700",
    textAlign: "center",
  },
  prayerList: {
    marginBottom: spacing.xl,
  },
});
