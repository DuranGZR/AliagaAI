import React, { useCallback, useEffect, useState, useMemo } from "react";
import {
  ActivityIndicator,
  FlatList,
  RefreshControl,
  StyleSheet,
  Text,
  TouchableOpacity,
  View,
  Share,
} from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { Ionicons } from "@expo/vector-icons";
import { useNavigation } from "@react-navigation/native";
import { LinearGradient } from "expo-linear-gradient";

import { DataStatePanel } from "../components/DataStatePanel";
import { pharmacyService } from "../services/api";
import { borderRadius, colors, spacing, typography } from "../theme";
import { Pharmacy } from "../types";
import { DataState, loadDataState } from "../utils/dataState";
import { openDirections, openPhone } from "../utils/externalActions";
import { useLocation } from "../context/LocationContext";
import { calculateDistance, formatDistance } from "../utils/location";

const AUTO_REFRESH_MS = 10 * 60 * 1000;

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
  return date.toLocaleDateString("tr-TR", { day: "2-digit", month: "long", year: "numeric" });
}

export function PharmacyListScreen() {
  const navigation = useNavigation<any>();
  const [pharmacies, setPharmacies] = useState<Pharmacy[]>([]);
  const [state, setState] = useState<DataState<Pharmacy[]> | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const { location, permissionStatus, requestPermission } = useLocation();

  useEffect(() => {
    if (permissionStatus === "undetermined") {
      void requestPermission();
    }
  }, [permissionStatus, requestPermission]);

  const sortedPharmacies = useMemo(() => {
    if (!location) return pharmacies;
    const mapped = pharmacies.map((item) => {
      if (item.latitude && item.longitude) {
        const dist = calculateDistance(
          location.latitude,
          location.longitude,
          Number(item.latitude),
          Number(item.longitude)
        );
        return { ...item, distance: dist };
      }
      return item;
    });
    return [...mapped].sort((a, b) => {
      const distA = (a as any).distance !== undefined ? (a as any).distance : Infinity;
      const distB = (b as any).distance !== undefined ? (b as any).distance : Infinity;
      return distA - distB;
    });
  }, [pharmacies, location]);

  const firstPharmacy = sortedPharmacies[0];
  const hasTodayData = firstPharmacy ? isTodayDate(firstPharmacy.duty_date) : false;

  const fetchPharmacies = useCallback(async (isRefresh = false) => {
    if (isRefresh) {
      setRefreshing(true);
    } else {
      setLoading(true);
    }

    const dataState = await loadDataState(() => pharmacyService.getToday(), [] as Pharmacy[]);
    setState(dataState);

    // Deduplicate pharmacies by name and address
    const uniquePharmacies: Pharmacy[] = [];
    const seenKeys = new Set<string>();
    for (const item of (dataState.data || [])) {
      const nameKey = (item.name || "").replace(/\s+/g, "").toLowerCase();
      const addrKey = (item.address || "").replace(/\s+/g, "").toLowerCase();
      const key = `${nameKey}_${addrKey}`;
      if (!seenKeys.has(key)) {
        seenKeys.add(key);
        uniquePharmacies.push(item);
      }
    }

    setPharmacies(uniquePharmacies);
    setLoading(false);
    setRefreshing(false);
  }, []);

  useEffect(() => {
    void fetchPharmacies();
    const timer = setInterval(() => void fetchPharmacies(true), AUTO_REFRESH_MS);
    return () => clearInterval(timer);
  }, [fetchPharmacies]);

  const sharePharmacy = async (item: Pharmacy) => {
    try {
      const message = `📍 Nöbetçi Eczane: ${item.name}\n📞 Telefon: ${item.phone || "Belirtilmemiş"}\n🗺️ Adres: ${item.address || "Belirtilmemiş"}\n📅 Tarih: ${formatDateOnly(item.duty_date)}\n\nAliağaAI ile paylaşıldı.`;
      await Share.share({ message });
    } catch (error) {
      console.log("Sharing error:", error);
    }
  };

  const renderItem = ({ item }: { item: Pharmacy }) => {
    const distanceStr = (item as any).distance !== undefined
      ? formatDistance((item as any).distance)
      : null;

    return (
      <LinearGradient colors={colors.gradients.surface} style={styles.pharmacyCard}>
        <View style={styles.pharmacyInfo}>
          <View style={styles.pharmacyHeaderRow}>
            <View style={{ flexDirection: "row", alignItems: "center", flex: 1, gap: spacing.sm }}>
              <Ionicons name="medical" size={16} color={colors.primary} />
              <Text style={styles.pharmacyName}>{item.name}</Text>
            </View>
            {distanceStr && (
              <View style={styles.distanceBadge}>
                <Ionicons name="location-sharp" size={10} color={colors.primary} />
                <Text style={styles.distanceText}>{distanceStr}</Text>
              </View>
            )}
          </View>
          <View style={styles.pharmacyDetailRow}>
            <Ionicons name="location" size={14} color={colors.textTertiary} />
            <Text style={styles.pharmacyAddress}>{item.address || "Adres bilgisi bulunmuyor"}</Text>
          </View>
          {item.phone ? (
            <View style={styles.pharmacyDetailRow}>
              <Ionicons name="call" size={14} color={colors.textTertiary} />
              <Text style={styles.pharmacyPhone}>{item.phone}</Text>
            </View>
          ) : null}
          <Text style={styles.pharmacyDate}>
            {isTodayDate(item.duty_date) ? "Bugünün nöbetçi kaydı" : `Son kayıt ${formatDateOnly(item.duty_date)}`}
          </Text>
        </View>
        <View style={styles.actionRow}>
          {item.phone ? (
            <TouchableOpacity style={styles.secondaryButton} onPress={() => void openPhone(item.phone)}>
              <Ionicons name="call-outline" size={16} color={colors.text} />
              <Text style={styles.secondaryButtonText}>Ara</Text>
            </TouchableOpacity>
          ) : null}
          <TouchableOpacity style={styles.secondaryButton} onPress={() => void sharePharmacy(item)}>
            <Ionicons name="share-social-outline" size={16} color={colors.text} />
            <Text style={styles.secondaryButtonText}>Paylaş</Text>
          </TouchableOpacity>
          <TouchableOpacity
            style={styles.directionsButton}
            onPress={() => void openDirections(`${item.name} ${item.address || "Aliağa"}`, item.maps_link)}
          >
            <Ionicons name="navigate" size={16} color={colors.background} />
            <Text style={styles.directionsText}>Yol Tarifi</Text>
          </TouchableOpacity>
        </View>
      </LinearGradient>
    );
  };

  return (
    <View style={styles.container}>
      <SafeAreaView style={styles.safeArea}>
        <View style={styles.header}>
          <TouchableOpacity
            style={styles.backButton}
            onPress={() => navigation.goBack()}
            hitSlop={{ top: 10, bottom: 10, left: 10, right: 10 }}
          >
            <Ionicons name="arrow-back" size={24} color={colors.text} />
          </TouchableOpacity>
          <View style={styles.headerCopy}>
            <Text style={styles.headerTitle}>
              {hasTodayData ? "Bugünkü Nöbetçi Eczaneler" : "Nöbetçi Eczaneler"}
            </Text>
            <Text style={styles.headerSubTitle}>
              {firstPharmacy
                ? hasTodayData
                  ? `${pharmacies.length} güncel kayıt`
                  : `Son kayıt: ${formatDateOnly(firstPharmacy.duty_date)}`
                : state?.status === "error"
                  ? "Kaynak yenilenemedi"
                  : "Güncel kayıt bekleniyor"}
            </Text>
          </View>
          <View style={{ width: 40 }} />
        </View>

        {loading ? (
          <View style={styles.center}>
            <ActivityIndicator size="large" color={colors.primary} />
          </View>
        ) : pharmacies.length === 0 ? (
          <View style={styles.center}>
            <DataStatePanel
              tone={state?.status === "error" ? "warning" : "info"}
              title={state?.status === "error" ? "Eczane kaynağı cevap vermedi" : "Bugünün nöbetçi eczane kaydı yok"}
              text={
                state?.status === "error"
                  ? "Aşağı çekerek tekrar deneyebilirsin. Ana ekranda son başarılı kayıt ayrı gösterilir."
                  : "Kaynak yenilendiğinde bu alan otomatik dolacak."
              }
            />
          </View>
        ) : (
          <FlatList
            data={sortedPharmacies}
            keyExtractor={(item, index) => (item.id ? item.id.toString() : index.toString())}
            renderItem={renderItem}
            contentContainerStyle={styles.listContent}
            showsVerticalScrollIndicator={false}
            refreshControl={
              <RefreshControl
                refreshing={refreshing}
                onRefresh={() => void fetchPharmacies(true)}
                tintColor={colors.primary}
                colors={[colors.primary]}
              />
            }
          />
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
  headerCopy: {
    flex: 1,
    alignItems: "center",
  },
  headerTitle: {
    ...typography.h3,
    color: colors.text,
    textAlign: "center",
  },
  headerSubTitle: {
    ...typography.captionSmall,
    color: colors.textTertiary,
    marginTop: 2,
    textTransform: "none",
  },
  center: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
    padding: spacing.xl,
  },
  listContent: {
    padding: spacing.xl,
    paddingBottom: 110,
  },
  pharmacyCard: {
    padding: spacing.lg,
    borderRadius: borderRadius.lg,
    marginBottom: spacing.md,
    borderWidth: 1,
    borderColor: "rgba(255, 255, 255, 0.05)",
  },
  pharmacyInfo: {
    marginBottom: spacing.md,
  },
  pharmacyHeaderRow: {
    flexDirection: "row",
    alignItems: "center",
    gap: spacing.sm,
    marginBottom: spacing.sm,
  },
  pharmacyName: {
    ...typography.h3,
    color: colors.text,
    flex: 1,
  },
  distanceBadge: {
    flexDirection: "row",
    alignItems: "center",
    gap: 4,
    backgroundColor: "rgba(200, 169, 110, 0.15)",
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 8,
    borderWidth: 0.5,
    borderColor: "rgba(200, 169, 110, 0.3)",
  },
  distanceText: {
    ...typography.captionSmall,
    color: colors.primary,
    fontWeight: "700",
  },
  pharmacyDetailRow: {
    flexDirection: "row",
    alignItems: "center",
    gap: spacing.xs,
    marginBottom: spacing.xs,
  },
  pharmacyAddress: {
    ...typography.bodySmall,
    color: colors.textSecondary,
    flex: 1,
  },
  pharmacyPhone: {
    ...typography.bodySmall,
    color: colors.textSecondary,
  },
  pharmacyDate: {
    ...typography.captionSmall,
    color: colors.primary,
    marginTop: spacing.xs,
    textTransform: "none",
  },
  actionRow: {
    flexDirection: "row",
    gap: spacing.sm,
  },
  secondaryButton: {
    minWidth: 84,
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "center",
    gap: spacing.xs,
    backgroundColor: colors.surfaceLight,
    borderWidth: 1,
    borderColor: colors.borderLight,
    paddingVertical: spacing.md,
    borderRadius: borderRadius.md,
  },
  secondaryButtonText: {
    ...typography.button,
    color: colors.text,
    fontSize: 14,
  },
  directionsButton: {
    flex: 1,
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "center",
    gap: spacing.xs,
    backgroundColor: colors.primary,
    paddingVertical: spacing.md,
    borderRadius: borderRadius.md,
  },
  directionsText: {
    ...typography.button,
    color: colors.background,
    fontSize: 14,
  },
});
