import React from "react";
import { ScrollView, StyleSheet, Text, TouchableOpacity, View } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { LinearGradient } from "expo-linear-gradient";
import { Ionicons } from "@expo/vector-icons";
import { useNavigation, useRoute } from "@react-navigation/native";

import { ReliableImage } from "../components/ReliableImage";
import { colors, spacing, typography, shadows, borderRadius } from "../theme";
import {
  PlaceDetailItem,
  categoryOfPlace,
  descriptionForPlace,
  imageForPlace,
  labelForPlaceCategory,
  tagsForPlace,
  translateCategory,
} from "../utils/placeDisplay";
import { openDirections, openExternalUrl, openPhone } from "../utils/externalActions";

const FALLBACK_PLACE: PlaceDetailItem = {
  name: "Aigai Antik Kenti",
  category: "Tarihi Yer",
  address: "Aliağa çevresi",
  description:
    "Aigai, Aiolis bölgesinin önemli antik kentlerinden biridir. Açık hava keşfi, tarih ve fotoğraf rotaları için Aliağa çevresindeki güçlü kültür duraklarından biri olarak öne çıkar.",
  rating: 4.8,
  tags: ["Tarih", "Açık hava", "Kültür"],
};

function normalizeRouteItem(value: unknown): PlaceDetailItem {
  if (!value || typeof value !== "object") return FALLBACK_PLACE;
  const item = value as Partial<PlaceDetailItem>;
  return {
    ...item,
    name: item.name || FALLBACK_PLACE.name,
    category: item.category || FALLBACK_PLACE.category,
    address: item.address || null,
    description: item.description || null,
  };
}

function formatRating(value?: number | null): string | null {
  return typeof value === "number" && Number.isFinite(value) ? value.toFixed(1) : null;
}

function sourceLabel(item: PlaceDetailItem): string {
  if (item.source_label) return item.source_label;
  if (item.source_url || item.website) return "Kaynak bağlantısı var";
  return "Yerel veri kaydı";
}

export function PlaceDetailScreen() {
  const navigation = useNavigation();
  const route = useRoute();
  const item = normalizeRouteItem(route.params);
  const displayCategory = translateCategory(item.category, item.subcategory) || labelForPlaceCategory(categoryOfPlace(item));
  const fallbackImage = imageForPlace({ ...item, image_url: null });
  const tags = tagsForPlace(item);
  const rating = formatRating(item.rating);
  const description = descriptionForPlace(item);

  const handleDirections = () => {
    void openDirections(`${item.name} ${item.address || "Aliağa"}`, item.maps_link);
  };

  return (
    <LinearGradient colors={colors.gradients.bg as any} style={styles.container}>
      <SafeAreaView style={styles.safeArea}>
        <View style={styles.imageHeader}>
          <ReliableImage
            uri={item.image_url}
            fallbackUri={fallbackImage}
            style={styles.headerImage}
            resizeMode="cover"
            label="Mekan görseli"
          />
          <LinearGradient colors={["rgba(0,0,0,0.04)", "rgba(0,0,0,0.54)", colors.background]} style={styles.imageOverlay} />
          <TouchableOpacity style={styles.backButton} onPress={() => navigation.goBack()} accessibilityRole="button">
            <Ionicons name="arrow-back" size={24} color={colors.text} />
          </TouchableOpacity>
          <View style={styles.headerBadge}>
            <Ionicons name="sparkles-outline" size={14} color={colors.primary} />
            <Text style={styles.headerBadgeText}>{displayCategory}</Text>
          </View>
        </View>

        <ScrollView contentContainerStyle={styles.content} showsVerticalScrollIndicator={false}>
          <View style={styles.titleRow}>
            <View style={styles.titleInfo}>
              <Text style={styles.title}>{item.name}</Text>
              <Text style={styles.category}>{sourceLabel(item)}</Text>
            </View>
            {rating ? (
              <View style={styles.ratingBadge}>
                <Ionicons name="star" size={15} color={colors.background} />
                <Text style={styles.ratingText}>{rating}</Text>
              </View>
            ) : null}
          </View>

          <View style={styles.tagsContainer}>
            {tags.map((tag) => (
              <View key={tag} style={styles.tag}>
                <Text style={styles.tagText}>{tag}</Text>
              </View>
            ))}
          </View>

          <View style={styles.infoCard}>
            <InfoRow icon="location" label="Konum" value={item.address || "Aliağa"} />
            {item.phone ? <InfoRow icon="call" label="Telefon" value={item.phone} /> : null}
            {item.website ? <InfoRow icon="globe-outline" label="Web" value={item.website} /> : null}
            {item.source_url ? <InfoRow icon="shield-checkmark-outline" label="Kaynak" value="Resmi veya açık veri bağlantısı" /> : null}
          </View>

          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Hakkında</Text>
            <Text style={styles.description}>{description}</Text>
          </View>


        </ScrollView>

        <View style={styles.bottomBar}>
          {item.phone ? (
            <TouchableOpacity style={styles.secondaryButton} onPress={() => void openPhone(item.phone)} accessibilityRole="button">
              <Ionicons name="call-outline" size={19} color={colors.text} />
            </TouchableOpacity>
          ) : null}
          {item.website || item.source_url ? (
            <TouchableOpacity
              style={styles.secondaryButton}
              onPress={() => void openExternalUrl(item.website || item.source_url)}
              accessibilityRole="button"
            >
              <Ionicons name="open-outline" size={19} color={colors.text} />
            </TouchableOpacity>
          ) : null}
          <TouchableOpacity style={styles.actionButton} onPress={handleDirections} accessibilityRole="button">
            <Ionicons name="map-outline" size={20} color={colors.background} />
            <Text style={styles.actionButtonText}>Yol Tarifi Al</Text>
          </TouchableOpacity>
        </View>
      </SafeAreaView>
    </LinearGradient>
  );
}

