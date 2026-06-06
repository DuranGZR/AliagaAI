import React, { useEffect, useMemo, useState } from "react";
import { ActivityIndicator, ScrollView, StyleSheet, Text, TouchableOpacity, View } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { Ionicons } from "@expo/vector-icons";
import { useNavigation } from "@react-navigation/native";

import { dailyDataService } from "../services/api";
import { CurrencyRate, FuelPrices, GoldPrice } from "../types";
import { borderRadius, colors, spacing, typography } from "../theme";

function formatMoney(value?: number | null): string {
  return typeof value === "number" && Number.isFinite(value) ? `${value.toFixed(2)} TL` : "Yok";
}

function formatChange(value?: number | null): string {
  if (typeof value !== "number" || !Number.isFinite(value)) return "";
  const sign = value > 0 ? "+" : "";
  return `${sign}${value.toFixed(2)}%`;
}

function firstCurrency(currencies: CurrencyRate[], code: string): CurrencyRate | undefined {
  return currencies.find((item) => item.code?.toLocaleUpperCase("tr-TR") === code);
}

export function MarketRatesScreen() {
  const navigation = useNavigation<any>();
  const [loading, setLoading] = useState(true);
  const [fuel, setFuel] = useState<FuelPrices | null>(null);
  const [currencies, setCurrencies] = useState<CurrencyRate[]>([]);
  const [golds, setGolds] = useState<GoldPrice[]>([]);
  const [loadError, setLoadError] = useState(false);

  useEffect(() => {
    const load = async () => {
      try {
        const [fuelData, currencyData, goldData] = await Promise.all([
          dailyDataService.getFuelPrices(),
          dailyDataService.getCurrency(),
          dailyDataService.getGold(),
        ]);
        setFuel(fuelData);
        setCurrencies(currencyData);
        setGolds(goldData);
        setLoadError(false);
      } catch {
        setFuel(null);
        setCurrencies([]);
        setGolds([]);
        setLoadError(true);
      } finally {
        setLoading(false);
      }
    };
    void load();
  }, []);

  const usd = useMemo(() => firstCurrency(currencies, "USD"), [currencies]);
  const eur = useMemo(() => firstCurrency(currencies, "EUR"), [currencies]);
  const visibleGolds = golds.slice(0, 6);

  return (
    <View style={styles.container}>
      <SafeAreaView style={styles.safeArea}>
        <View style={styles.header}>
          <TouchableOpacity style={styles.backButton} onPress={() => navigation.goBack()}>
            <Ionicons name="arrow-back" size={23} color={colors.text} />
          </TouchableOpacity>
          <View>
            <Text style={styles.headerTitle}>Piyasa Bilgileri</Text>
            <Text style={styles.headerSub}>Yakıt, döviz ve altın</Text>
          </View>
          <View style={{ width: 40 }} />
        </View>

        {loading ? (
          <View style={styles.center}>
            <ActivityIndicator size="large" color={colors.primary} />
          </View>
        ) : (
          <ScrollView contentContainerStyle={styles.content} showsVerticalScrollIndicator={false}>
            {loadError ? (
              <View style={styles.emptyCard}>
                <Text style={styles.emptyText}>Piyasa kaynakları yenilenemedi. Daha sonra tekrar dene.</Text>
              </View>
            ) : null}
            <View style={styles.quickGrid}>
              <QuickRate icon="car-outline" label="Benzin" value={formatMoney(fuel?.gasoline)} />
              <QuickRate icon="bus-outline" label="Dizel" value={formatMoney(fuel?.diesel)} />
              <QuickRate icon="trending-up-outline" label="USD" value={formatMoney(usd?.selling || usd?.buying)} />
              <QuickRate icon="diamond-outline" label="Gram" value={formatMoney(visibleGolds[0]?.selling || visibleGolds[0]?.buying)} />
            </View>

            <SectionTitle title="Döviz" />
            <RateRow title="USD" subtitle={usd?.name || "Amerikan Doları"} value={formatMoney(usd?.selling || usd?.buying)} meta={formatChange(usd?.change_pct)} />
            <RateRow title="EUR" subtitle={eur?.name || "Euro"} value={formatMoney(eur?.selling || eur?.buying)} meta={formatChange(eur?.change_pct)} />

            <SectionTitle title="Altın" />
            {visibleGolds.length === 0 ? (
              <View style={styles.emptyCard}>
                <Text style={styles.emptyText}>Altın verisi bulunamadı.</Text>
              </View>
            ) : (
              visibleGolds.map((item) => (
                <RateRow
                  key={item.id}
                  title={item.name}
                  subtitle="Satış / alış verisi"
                  value={formatMoney(item.selling || item.buying)}
                  meta={formatChange(item.change_pct)}
                />
              ))
            )}
          </ScrollView>
        )}
      </SafeAreaView>
    </View>
  );
}

