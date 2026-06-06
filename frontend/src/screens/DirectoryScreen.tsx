import React, { useEffect, useMemo, useState } from "react";
import {
  ActivityIndicator,
  FlatList,
  Linking,
  ScrollView,
  StyleSheet,
  Text,
  TextInput,
  TouchableOpacity,
  View,
} from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { Ionicons } from "@expo/vector-icons";
import { LinearGradient } from "expo-linear-gradient";
import { useNavigation } from "@react-navigation/native";

import { AppHeader } from "../components/AppHeader";
import { cityService, placeService } from "../services/api";
import {
  EmergencyContact,
  Institution,
  PostalCode,
  ServiceProvider,
  TaxiStand,
} from "../types";
import { borderRadius, colors, spacing, typography } from "../theme";
import { openDirections } from "../utils/externalActions";

type IconName = keyof typeof Ionicons.glyphMap;

type DirectoryCategory =
  | "all"
  | "emergency"
  | "health"
  | "public"
  | "school"
  | "bank"
  | "cargo"
  | "notary"
  | "taxi"
  | "parking"
  | "service"
  | "neighborhood";

type DirectoryEntry = {
  id: string;
  title: string;
  category: DirectoryCategory;
  categoryLabel: string;
  subtitle: string;
  detail?: string | null;
  phone?: string | null;
  address?: string | null;
  meta?: string | null;
  icon: IconName;
  tone: string;
  searchText: string;
  priority: number;
};

const CATEGORIES: Array<{
  key: DirectoryCategory;
  label: string;
  icon: IconName;
}> = [
  { key: "all", label: "Tümü", icon: "apps-outline" },
  { key: "emergency", label: "Acil", icon: "call-outline" },
  { key: "health", label: "Sağlık", icon: "medical-outline" },
  { key: "public", label: "Kamu", icon: "business-outline" },
  { key: "school", label: "Okullar", icon: "school-outline" },
  { key: "bank", label: "Banka / ATM", icon: "card-outline" },
  { key: "cargo", label: "Kargo", icon: "cube-outline" },
  { key: "notary", label: "Noter", icon: "document-text-outline" },
  { key: "taxi", label: "Taksi", icon: "car-outline" },
  { key: "parking", label: "Otopark", icon: "car-sport-outline" },
  { key: "service", label: "Hizmetler", icon: "construct-outline" },
  { key: "neighborhood", label: "Mahalle", icon: "map-outline" },
];

const HERO_CATEGORIES: DirectoryCategory[] = ["emergency", "taxi", "health"];

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

function categoryLabel(key: DirectoryCategory): string {
  return CATEGORIES.find((item) => item.key === key)?.label || "Rehber";
}

function institutionCategory(row: Institution): DirectoryCategory {
  const category = normalizeText(row.category);
  const subcategory = normalizeText(row.subcategory);
  const joined = `${category} ${subcategory} ${normalizeText(row.name)}`;

  if (joined.includes("saglik") || joined.includes("hastane") || joined.includes("eczane")) return "health";
  if (joined.includes("egitim") || joined.includes("okul")) return "school";
  if (joined.includes("banka") || joined.includes("atm")) return "bank";
  if (joined.includes("kargo")) return "cargo";
  if (joined.includes("noter")) return "notary";
  if (joined.includes("otopark")) return "parking";
  return "public";
}

function institutionIcon(key: DirectoryCategory): IconName {
  if (key === "health") return "medical-outline";
  if (key === "school") return "school-outline";
  if (key === "bank") return "card-outline";
  if (key === "cargo") return "cube-outline";
  if (key === "notary") return "document-text-outline";
  if (key === "parking") return "car-sport-outline";
  return "business-outline";
}

function serviceLabel(category?: string | null): string {
  const text = normalizeText(category);
  if (text.includes("tesisat")) return "Tesisatçı";
  if (text.includes("elektrik")) return "Elektrikçi";
  if (text.includes("cilingir")) return "Çilingir";
  if (text.includes("oto")) return "Oto hizmet";
  if (text.includes("veteriner")) return "Veteriner";
  if (text.includes("nakliyat")) return "Nakliyat";
  return "Hizmet";
}

