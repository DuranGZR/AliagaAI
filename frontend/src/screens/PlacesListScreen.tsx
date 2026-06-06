import React, { useCallback, useEffect, useState, useMemo } from "react";
import {
  ActivityIndicator,
  FlatList,
  RefreshControl,
  StyleSheet,
  Text,
  TouchableOpacity,
  View,
} from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { Ionicons } from "@expo/vector-icons";
import { useNavigation } from "@react-navigation/native";

import { DataStatePanel } from "../components/DataStatePanel";
import { ReliableImage } from "../components/ReliableImage";
import { placeService } from "../services/api";
import { borderRadius, colors, spacing, typography } from "../theme";
import { Place } from "../types";
import { DataState, loadDataState } from "../utils/dataState";
import { categoryOfPlace, descriptionForPlace, imageForPlace, labelForPlaceCategory } from "../utils/placeDisplay";
import { useLocation } from "../context/LocationContext";
import { calculateDistance, formatDistance } from "../utils/location";

export function PlacesListScreen() {
  const navigation = useNavigation<any>();
  const [places, setPlaces] = useState<Place[]>([]);
  const [state, setState] = useState<DataState<Place[]> | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const { location, permissionStatus, requestPermission } = useLocation();

  useEffect(() => {
    if (permissionStatus === "undetermined") {
      void requestPermission();
    }
  }, [permissionStatus, requestPermission]);

  const sortedPlaces = useMemo(() => {
    if (!location) return places;
    const mapped = places.map((item) => {
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
  }, [places, location]);

  const fetchPlaces = useCallback(async (isRefresh = false) => {
    if (isRefresh) {
      setRefreshing(true);
    } else {
      setLoading(true);
    }

    const dataState = await loadDataState(() => placeService.getAll(undefined, 500), [] as Place[]);
    setState(dataState);
    setPlaces(dataState.data || []);
    setLoading(false);
    setRefreshing(false);
  }, []);

  useEffect(() => {
    void fetchPlaces();
  }, [fetchPlaces]);

  const renderItem = ({ item }: { item: Place }) => {
    const category = item.category || labelForPlaceCategory(categoryOfPlace(item));
    const distanceStr = (item as any).distance !== undefined
      ? formatDistance((item as any).distance)
      : null;

    return (
      <TouchableOpacity
        style={styles.placeCard}
        activeOpacity={0.88}
        onPress={() => navigation.navigate("PlaceDetail", { ...item })}
      >
        <View style={styles.imageContainer}>
          <ReliableImage
            uri={item.image_url}
            fallbackUri={imageForPlace({ ...item, image_url: null })}
            style={styles.image}
            resizeMode="cover"
            label="Mekan"
          />
        </View>
        <View style={styles.infoContainer}>
          <View style={styles.headerRow}>
            <Text style={styles.category} numberOfLines={1}>
              {category.toLocaleUpperCase("tr-TR")}
            </Text>
            {distanceStr && (
              <View style={styles.distanceBadge}>
                <Ionicons name="location-sharp" size={10} color={colors.primary} />
                <Text style={styles.distanceText}>{distanceStr}</Text>
              </View>
            )}
          </View>
          <Text style={styles.name} numberOfLines={2}>
            {item.name}
          </Text>
          <View style={styles.addressRow}>
            <Ionicons name="location" size={14} color={colors.primary} />
            <Text style={styles.address} numberOfLines={1}>
              {item.address || "Aliağa"}
            </Text>
          </View>
          <Text style={styles.description} numberOfLines={2}>
            {descriptionForPlace(item)}
          </Text>
        </View>
      </TouchableOpacity>
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
            <Text style={styles.headerTitle}>Keşif Rotaları</Text>
            <Text style={styles.headerSub}>{places.length > 0 ? `${places.length} mekan kaydı` : "Mekan verisi"}</Text>
          </View>
          <View style={{ width: 40 }} />
        </View>

        {loading ? (
          <View style={styles.center}>
            <ActivityIndicator size="large" color={colors.primary} />
          </View>
        ) : places.length === 0 ? (
          <View style={styles.center}>
            <DataStatePanel
              tone={state?.status === "error" ? "warning" : "info"}
              title={state?.status === "error" ? "Mekan verisi yenilenemedi" : "Mekan kaydı bulunamadı"}
              text={
                state?.status === "error"
                  ? "Kaynak cevap vermedi. Aşağı çekerek tekrar deneyebilirsin."
                  : "Yeni mekan verisi geldiğinde bu liste otomatik dolacak."
              }
            />
          </View>
        ) : (
          <FlatList
            data={sortedPlaces}
            keyExtractor={(item) => item.id.toString()}
            renderItem={renderItem}
            contentContainerStyle={styles.listContent}
            showsVerticalScrollIndicator={false}
            refreshControl={
              <RefreshControl
                refreshing={refreshing}
                onRefresh={() => void fetchPlaces(true)}
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
  },
  headerSub: {
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
    width: 112,
    minHeight: 132,
    backgroundColor: colors.surfaceLight,
  },
  image: {
    width: "100%",
    height: "100%",
  },
  infoContainer: {
    flex: 1,
    padding: spacing.md,
    justifyContent: "center",
  },
  headerRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: spacing.xs,
  },
  category: {
    ...typography.captionSmall,
    color: colors.primary,
    flex: 1,
    marginRight: spacing.xs,
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
  name: {
    ...typography.bodyMedium,
    color: colors.text,
    marginBottom: spacing.xs,
    fontWeight: "800",
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
  description: {
    ...typography.captionSmall,
    color: colors.textTertiary,
    marginTop: spacing.xs,
    textTransform: "none",
  },
});
