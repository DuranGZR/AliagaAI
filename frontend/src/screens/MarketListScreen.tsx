import React, { useEffect, useMemo, useState } from "react";
import { ActivityIndicator, ScrollView, StyleSheet, Text, TouchableOpacity, View } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { Ionicons } from "@expo/vector-icons";
import { useNavigation } from "@react-navigation/native";

import { cityService } from "../services/api";
import { StreetMarket } from "../types";
import { borderRadius, colors, spacing, typography } from "../theme";
import { openDirections } from "../utils/externalActions";

const DAYS = ["pazartesi", "salı", "çarşamba", "perşembe", "cuma", "cumartesi", "pazar"];
const DAY_LABELS: Record<string, string> = {
  pazartesi: "Pazartesi",
  sali: "Salı",
  carsamba: "Çarşamba",
  persembe: "Perşembe",
  cuma: "Cuma",
  cumartesi: "Cumartesi",
  pazar: "Pazar",
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

function dayLabel(value: string): string {
  return DAY_LABELS[normalizeText(value)] || value.slice(0, 1).toLocaleUpperCase("tr-TR") + value.slice(1);
}

async function openMarketMap(market: StreetMarket) {
  await openDirections(`${market.name} ${market.address || market.neighborhood || "Aliağa"}`);
}

export function MarketListScreen() {
  const navigation = useNavigation<any>();
  const [loading, setLoading] = useState(true);
  const [markets, setMarkets] = useState<StreetMarket[]>([]);
  const [selectedDay, setSelectedDay] = useState<string | null>(null);
  const [loadError, setLoadError] = useState(false);

  useEffect(() => {
    const load = async () => {
      try {
        const data = await cityService.getMarkets(100);
        // Filter out "Helvacı Pazaryeri" (keeping only "Helvacı Kapalı Pazaryeri")
        const cleaned = data.filter((m) => {
          const norm = normalizeText(m.name);
          return !(norm.includes("helvaci") && !norm.includes("kapali"));
        });
        setMarkets(cleaned);
        setLoadError(false);
      } catch {
        setMarkets([]);
        setLoadError(true);
      } finally {
        setLoading(false);
      }
    };
    void load();
  }, []);

  const filtered = useMemo(() => {
    if (!selectedDay) return markets;
    const day = normalizeText(selectedDay);
    return markets.filter((market) => {
      const marketDays = normalizeText(market.day_of_week).split(/[\s,]+/);
      return marketDays.includes(day);
    });
  }, [markets, selectedDay]);

  return (
    <View style={styles.container}>
      <SafeAreaView style={styles.safeArea}>
        <View style={styles.header}>
          <TouchableOpacity style={styles.backButton} onPress={() => navigation.goBack()}>
            <Ionicons name="arrow-back" size={23} color={colors.text} />
          </TouchableOpacity>
          <View>
            <Text style={styles.headerTitle}>Semt Pazarları</Text>
            <Text style={styles.headerSub}>Gün, mahalle ve konum bilgisi</Text>
          </View>
          <View style={{ width: 40 }} />
        </View>

        {loading ? (
          <View style={styles.center}>
            <ActivityIndicator size="large" color={colors.primary} />
          </View>
        ) : (
          <ScrollView contentContainerStyle={styles.content} showsVerticalScrollIndicator={false}>
            <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={styles.dayRow}>
              <TouchableOpacity style={[styles.dayChip, !selectedDay && styles.dayChipActive]} onPress={() => setSelectedDay(null)}>
                <Text style={[styles.dayText, !selectedDay && styles.dayTextActive]}>Tümü</Text>
              </TouchableOpacity>
              {DAYS.map((day) => (
                <TouchableOpacity
                  key={day}
                  style={[styles.dayChip, selectedDay === day && styles.dayChipActive]}
                  onPress={() => setSelectedDay(day)}
                >
                  <Text style={[styles.dayText, selectedDay === day && styles.dayTextActive]}>{dayLabel(day)}</Text>
                </TouchableOpacity>
              ))}
            </ScrollView>

            {filtered.length === 0 ? (
              <View style={styles.emptyCard}>
                <Text style={styles.emptyTitle}>{loadError ? "Pazar verisi yenilenemedi." : "Bu gün için pazar kaydı yok."}</Text>
                <Text style={styles.emptyText}>
                  {loadError ? "Kaynak cevap vermedi. Daha sonra tekrar dene." : "Başka bir gün seçerek haftalık listeyi görebilirsin."}
                </Text>
              </View>
            ) : (
              filtered.map((market) => (
                <View key={market.id} style={styles.marketCard}>
                  <View style={styles.marketTop}>
                    <View style={styles.marketIcon}>
                      <Ionicons name="basket" size={18} color={colors.primary} />
                    </View>
                    <View style={styles.marketBody}>
                      <Text style={styles.marketDay}>{dayLabel(market.day_of_week)}</Text>
                      <Text style={styles.marketName}>{market.name}</Text>
                    </View>
                  </View>
                  <Text style={styles.marketAddress}>{market.address || market.neighborhood || "Konum bilgisi yok"}</Text>
                  {market.description ? <Text style={styles.marketDesc}>{market.description}</Text> : null}
                  <TouchableOpacity style={styles.mapButton} onPress={() => openMarketMap(market)}>
                    <Ionicons name="navigate" size={16} color={colors.background} />
                    <Text style={styles.mapButtonText}>Haritada Aç</Text>
                  </TouchableOpacity>
                </View>
              ))
            )}
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
  center: { flex: 1, alignItems: "center", justifyContent: "center" },
  content: { padding: spacing.xl, paddingBottom: 110 },
  dayRow: { gap: spacing.sm, paddingBottom: spacing.lg },
  dayChip: {
    borderRadius: borderRadius.full,
    borderWidth: 1,
    borderColor: colors.borderLight,
    backgroundColor: colors.surface,
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
  },
  dayChipActive: { borderColor: colors.primary, backgroundColor: colors.primaryLight },
  dayText: { ...typography.bodySmall, color: colors.textSecondary },
  dayTextActive: { color: colors.primary, fontWeight: "700" },
  emptyCard: {
    backgroundColor: colors.surface,
    borderRadius: borderRadius.lg,
    borderWidth: 1,
    borderColor: colors.borderLight,
    padding: spacing.lg,
  },
  emptyTitle: { ...typography.bodyMedium, color: colors.text, marginBottom: spacing.xs },
  emptyText: { ...typography.bodySmall, color: colors.textSecondary },
  marketCard: {
    backgroundColor: "rgba(20,20,24,0.96)",
    borderRadius: borderRadius.lg,
    borderWidth: 1,
    borderColor: colors.borderLight,
    padding: spacing.lg,
    marginBottom: spacing.md,
  },
  marketTop: { flexDirection: "row", alignItems: "center", marginBottom: spacing.md },
  marketIcon: {
    width: 38,
    height: 38,
    borderRadius: 19,
    backgroundColor: colors.primaryLight,
    justifyContent: "center",
    alignItems: "center",
    marginRight: spacing.md,
  },
  marketBody: { flex: 1 },
  marketDay: { ...typography.captionSmall, color: colors.primary, marginBottom: 2 },
  marketName: { ...typography.h3, color: colors.text },
  marketAddress: { ...typography.bodySmall, color: colors.textSecondary, marginBottom: spacing.sm },
  marketDesc: { ...typography.bodySmall, color: colors.textSecondary, marginBottom: spacing.md },
  mapButton: {
    alignSelf: "flex-start",
    flexDirection: "row",
    alignItems: "center",
    gap: spacing.xs,
    backgroundColor: colors.primary,
    borderRadius: borderRadius.full,
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
  },
  mapButtonText: { ...typography.bodySmall, color: colors.background, fontWeight: "700" },
});