function makeSearchText(parts: Array<string | null | undefined>): string {
  return normalizeText(parts.filter(Boolean).join(" "));
}

function buildEntries({
  emergency,
  institutions,
  services,
  taxis,
  postalCodes,
}: {
  emergency: EmergencyContact[];
  institutions: Institution[];
  services: ServiceProvider[];
  taxis: TaxiStand[];
  postalCodes: PostalCode[];
}): DirectoryEntry[] {
  const emergencyEntries: DirectoryEntry[] = emergency.map((row) => ({
    id: `emergency-${row.id}`,
    title: row.name,
    category: normalizeText(row.category).includes("saglik") ? "health" : "emergency",
    categoryLabel: normalizeText(row.category).includes("saglik") ? "Sağlık" : "Acil",
    subtitle: row.phone,
    detail: row.description || "Hızlı iletişim",
    phone: row.phone,
    icon: "call-outline",
    tone: colors.error,
    searchText: makeSearchText([row.name, row.phone, row.category, row.description, "acil telefon"]),
    priority: row.priority,
  }));

  const institutionEntries: DirectoryEntry[] = institutions.map((row) => {
    const category = institutionCategory(row);
    return {
      id: `institution-${row.id}`,
      title: row.name,
      category,
      categoryLabel: categoryLabel(category),
      subtitle: row.phone || categoryLabel(category),
      detail: row.address || row.description || row.subcategory || "Adres bilgisi bekleniyor",
      phone: row.phone,
      address: row.address,
      icon: institutionIcon(category),
      tone: category === "health" ? colors.success : colors.primary,
      searchText: makeSearchText([
        row.name,
        row.phone,
        row.address,
        row.category,
        row.subcategory,
        row.description,
        categoryLabel(category),
      ]),
      priority: 100,
    };
  });

  const serviceEntries: DirectoryEntry[] = services.map((row) => ({
    id: `service-${row.id}`,
    title: row.name,
    category: "service",
    categoryLabel: serviceLabel(row.category),
    subtitle: row.phone,
    detail: row.neighborhood || row.address || row.description || (row.is_24h ? "24 saat" : "Hizmet sağlayıcı"),
    phone: row.phone,
    address: row.address || row.neighborhood || null,
    meta: row.is_24h ? "24 saat" : null,
    icon: "construct-outline",
    tone: colors.tertiary,
    searchText: makeSearchText([
      row.name,
      row.phone,
      row.category,
      row.neighborhood,
      row.address,
      row.description,
      serviceLabel(row.category),
      "çilingir tesisatçı elektrikçi hizmet",
    ]),
    priority: 120,
  }));

  const taxiEntries: DirectoryEntry[] = taxis.map((row) => ({
    id: `taxi-${row.id}`,
    title: row.name,
    category: "taxi",
    categoryLabel: "Taksi",
    subtitle: row.phone || "Telefon bilgisi yok",
    detail: row.address || (row.is_24h ? "24 saat hizmet" : "Taksi durağı"),
    phone: row.phone,
    address: row.address,
    meta: row.is_24h ? "24 saat" : null,
    icon: "car-outline",
    tone: colors.info,
    searchText: makeSearchText([row.name, row.phone, row.address, "taksi durak durağı"]),
    priority: 80,
  }));

  const postalEntries: DirectoryEntry[] = postalCodes.map((row) => ({
    id: `postal-${row.id}`,
    title: `${row.neighborhood} Mahallesi`,
    category: "neighborhood",
    categoryLabel: "Mahalle",
    subtitle: row.postal_code,
    detail: `${row.district} posta kodu`,
    meta: row.postal_code,
    icon: "map-outline",
    tone: colors.primary,
    searchText: makeSearchText([row.neighborhood, row.postal_code, row.district, "mahalle posta kodu"]),
    priority: 130,
  }));

  return [
    ...emergencyEntries,
    ...taxiEntries,
    ...institutionEntries,
    ...serviceEntries,
    ...postalEntries,
  ].sort((a, b) => a.priority - b.priority || a.title.localeCompare(b.title, "tr"));
}

