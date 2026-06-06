import React, { useMemo } from "react";
import {
  Linking,
  Platform,
  StyleSheet,
  Text,
  View,
} from "react-native";
import { Ionicons } from "@expo/vector-icons";

import { Place } from "../types";
import { colors, markerColors, borderRadius, spacing, typography } from "../theme";
import { categoryOfPlace, labelForPlaceCategory } from "../utils/placeDisplay";
import type { PlaceDisplayCategory } from "../utils/placeDisplay";

// ── Rota tipleri ──────────────────────────────────────────────────────
export interface RouteCoordinate {
  latitude: number;
  longitude: number;
}

export interface MapRoute {
  id: string;
  title: string;
  icon: string;
  duration: string;
  coordinates: RouteCoordinate[];
}

// ── Props ─────────────────────────────────────────────────────────────
interface ExploreMapProps {
  places: Place[];
  selectedFilter: string;
  routes: MapRoute[];
  activeRouteId?: string | null;
}

// ── react-native-maps (mobil + web) ─────────────────────────────────
import MapView, { Callout as CalloutC, Marker as MarkerC, Polyline as PolylineC } from "react-native-maps";

// ── Yardımcılar ──────────────────────────────────────────────────────
function markerColorForPlace(place: Place): string {
  const cat = categoryOfPlace(place);
  return markerColors[cat] || markerColors.default;
}

function pinIconForCategory(cat: PlaceDisplayCategory): keyof typeof Ionicons.glyphMap {
  const map: Record<PlaceDisplayCategory, keyof typeof Ionicons.glyphMap> = {
    history: "business-outline", food: "restaurant-outline", coast: "water-outline",
    park: "leaf-outline", culture: "color-palette-outline", shopping: "cart-outline",
    service: "construct-outline", other: "ellipsis-horizontal-outline",
  };
  return map[cat] || "location-outline";
}

function openDirections(place: Place) {
  const label = encodeURIComponent(`${place.name} ${place.address || "Aliağa"}`);
  let url: string;
  if (Platform.OS === "ios") {
    url = `maps://?daddr=${label}`;
  } else {
    url = `https://www.google.com/maps/dir/?api=1&destination=${label}`;
  }
  Linking.openURL(url).catch(() => {
    const fb = `https://www.google.com/maps/dir/?api=1&destination=${label}`;
    Linking.openURL(fb);
  });
}

// ── Ana bileşen ──────────────────────────────────────────────────────
export function ExploreMap({ places, selectedFilter, routes, activeRouteId }: ExploreMapProps) {
  const filteredPlaces = useMemo(() => {
    return places.filter((p) => {
      if (!p.latitude || !p.longitude) return false;
      if (selectedFilter === "all") return true;
      if (selectedFilter === "events" || selectedFilter === "route") return false;
      const cat = categoryOfPlace(p);
      if (selectedFilter === "coast") {
        return cat === "coast" || cat === "park";
      }
      return cat === selectedFilter;
    });
  }, [places, selectedFilter]);

  const activeRoute = useMemo(() => {
    if (selectedFilter !== "route") return null;
    if (activeRouteId) {
      return routes.find((r) => r.id === activeRouteId) || (routes.length > 0 ? routes[0] : null);
    }
    return routes.length > 0 ? routes[0] : null;
  }, [selectedFilter, routes, activeRouteId]);

  // Rota bölgesi
  const routeRegion = useMemo(() => {
    if (!activeRoute || activeRoute.coordinates.length === 0) return null;
    const coords = activeRoute.coordinates;
    const lats = coords.map((c) => c.latitude);
    const lngs = coords.map((c) => c.longitude);
    return {
      latitude: (Math.min(...lats) + Math.max(...lats)) / 2,
      longitude: (Math.min(...lngs) + Math.max(...lngs)) / 2,
      latitudeDelta: (Math.max(...lats) - Math.min(...lats)) * 1.5 || 0.05,
      longitudeDelta: (Math.max(...lngs) - Math.min(...lngs)) * 1.5 || 0.05,
    };
  }, [activeRoute]);

  const initialRegion = routeRegion || {
    latitude: 38.7950,
    longitude: 26.9760,
    latitudeDelta: 0.12,
    longitudeDelta: 0.12,
  };

  const displayPlaces = filteredPlaces.slice(0, 50);

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <View style={styles.headerLeft}>
          <Ionicons name="map-outline" size={16} color={colors.primary} />
          <Text style={styles.headerTitle}>
            {selectedFilter === "route" ? "Rota Görünümü" : "Harita"}
          </Text>
        </View>
        <View style={styles.fitButton}>
          <Ionicons name="location-outline" size={14} color={colors.primary} />
          <Text style={styles.fitText}>{filteredPlaces.length} nokta</Text>
        </View>
      </View>
      <View style={styles.mapWrap}>
        <MapView
          style={styles.map}
          initialRegion={initialRegion}
          showsUserLocation={false}
          showsCompass
          showsScale
          toolbarEnabled={false}
        >
          {displayPlaces.map((place: Place) => (
            <MarkerC
              key={`p-${place.id}`}
              coordinate={{ latitude: place.latitude!, longitude: place.longitude! }}
              pinColor={markerColorForPlace(place)}
            >
              <CalloutC tooltip onPress={() => openDirections(place)}>
                <View style={styles.callout}>
                  <View style={styles.calloutHeader}>
                    <Ionicons name={pinIconForCategory(categoryOfPlace(place))} size={14} color={markerColorForPlace(place)} />
                    <Text style={styles.calloutTitle} numberOfLines={1}>{place.name}</Text>
                  </View>
                  <Text style={styles.calloutCategory}>{labelForPlaceCategory(categoryOfPlace(place))}</Text>
                  {place.description ? (
                    <Text style={styles.calloutDesc} numberOfLines={3}>{place.description}</Text>
                  ) : null}
                  <View style={styles.calloutAction}>
                    <Ionicons name="navigate-outline" size={13} color={colors.background} />
                    <Text style={styles.calloutActionText}>Yol Tarifi</Text>
                  </View>
                </View>
              </CalloutC>
            </MarkerC>
          ))}
          {activeRoute && activeRoute.coordinates.length >= 2 && (
            <>
              <MarkerC coordinate={activeRoute.coordinates[0]} pinColor="#4CAF50" title="Başlangıç" />
              <MarkerC coordinate={activeRoute.coordinates[activeRoute.coordinates.length - 1]} pinColor="#EF4444" title="Bitiş" />
              <PolylineC coordinates={activeRoute.coordinates} strokeColor={colors.primary} strokeWidth={3} />
            </>
          )}
        </MapView>
      </View>
    </View>
  );
}

