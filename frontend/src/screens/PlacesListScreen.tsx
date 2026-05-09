import React, { useEffect, useState } from "react";
import {
  View,
  StyleSheet,
  Text,
  TouchableOpacity,
  FlatList,
  ActivityIndicator,
  Image,
} from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { Ionicons } from "@expo/vector-icons";
import { useNavigation } from "@react-navigation/native";

import { colors, spacing, typography, borderRadius } from "../theme";
import { placeService } from "../services/api";
import { Place } from "../types";

export function PlacesListScreen() {
  const navigation = useNavigation<any>();
  const [places, setPlaces] = useState<Place[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchPlaces = async () => {
      try {
        const data = await placeService.getAll();
        setPlaces(data || []);
      } catch (error) {
        console.error("Mekanlar çekilirken hata:", error);
      } finally {
        setLoading(false);
      }
    };
    fetchPlaces();
  }, []);

  const renderItem = ({ item }: { item: Place }) => (
    <TouchableOpacity
      style={styles.placeCard}
      onPress={() => navigation.navigate("PlaceDetail", { ...item })}
    >
      <View style={styles.imageContainer}>
        {item.image_url ? (
          <Image
            source={{ uri: item.image_url }}
            style={styles.image}
            resizeMode="cover"
          />
        ) : (
          <View style={styles.imageFallback}>
            <Ionicons name="image-outline" size={32} color={colors.textTertiary} />
          </View>
        )}
      </View>
      <View style={styles.infoContainer}>
        <Text style={styles.category} numberOfLines={1}>
          {item.category?.toUpperCase() || "MEKAN"}
        </Text>
        <Text style={styles.name} numberOfLines={2}>
          {item.name}
        </Text>
        <View style={styles.addressRow}>
          <Ionicons name="location" size={14} color={colors.primary} />
          <Text style={styles.address} numberOfLines={1}>
            {item.address || "Aliağa"}
          </Text>
        </View>
      </View>
    </TouchableOpacity>
  );

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
          <Text style={styles.headerTitle}>Keşif Rotaları</Text>
          <View style={{ width: 24 }} />
        </View>

        {loading ? (
          <View style={styles.center}>
            <ActivityIndicator size="large" color={colors.primary} />
          </View>
        ) : places.length === 0 ? (
          <View style={styles.center}>
            <Text style={styles.emptyText}>Henüz kayıtlı mekan bulunmuyor.</Text>
          </View>
        ) : (
          <FlatList
            data={places}
            keyExtractor={(item) => item.id.toString()}
            renderItem={renderItem}
            contentContainerStyle={styles.listContent}
            showsVerticalScrollIndicator={false}
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
  headerTitle: {
    ...typography.h3,
    color: colors.text,
  },
  center: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
  },
  emptyText: {
    ...typography.body,
    color: colors.textSecondary,
  },
  listContent: {
    padding: spacing.xl,
    paddingBottom: 100,
  },
  placeCard: {
    flexDirection: "row",
    backgroundColor: colors.surface,
    borderRadius: borderRadius.lg,
    overflow: "hidden",
    marginBottom: spacing.md,
    borderWidth: 1,
    borderColor: "rgba(255, 255, 255, 0.05)",
  },
  imageContainer: {
    width: 100,
    height: 100,
    backgroundColor: colors.surfaceLight,
  },
  image: {
    width: "100%",
    height: "100%",
  },
  imageFallback: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
    backgroundColor: "rgba(30, 30, 30, 0.9)",
  },
  infoContainer: {
    flex: 1,
    padding: spacing.md,
    justifyContent: "center",
  },
  category: {
    ...typography.captionSmall,
    color: colors.primary,
    marginBottom: spacing.xs,
  },
  name: {
    ...typography.bodyMedium,
    color: colors.text,
    marginBottom: spacing.xs,
  },
  addressRow: {
    flexDirection: "row",
    alignItems: "center",
    gap: spacing.xs,
  },
  address: {
    ...typography.caption,
    color: colors.textSecondary,
    flex: 1,
  },
});