function dialPhone(phone?: string | null) {
  if (!phone) return;
  const sanitized = phone.replace(/[^\d+]/g, "");
  if (!sanitized) return;
  void Linking.openURL(`tel:${sanitized}`).catch(() => undefined);
}

function openMap(entry: DirectoryEntry) {
  let target = entry.title;
  if (entry.address && entry.address.toLowerCase() !== entry.title.toLowerCase()) {
    target = `${entry.title}, ${entry.address}`;
  }
  void openDirections(`${target} Aliağa`);
}

async function safe<T>(request: Promise<T>, fallback: T): Promise<T> {
  try {
    return await request;
  } catch {
    return fallback;
  }
}

export function DirectoryScreen() {
  const navigation = useNavigation<any>();
  const [loading, setLoading] = useState(true);
  const [query, setQuery] = useState("");
  const [selectedCategory, setSelectedCategory] = useState<DirectoryCategory>("all");
  const [entries, setEntries] = useState<DirectoryEntry[]>([]);
  const [searchFocused, setSearchFocused] = useState(false);

  useEffect(() => {
    const load = async () => {
      try {
        const [emergency, institutions, services, taxis, postalCodes] = await Promise.all([
          safe(cityService.getEmergencyContacts(100), []),
          safe(placeService.getInstitutions(undefined, 100), []),
          safe(placeService.getServices(undefined, 100), []),
          safe(cityService.getTaxis(100), []),
          safe(cityService.getPostalCodes(200), []),
        ]);

        setEntries(buildEntries({ emergency, institutions, services, taxis, postalCodes }));
      } finally {
        setLoading(false);
      }
    };

    load();
  }, []);

  const categoryCounts = useMemo(() => {
    const counts: Record<string, number> = { all: entries.length };
    for (const entry of entries) {
      counts[entry.category] = (counts[entry.category] || 0) + 1;
    }
    return counts;
  }, [entries]);

  const normalizedQuery = normalizeText(query.trim());
  const filteredEntries = useMemo(() => {
    return entries.filter((entry) => {
      const categoryMatches = selectedCategory === "all" || entry.category === selectedCategory;
      const queryMatches = !normalizedQuery || entry.searchText.includes(normalizedQuery);
      return categoryMatches && queryMatches;
    });
  }, [entries, normalizedQuery, selectedCategory]);

  const overviewMode = !normalizedQuery && selectedCategory === "all";
  const featuredEntries = useMemo(
    () => entries.filter((entry) => entry.category === "emergency" || entry.category === "taxi").slice(0, 8),
    [entries]
  );
  const visibleEntries = overviewMode ? featuredEntries : filteredEntries;
  const activeCategoryCount = CATEGORIES.filter(
    (item) => item.key !== "all" && (categoryCounts[item.key] || 0) > 0
  ).length;

  const selectCategory = (key: DirectoryCategory) => {
    setSelectedCategory(key);
  };

  const renderEntry = ({ item }: { item: DirectoryEntry }) => (
    <View style={[styles.resultCard, { borderColor: `${item.tone}2C` }]}>
      <View style={styles.resultTop}>
        <View style={[styles.resultIcon, { backgroundColor: `${item.tone}22` }]}>
          <Ionicons name={item.icon} size={18} color={item.tone} />
        </View>
        <View style={styles.resultBody}>
          <View style={styles.resultMetaRow}>
            <Text style={styles.resultCategory}>{item.categoryLabel}</Text>
            {item.meta ? <Text style={styles.resultMeta}>{item.meta}</Text> : null}
          </View>
          <Text style={styles.resultTitle} numberOfLines={2}>
            {item.title}
          </Text>
          <Text style={styles.resultSubtitle} numberOfLines={1}>
            {item.subtitle}
          </Text>
        </View>
      </View>

      {item.detail ? (
        <Text style={styles.resultDetail} numberOfLines={2}>
          {item.detail}
        </Text>
      ) : null}

      {(item.phone || item.address) && (
        <View style={styles.actionRow}>
          {item.phone ? (
            <TouchableOpacity
              accessibilityRole="button"
              style={styles.actionButton}
              onPress={() => dialPhone(item.phone)}
            >
              <Ionicons name="call" size={15} color={colors.background} />
              <Text style={styles.actionButtonText}>Ara</Text>
            </TouchableOpacity>
          ) : null}
          {item.address ? (
            <TouchableOpacity
              accessibilityRole="button"
              style={styles.secondaryButton}
              onPress={() => openMap(item)}
            >
              <Ionicons name="navigate-outline" size={15} color={colors.primary} />
              <Text style={styles.secondaryButtonText}>Konum</Text>
            </TouchableOpacity>
          ) : null}
        </View>
      )}
    </View>
  );

  return (
    <View style={styles.container}>
      <SafeAreaView style={styles.safeArea} edges={["top"]}>
        <AppHeader />

        {loading ? (
          <View style={styles.center}>
            <ActivityIndicator size="large" color={colors.primary} />
          </View>
        ) : (
          <FlatList
            data={visibleEntries}
            keyExtractor={(item) => item.id}
            renderItem={renderEntry}
            keyboardShouldPersistTaps="handled"
            showsVerticalScrollIndicator={false}
            contentContainerStyle={styles.listContent}
            ListHeaderComponent={
              <View>
                <LinearGradient
                  colors={["rgba(31,31,35,0.98)", "rgba(14,14,16,0.98)", "rgba(9,9,10,0.96)"]}
                  locations={[0, 0.58, 1]}
                  style={styles.heroCard}
                >
                  <View style={styles.heroGlow} />
                  <View style={styles.heroTop}>
                    <View style={styles.heroKickerRow}>
                      <View style={styles.kickerMark} />
                      <Text style={styles.heroKicker}>REHBER</Text>
                    </View>
                    <View style={styles.statusBadge}>
                      <Ionicons name="layers-outline" size={14} color={colors.primary} />
                      <Text style={styles.statusBadgeText}>{entries.length} kayıt</Text>
                    </View>
                  </View>

                  <Text style={styles.pageTitle}>Aradığın yer burada.</Text>
                  <Text style={styles.pageSubtitle}>
                    Kurum, hizmet, mahalle, telefon ve konumu tek ekrandan bul.
                  </Text>

                  <View style={[styles.searchBox, searchFocused && styles.searchBoxFocused]}>
                    <Ionicons name="search" size={18} color={searchFocused ? colors.primary : colors.textSecondary} />
                    <TextInput
                      value={query}
                      onChangeText={setQuery}
                      placeholder="Noter, taksi, Atatürk Mahallesi..."
                      placeholderTextColor="rgba(255, 255, 255, 0.48)"
                      style={styles.searchInput}
                      autoCorrect={false}
                      returnKeyType="search"
                      onFocus={() => setSearchFocused(true)}
                      onBlur={() => setSearchFocused(false)}
                    />
                    {query ? (
                      <TouchableOpacity accessibilityRole="button" hitSlop={8} onPress={() => setQuery("")}>
                        <Ionicons name="close-circle" size={18} color={colors.textTertiary} />
                      </TouchableOpacity>
                    ) : null}
                  </View>

                  <View style={styles.heroQuickRow}>
                    {HERO_CATEGORIES.map((key) => {
                      const category = CATEGORIES.find((item) => item.key === key);
                      if (!category) return null;
                      return (
                        <TouchableOpacity
                          key={key}
                          accessibilityRole="button"
                          activeOpacity={0.86}
                          style={styles.heroQuickCard}
                          onPress={() => selectCategory(key)}
                        >
                          <View style={styles.heroQuickIcon}>
                            <Ionicons name={category.icon} size={16} color={colors.primary} />
                          </View>
                          <Text style={styles.heroQuickTitle}>{category.label}</Text>
                          <Text style={styles.heroQuickCount}>{categoryCounts[key] || 0}</Text>
                        </TouchableOpacity>
                      );
                    })}
                  </View>
                </LinearGradient>

                <ScrollView
                  horizontal
                  showsHorizontalScrollIndicator={false}
                  contentContainerStyle={styles.categoryRow}
                >
                  {CATEGORIES.map((item) => {
                    const active = selectedCategory === item.key;
                    return (
                      <TouchableOpacity
                        key={item.key}
                        accessibilityRole="button"
                        style={[styles.categoryChip, active && styles.categoryChipActive]}
                        onPress={() => selectCategory(item.key)}
                      >
                        <Ionicons
                          name={item.icon}
                          size={14}
                          color={active ? colors.primary : colors.textSecondary}
                        />
                        <Text style={[styles.categoryText, active && styles.categoryTextActive]}>
                          {item.label}
                        </Text>
                        <Text style={styles.categoryCount}>{categoryCounts[item.key] || 0}</Text>
                      </TouchableOpacity>
                    );
                  })}
                </ScrollView>

                {overviewMode ? (
                  <View style={styles.overviewGrid}>
                    {CATEGORIES.filter((item) => item.key !== "all" && (categoryCounts[item.key] || 0) > 0)
                      .slice(0, 8)
                      .map((item) => (
                        <TouchableOpacity
                          key={item.key}
                          accessibilityRole="button"
                          style={styles.overviewTile}
                          onPress={() => selectCategory(item.key)}
                        >
                          <View style={styles.overviewIcon}>
                            <Ionicons name={item.icon} size={18} color={colors.primary} />
                          </View>
                          <Text style={styles.overviewTitle}>{item.label}</Text>
                          <Text style={styles.overviewCount}>{categoryCounts[item.key] || 0} kayıt</Text>
                        </TouchableOpacity>
                      ))}
                  </View>
                ) : null}

                <View style={styles.resultsHeader}>
                  <Text style={styles.resultsTitle}>
                    {overviewMode ? "SIK KULLANILANLAR" : "SONUÇLAR"}
                  </Text>
                  <Text style={styles.resultsCount}>
                    {overviewMode ? `${activeCategoryCount} kategori` : `${filteredEntries.length} kayıt`}
                  </Text>
                </View>
              </View>
            }
            ListEmptyComponent={
              <View style={styles.emptyCard}>
                <Ionicons name="search-outline" size={24} color={colors.textTertiary} />
                <Text style={styles.emptyTitle}>Sonuç bulunamadı.</Text>
                <Text style={styles.emptyText}>Aradığınız kurum veya numarayı bulamadınız mı?</Text>
                <TouchableOpacity
                  style={styles.aiRedirectButton}
                  onPress={() => {
                    navigation.navigate("Chat", {
                      presetPrompt: `Aliağa kent rehberinde "${query}" araması yaptım fakat sonuç bulamadım. Bu kurum/hizmet hakkında telefon, adres ve çalışma saati detaylarını benim için bulup paylaşır mısın?`,
                      presetPromptId: `${Date.now()}`
                    });
                  }}
                >
                  <Ionicons name="sparkles-outline" size={16} color={colors.background} />
                  <Text style={styles.aiRedirectButtonText}>AliağaAI Asistanına Sor</Text>
                </TouchableOpacity>
              </View>
            }
          />
        )}
      </SafeAreaView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.background },
  safeArea: { flex: 1 },
  center: { flex: 1, alignItems: "center", justifyContent: "center" },
  listContent: {
    paddingHorizontal: spacing.lg,
    paddingTop: 80,
    paddingBottom: 140,
  },
  heroCard: {
    position: "relative",
    overflow: "hidden",
    borderRadius: borderRadius.xl,
    borderWidth: 1,
    borderColor: "rgba(200,169,110,0.24)",
    padding: spacing.lg,
    marginTop: spacing.lg,
    marginBottom: spacing.lg,
  },
  heroGlow: {
    position: "absolute",
    top: -70,
    right: -58,
    width: 172,
    height: 172,
    borderRadius: 86,
    backgroundColor: "rgba(200,169,110,0.14)",
  },
  heroTop: {
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
  heroKicker: {
    ...typography.caption,
    color: colors.primary,
    letterSpacing: 1.8,
  },
  statusBadge: {
    minHeight: 30,
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
  pageTitle: {
    fontSize: 36,
    lineHeight: 42,
    fontWeight: "700",
    color: colors.text,
    letterSpacing: 0,
  },
  pageSubtitle: {
    ...typography.bodySmall,
    color: colors.textSecondary,
    marginTop: spacing.xs,
    maxWidth: 302,
  },
  searchBox: {
    minHeight: 56,
    borderRadius: borderRadius.lg,
    borderWidth: 1,
    borderColor: "rgba(255,255,255,0.09)",
    backgroundColor: "rgba(255,255,255,0.045)",
    paddingHorizontal: spacing.md,
    flexDirection: "row",
    alignItems: "center",
    gap: spacing.sm,
    marginTop: spacing.lg,
  },
  searchBoxFocused: {
    borderColor: colors.primary,
    shadowColor: colors.primary,
    shadowOffset: { width: 0, height: 0 },
    shadowOpacity: 0.15,
    shadowRadius: 8,
    elevation: 3,
  },
  searchInput: {
    flex: 1,
    color: colors.text,
    fontSize: 15,
    lineHeight: 20,
    paddingVertical: spacing.md,
  },
  heroQuickRow: {
    flexDirection: "row",
    gap: spacing.sm,
    marginTop: spacing.md,
  },
  heroQuickCard: {
    flex: 1,
    minHeight: 82,
    borderRadius: borderRadius.lg,
    borderWidth: 1,
    borderColor: "rgba(255,255,255,0.08)",
    backgroundColor: "rgba(255,255,255,0.04)",
    padding: spacing.sm,
    justifyContent: "space-between",
  },
  heroQuickIcon: {
    width: 28,
    height: 28,
    borderRadius: 14,
    alignItems: "center",
    justifyContent: "center",
    backgroundColor: colors.primaryLight,
  },
  heroQuickTitle: {
    ...typography.captionSmall,
    color: colors.textSecondary,
    textTransform: "none",
  },
  heroQuickCount: {
    fontFamily: "Outfit_800ExtraBold",
    fontSize: 18,
    lineHeight: 22,
    color: colors.text,
  },
  categoryRow: {
    gap: spacing.sm,
    paddingBottom: spacing.xl,
    marginVertical: spacing.md,
  },
  categoryChip: {
    minHeight: 40,
    borderRadius: borderRadius.full,
    borderWidth: 1,
    borderColor: "rgba(255,255,255,0.08)",
    backgroundColor: "rgba(24,24,27,0.82)",
    paddingHorizontal: spacing.md,
    flexDirection: "row",
    alignItems: "center",
    gap: spacing.xs,
  },
  categoryChipActive: {
    borderColor: "rgba(200,169,110,0.7)",
    backgroundColor: "rgba(200,169,110,0.12)",
  },
  categoryText: {
    ...typography.bodySmall,
    fontFamily: "PlusJakartaSans_600SemiBold",
    color: colors.textSecondary,
  },
  categoryTextActive: {
    fontFamily: "PlusJakartaSans_700Bold",
    color: colors.primary,
  },
  categoryCount: {
    ...typography.captionSmall,
    color: colors.textTertiary,
  },
  overviewGrid: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: spacing.sm,
    marginBottom: spacing.xl,
  },
  overviewTile: {
    width: "48.5%",
    minHeight: 118,
    borderRadius: borderRadius.lg,
    borderWidth: 1,
    borderColor: "rgba(200,169,110,0.18)",
    backgroundColor: "rgba(23,23,26,0.88)",
    padding: spacing.md,
    justifyContent: "space-between",
  },
  overviewIcon: {
    width: 36,
    height: 36,
    borderRadius: 18,
    alignItems: "center",
    justifyContent: "center",
    backgroundColor: colors.primaryLight,
  },
  overviewTitle: {
    fontSize: 16,
    lineHeight: 21,
    color: colors.text,
    fontWeight: "800",
  },
  overviewCount: {
    ...typography.captionSmall,
    color: colors.textSecondary,
    marginTop: 2,
  },
  resultsHeader: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    borderBottomWidth: 1,
    borderBottomColor: colors.borderLight,
    paddingBottom: spacing.sm,
    marginBottom: spacing.md,
  },
  resultsTitle: {
    ...typography.caption,
    color: colors.primary,
    letterSpacing: 1.5,
  },
  resultsCount: {
    ...typography.captionSmall,
    color: colors.textSecondary,
  },
  resultCard: {
    borderRadius: borderRadius.lg,
    borderWidth: 1,
    backgroundColor: "rgba(20,20,24,0.94)",
    padding: spacing.lg,
    marginBottom: spacing.md,
  },
  resultTop: {
    flexDirection: "row",
    alignItems: "flex-start",
  },
  resultIcon: {
    width: 40,
    height: 40,
    borderRadius: 20,
    justifyContent: "center",
    alignItems: "center",
    marginRight: spacing.md,
  },
  resultBody: {
    flex: 1,
    minWidth: 0,
  },
  resultMetaRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    gap: spacing.sm,
    marginBottom: 2,
  },
  resultCategory: {
    ...typography.captionSmall,
    color: colors.primary,
  },
  resultMeta: {
    ...typography.captionSmall,
    color: colors.textTertiary,
  },
  resultTitle: {
    ...typography.bodyMedium,
    color: colors.text,
    fontWeight: "700",
  },
  resultSubtitle: {
    ...typography.bodySmall,
    color: colors.textSecondary,
    marginTop: 2,
  },
  resultDetail: {
    ...typography.bodySmall,
    color: colors.textSecondary,
    marginTop: spacing.md,
  },
  actionRow: {
    flexDirection: "row",
    gap: spacing.sm,
    marginTop: spacing.md,
  },
  actionButton: {
    minHeight: 48,
    borderRadius: borderRadius.full,
    backgroundColor: colors.primary,
    paddingHorizontal: spacing.lg,
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "center",
    gap: spacing.xs,
  },
  actionButtonText: {
    ...typography.bodySmall,
    color: colors.background,
    fontWeight: "800",
  },
  secondaryButton: {
    minHeight: 48,
    borderRadius: borderRadius.full,
    borderWidth: 1,
    borderColor: "rgba(200,169,110,0.32)",
    paddingHorizontal: spacing.lg,
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "center",
    gap: spacing.xs,
  },
  secondaryButtonText: {
    ...typography.bodySmall,
    color: colors.primary,
    fontWeight: "700",
  },
  emptyCard: {
    borderRadius: borderRadius.lg,
    borderWidth: 1,
    borderColor: colors.borderLight,
    backgroundColor: colors.surface,
    padding: spacing.lg,
    alignItems: "center",
  },
  emptyTitle: {
    ...typography.bodyMedium,
    color: colors.text,
    marginTop: spacing.sm,
  },
  emptyText: {
    ...typography.bodySmall,
    color: colors.textSecondary,
    textAlign: "center",
    marginTop: spacing.xs,
  },
  aiRedirectButton: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "center",
    gap: spacing.xs,
    backgroundColor: colors.primary,
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.md,
    borderRadius: borderRadius.md,
    marginTop: spacing.md,
    width: "100%",
  },
  aiRedirectButtonText: {
    ...typography.button,
    color: colors.background,
    fontSize: 14,
  },
});
