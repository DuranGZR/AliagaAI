import React from "react";
import { View, Text, StyleSheet, TouchableOpacity, Linking, Platform } from "react-native";
import { BlurView } from "expo-blur";
import { Ionicons } from "@expo/vector-icons";
import { colors, spacing, borderRadius, shadows, typography } from "../theme";

interface PlaceCardProps {
  name: string;
  category?: string | null;
  address?: string | null;
  phone?: string | null;
  rating?: number | null;
  tags?: string[] | null;
  maps_link?: string | null;
}

export function PlaceCard({
  name,
  category,
  address,
  phone,
  rating,
  tags,
  maps_link,
}: PlaceCardProps) {
  const handleCall = () => {
    if (phone) Linking.openURL(`tel:${phone}`);
  };

  const handleMap = () => {
    if (maps_link) Linking.openURL(maps_link);
  };

  return (
    <View style={styles.cardContainer}>
      <BlurView intensity={60} tint="light" style={styles.card}>
        <View style={styles.header}>
          <View style={styles.titleRow}>
            <Text style={styles.name} numberOfLines={1}>
              {name}
            </Text>
            {rating != null && (
              <View style={styles.ratingBadge}>
                <Ionicons name="star" size={12} color="#F59E0B" />
                <Text style={styles.ratingText}>{rating.toFixed(1)}</Text>
              </View>
            )}
          </View>
          {category && (
            <View style={styles.categoryBadge}>
              <Text style={styles.categoryText}>{category}</Text>
            </View>
          )}
        </View>

        {address && (
          <View style={styles.infoRow}>
            <Ionicons name="location-sharp" size={14} color={colors.primary} />
            <Text style={styles.infoText} numberOfLines={1}>
              {address}
            </Text>
          </View>
        )}

        {tags && tags.length > 0 && (
          <View style={styles.tagsRow}>
            {tags.slice(0, 3).map((tag) => (
              <View key={tag} style={styles.tag}>
                <Text style={styles.tagText}>{tag}</Text>
              </View>
            ))}
          </View>
        )}

        <View style={styles.actions}>
          {phone && (
            <TouchableOpacity style={styles.actionButton} onPress={handleCall}>
              <Ionicons name="call" size={16} color={colors.primary} />
              <Text style={styles.actionText}>Ara</Text>
            </TouchableOpacity>
          )}
          {maps_link && (
            <TouchableOpacity style={[styles.actionButton, styles.primaryAction]} onPress={handleMap}>
              <Ionicons name="navigate" size={16} color="white" />
              <Text style={[styles.actionText, styles.primaryActionText]}>Yol Tarifi</Text>
            </TouchableOpacity>
          )}
        </View>
      </BlurView>
    </View>
  );
}

const styles = StyleSheet.create({
  cardContainer: {
    marginBottom: spacing.md,
    ...shadows.soft,
  },
  card: {
    borderRadius: borderRadius.xl,
    padding: spacing.lg,
    backgroundColor: "rgba(255, 255, 255, 0.7)",
    borderWidth: 1,
    borderColor: colors.borderLight,
    overflow: "hidden",
  },
  header: {
    marginBottom: spacing.md,
  },
  titleRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
  },
  name: {
    ...typography.h3,
    color: colors.text,
    flex: 1,
    marginRight: spacing.sm,
  },
  ratingBadge: {
    flexDirection: "row",
    alignItems: "center",
    backgroundColor: "rgba(245, 158, 11, 0.1)",
    paddingHorizontal: spacing.sm,
    paddingVertical: 4,
    borderRadius: borderRadius.sm,
    gap: 4,
  },
  ratingText: {
    ...typography.caption,
    fontWeight: "700",
    color: "#B45309",
  },
  categoryBadge: {
    alignSelf: "flex-start",
    backgroundColor: colors.primaryLight,
    paddingHorizontal: spacing.sm,
    paddingVertical: 2,
    borderRadius: borderRadius.sm,
    marginTop: spacing.xs,
  },
  categoryText: {
    ...typography.caption,
    color: colors.primary,
    fontWeight: "600",
    textTransform: "uppercase",
    letterSpacing: 0.5,
  },
  infoRow: {
    flexDirection: "row",
    alignItems: "center",
    marginBottom: spacing.sm,
    gap: spacing.xs,
  },
  infoText: {
    ...typography.bodySmall,
    color: colors.textSecondary,
    flex: 1,
  },
  tagsRow: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: spacing.xs,
    marginBottom: spacing.md,
  },
  tag: {
    backgroundColor: "rgba(148, 163, 184, 0.1)",
    paddingHorizontal: spacing.sm,
    paddingVertical: 4,
    borderRadius: borderRadius.full,
  },
  tagText: {
    fontSize: 10,
    fontWeight: "600",
    color: colors.textSecondary,
  },
  actions: {
    flexDirection: "row",
    gap: spacing.sm,
    marginTop: spacing.sm,
  },
  actionButton: {
    flex: 1,
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "center",
    gap: spacing.xs,
    paddingVertical: spacing.md,
    borderRadius: borderRadius.md,
    backgroundColor: "white",
    borderWidth: 1,
    borderColor: colors.border,
  },
  primaryAction: {
    backgroundColor: colors.primary,
    borderColor: colors.primary,
  },
  actionText: {
    ...typography.bodySmall,
    color: colors.primary,
    fontWeight: "700",
  },
  primaryActionText: {
    color: "white",
  },
});
