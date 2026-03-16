import React from "react";
import { View, Text, StyleSheet, TouchableOpacity, Linking } from "react-native";
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
    <View style={styles.card}>
      <View style={styles.header}>
        <View style={styles.titleRow}>
          <Text style={styles.name} numberOfLines={2}>
            {name}
          </Text>
          {rating != null && (
            <View style={styles.ratingBadge}>
              <Ionicons name="star" size={12} color="#FCD34D" />
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
          <Ionicons name="location-outline" size={14} color={colors.textSecondary} />
          <Text style={styles.infoText} numberOfLines={2}>
            {address}
          </Text>
        </View>
      )}

      {tags && tags.length > 0 && (
        <View style={styles.tagsRow}>
          {tags.slice(0, 4).map((tag) => (
            <View key={tag} style={styles.tag}>
              <Text style={styles.tagText}>{tag}</Text>
            </View>
          ))}
        </View>
      )}

      <View style={styles.actions}>
        {phone && (
          <TouchableOpacity style={styles.actionButton} onPress={handleCall}>
            <Ionicons name="call-outline" size={16} color={colors.primary} />
            <Text style={styles.actionText}>Ara</Text>
          </TouchableOpacity>
        )}
        {maps_link && (
          <TouchableOpacity style={styles.actionButton} onPress={handleMap}>
            <Ionicons name="navigate-outline" size={16} color={colors.primary} />
            <Text style={styles.actionText}>Yol Tarifi</Text>
          </TouchableOpacity>
        )}
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: colors.surface,
    borderRadius: borderRadius.md,
    padding: spacing.lg,
    marginBottom: spacing.md,
    ...shadows.md,
  },
  header: {
    marginBottom: spacing.sm,
  },
  titleRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "flex-start",
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
    backgroundColor: "#FEF3C7",
    paddingHorizontal: spacing.sm,
    paddingVertical: 2,
    borderRadius: borderRadius.sm,
    gap: 2,
  },
  ratingText: {
    ...typography.caption,
    fontWeight: "600",
    color: "#92400E",
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
    fontWeight: "500",
  },
  infoRow: {
    flexDirection: "row",
    alignItems: "flex-start",
    marginBottom: spacing.xs,
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
    marginTop: spacing.sm,
  },
  tag: {
    backgroundColor: colors.borderLight,
    paddingHorizontal: spacing.sm,
    paddingVertical: 2,
    borderRadius: borderRadius.full,
  },
  tagText: {
    ...typography.caption,
    color: colors.textSecondary,
  },
  actions: {
    flexDirection: "row",
    gap: spacing.md,
    marginTop: spacing.md,
    paddingTop: spacing.md,
    borderTopWidth: 1,
    borderTopColor: colors.borderLight,
  },
  actionButton: {
    flexDirection: "row",
    alignItems: "center",
    gap: spacing.xs,
  },
  actionText: {
    ...typography.bodySmall,
    color: colors.primary,
    fontWeight: "500",
  },
});