function InfoRow({
  icon,
  label,
  value,
}: {
  icon: keyof typeof Ionicons.glyphMap;
  label: string;
  value: string;
}) {
  return (
    <View style={styles.infoRow}>
      <View style={styles.infoIcon}>
        <Ionicons name={icon} size={17} color={colors.primary} />
      </View>
      <View style={styles.infoCopy}>
        <Text style={styles.infoLabel}>{label}</Text>
        <Text style={styles.infoText}>{value}</Text>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  safeArea: {
    flex: 1,
  },
  imageHeader: {
    height: 310,
    backgroundColor: colors.surface,
  },
  headerImage: {
    ...StyleSheet.absoluteFillObject,
  },
  imageOverlay: {
    ...StyleSheet.absoluteFillObject,
  },
  backButton: {
    position: "absolute",
    top: spacing.md,
    left: spacing.lg,
    width: 44,
    height: 44,
    borderRadius: 22,
    backgroundColor: colors.glassDark,
    justifyContent: "center",
    alignItems: "center",
    borderWidth: 1,
    borderColor: colors.borderLight,
  },
  headerBadge: {
    position: "absolute",
    right: spacing.lg,
    bottom: spacing.lg,
    minHeight: 32,
    borderRadius: borderRadius.full,
    borderWidth: 1,
    borderColor: "rgba(200,169,110,0.28)",
    backgroundColor: "rgba(0,0,0,0.48)",
    paddingHorizontal: spacing.md,
    flexDirection: "row",
    alignItems: "center",
    gap: spacing.xs,
  },
  headerBadgeText: {
    ...typography.captionSmall,
    color: colors.primary,
    textTransform: "none",
  },
  content: {
    padding: spacing.xl,
    paddingTop: spacing.lg,
    paddingBottom: 132,
  },
  titleRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "flex-start",
    marginBottom: spacing.md,
  },
  titleInfo: {
    flex: 1,
    paddingRight: spacing.md,
  },
  title: {
    ...typography.h1,
    color: colors.text,
    fontSize: 29,
    letterSpacing: 0,
  },
  category: {
    ...typography.bodySmall,
    color: colors.secondary,
    marginTop: 5,
  },
  ratingBadge: {
    flexDirection: "row",
    alignItems: "center",
    backgroundColor: colors.secondary,
    paddingHorizontal: spacing.sm,
    paddingVertical: 6,
    borderRadius: borderRadius.md,
  },
  ratingText: {
    ...typography.bodySmall,
    fontWeight: "800",
    color: colors.background,
    marginLeft: 4,
  },
  tagsContainer: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: spacing.sm,
    marginBottom: spacing.lg,
  },
  tag: {
    backgroundColor: colors.surfaceHighlight,
    paddingHorizontal: spacing.md,
    paddingVertical: 6,
    borderRadius: borderRadius.full,
    borderWidth: 1,
    borderColor: colors.borderLight,
  },
  tagText: {
    ...typography.captionSmall,
    color: colors.textSecondary,
  },
  infoCard: {
    borderRadius: borderRadius.xl,
    borderWidth: 1,
    borderColor: colors.borderLight,
    backgroundColor: "rgba(22,22,26,0.9)",
    padding: spacing.md,
    marginBottom: spacing.xl,
  },
  infoRow: {
    flexDirection: "row",
    alignItems: "center",
    paddingVertical: spacing.sm,
  },
  infoIcon: {
    width: 34,
    height: 34,
    borderRadius: 17,
    alignItems: "center",
    justifyContent: "center",
    backgroundColor: colors.primaryLight,
    marginRight: spacing.md,
  },
  infoCopy: {
    flex: 1,
  },
  infoLabel: {
    ...typography.captionSmall,
    color: colors.textTertiary,
    textTransform: "none",
  },
  infoText: {
    ...typography.bodySmall,
    color: colors.text,
    marginTop: 2,
  },
  section: {
    borderTopWidth: 1,
    borderTopColor: colors.borderLight,
    paddingTop: spacing.lg,
    marginBottom: spacing.xl,
  },
  sectionTitle: {
    ...typography.h3,
    color: colors.text,
    marginBottom: spacing.sm,
  },
  description: {
    ...typography.body,
    color: colors.textSecondary,
    lineHeight: 26,
  },
  bottomBar: {
    position: "absolute",
    bottom: 0,
    left: 0,
    right: 0,
    padding: spacing.xl,
    paddingBottom: spacing.xxl,
    backgroundColor: colors.background,
    borderTopWidth: 1,
    borderTopColor: colors.borderLight,
    flexDirection: "row",
    alignItems: "center",
    gap: spacing.sm,
  },
  secondaryButton: {
    width: 54,
    height: 54,
    borderRadius: 27,
    backgroundColor: colors.surfaceLight,
    borderWidth: 1,
    borderColor: colors.borderLight,
    alignItems: "center",
    justifyContent: "center",
  },
  actionButton: {
    flex: 1,
    backgroundColor: colors.primary,
    flexDirection: "row",
    justifyContent: "center",
    alignItems: "center",
    height: 56,
    borderRadius: borderRadius.full,
    ...shadows.glow,
  },
  actionButtonText: {
    ...typography.button,
    color: colors.background,
    marginLeft: spacing.sm,
  },
});