// ── Stiller ───────────────────────────────────────────────────────────
const styles = StyleSheet.create({
  container: {
    marginBottom: spacing.lg,
    borderRadius: borderRadius.xl,
    borderWidth: 1,
    borderColor: "rgba(200,169,110,0.18)",
    overflow: "hidden",
    backgroundColor: "rgba(20,20,24,0.96)",
  },
  // Header
  header: {
    flexDirection: "row", alignItems: "center", justifyContent: "space-between",
    paddingHorizontal: spacing.lg, paddingVertical: spacing.md,
    borderBottomWidth: 1, borderBottomColor: "rgba(200,169,110,0.10)",
  },
  headerLeft: { flexDirection: "row", alignItems: "center", gap: spacing.xs },
  headerTitle: { ...typography.captionSmall, color: colors.primary, letterSpacing: 1.2 },
  fitButton: {
    flexDirection: "row", alignItems: "center", gap: 4,
    paddingHorizontal: spacing.sm, paddingVertical: 6, borderRadius: borderRadius.full,
    borderWidth: 1, borderColor: "rgba(200,169,110,0.28)", backgroundColor: "rgba(200,169,110,0.08)",
  },
  fitText: { ...typography.captionSmall, color: colors.primary },
  // Mobil harita
  mapWrap: { height: 340, position: "relative" as const },
  map: { flex: 1 },
  // Callout
  callout: {
    width: 220, backgroundColor: "rgba(20,20,24,0.98)", borderRadius: borderRadius.lg,
    borderWidth: 1, borderColor: "rgba(200,169,110,0.32)", padding: spacing.md,
  },
  calloutHeader: { flexDirection: "row", alignItems: "center", gap: spacing.xs, marginBottom: 4 },
  calloutTitle: { ...typography.bodySmall, color: colors.text, fontWeight: "700", flex: 1 },
  calloutCategory: { ...typography.captionSmall, color: colors.primary, marginBottom: spacing.xs, fontWeight: "500" },
  calloutDesc: { ...typography.captionSmall, color: colors.textSecondary, marginBottom: spacing.sm, fontSize: 10, lineHeight: 13, opacity: 0.8 },
  calloutAction: {
    flexDirection: "row", alignItems: "center", justifyContent: "center", gap: 4,
    backgroundColor: colors.primary, paddingVertical: 8, paddingHorizontal: spacing.sm, borderRadius: borderRadius.md,
  },
  calloutActionText: { ...typography.captionSmall, color: colors.background, fontWeight: "700" },
});