function QuickRate({
  icon,
  label,
  value,
}: {
  icon: keyof typeof Ionicons.glyphMap;
  label: string;
  value: string;
}) {
  return (
    <View style={styles.quickCard}>
      <Ionicons name={icon} size={17} color={colors.primary} />
      <Text style={styles.quickLabel}>{label}</Text>
      <Text style={styles.quickValue}>{value}</Text>
    </View>
  );
}

function SectionTitle({ title }: { title: string }) {
  return <Text style={styles.sectionTitle}>{title}</Text>;
}

function RateRow({ title, subtitle, value, meta }: { title: string; subtitle: string; value: string; meta?: string }) {
  return (
    <View style={styles.rateRow}>
      <View style={styles.rateBody}>
        <Text style={styles.rateTitle}>{title}</Text>
        <Text style={styles.rateSubtitle}>{subtitle}</Text>
      </View>
      <View style={styles.rateRight}>
        <Text style={styles.rateValue}>{value}</Text>
        {meta ? <Text style={styles.rateMeta}>{meta}</Text> : null}
      </View>
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
  quickGrid: { flexDirection: "row", flexWrap: "wrap", gap: spacing.sm, marginBottom: spacing.lg },
  quickCard: {
    width: "48.4%",
    minHeight: 92,
    borderRadius: borderRadius.md,
    borderWidth: 1,
    borderColor: colors.borderLight,
    backgroundColor: colors.surface,
    padding: spacing.md,
  },
  quickLabel: { ...typography.captionSmall, color: colors.textSecondary, marginTop: spacing.sm },
  quickValue: { ...typography.bodyMedium, color: colors.text, fontWeight: "700", marginTop: 2 },
  sectionTitle: { ...typography.caption, color: colors.primary, letterSpacing: 1.4, marginTop: spacing.md, marginBottom: spacing.sm },
  rateRow: {
    flexDirection: "row",
    alignItems: "center",
    borderRadius: borderRadius.lg,
    borderWidth: 1,
    borderColor: colors.borderLight,
    backgroundColor: "rgba(20,20,24,0.96)",
    padding: spacing.lg,
    marginBottom: spacing.sm,
  },
  rateBody: { flex: 1, paddingRight: spacing.md },
  rateTitle: { ...typography.bodyMedium, color: colors.text, fontWeight: "700" },
  rateSubtitle: { ...typography.bodySmall, color: colors.textSecondary, marginTop: 2 },
  rateRight: { alignItems: "flex-end" },
  rateValue: { ...typography.bodyMedium, color: colors.text, fontWeight: "700" },
  rateMeta: { ...typography.captionSmall, color: colors.primary, marginTop: 2 },
  emptyCard: {
    borderRadius: borderRadius.lg,
    borderWidth: 1,
    borderColor: colors.borderLight,
    backgroundColor: colors.surface,
    padding: spacing.lg,
  },
  emptyText: { ...typography.bodySmall, color: colors.textSecondary },
});
