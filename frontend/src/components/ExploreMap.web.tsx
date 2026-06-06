import React, { useMemo, useEffect, useRef } from "react";
import {
  Linking,
  StyleSheet,
  Text,
  View,
  TouchableOpacity,
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

// ── Web Harita Bileşeni ────────────────────────────────────────────────
export function ExploreMap({ places, selectedFilter, routes, activeRouteId }: ExploreMapProps) {
  const mapRef = useRef<HTMLDivElement>(null);
  const leafletMapInstance = useRef<any>(null);

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

  const displayPlaces = useMemo(() => {
    return filteredPlaces.slice(0, 50);
  }, [filteredPlaces]);


  // Leaflet kütüphanesini ve stilini dinamik olarak yükle ve haritayı çiz
  useEffect(() => {
    if (typeof window === "undefined" || !mapRef.current) return;

    // 1. CSS Ekle
    let cssLink = document.getElementById("leaflet-css") as HTMLLinkElement;
    if (!cssLink) {
      cssLink = document.createElement("link");
      cssLink.id = "leaflet-css";
      cssLink.rel = "stylesheet";
      cssLink.href = "https://unpkg.com/leaflet@1.9.4/dist/leaflet.css";
      document.head.appendChild(cssLink);
    }

    // 2. Özel Pin ve Pop-up stillerini ekle (Black & Gold ve Mikro-Animasyonlar için)
    let popupStyle = document.getElementById("leaflet-custom-popup-style") as HTMLStyleElement;
    if (!popupStyle) {
      popupStyle = document.createElement("style");
      popupStyle.id = "leaflet-custom-popup-style";
      popupStyle.innerHTML = `
        /* Pop-up stilleri */
        .custom-leaflet-popup .leaflet-popup-content-wrapper {
          background: rgba(20, 20, 24, 0.98) !important;
          border: 1px solid rgba(200, 169, 110, 0.32) !important;
          box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37) !important;
          border-radius: 12px !important;
          color: #ffffff !important;
          padding: 0 !important;
          overflow: hidden;
        }
        .custom-leaflet-popup .leaflet-popup-content {
          margin: 0 !important;
          padding: 12px !important;
          line-height: 1.4;
        }
        .custom-leaflet-popup .leaflet-popup-tip {
          background: rgba(20, 20, 24, 0.98) !important;
          border-left: 1px solid rgba(200, 169, 110, 0.32) !important;
          border-bottom: 1px solid rgba(200, 169, 110, 0.32) !important;
          box-shadow: none !important;
        }
        .leaflet-control-attribution {
          background: rgba(10, 10, 10, 0.7) !important;
          color: rgba(255, 255, 255, 0.4) !important;
          font-size: 9px !important;
        }
        .leaflet-control-attribution a {
          color: #C8A96E !important;
        }
        .leaflet-bar, .leaflet-touch .leaflet-bar {
          border: 1px solid rgba(200, 169, 110, 0.4) !important;
          box-shadow: 0 4px 12px rgba(0, 0, 0, 0.5) !important;
          border-radius: 8px !important;
          overflow: hidden !important;
        }
        .leaflet-bar a, .leaflet-touch .leaflet-bar a {
          background-color: #141418 !important;
          color: #C8A96E !important;
          border-bottom: 1px solid rgba(200, 169, 110, 0.2) !important;
          border-top: none !important;
          border-left: none !important;
          border-right: none !important;
        }
        .leaflet-bar a:hover, .leaflet-touch .leaflet-bar a:hover {
          background-color: #C8A96E !important;
          color: #0A0A0A !important;
        }
        .leaflet-touch .leaflet-bar a {
          width: 32px !important;
          height: 32px !important;
          line-height: 30px !important;
        }

        /* Özel Premium Pin Stilleri */
        .custom-marker-wrapper {
          position: relative;
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          width: 30px;
          height: 35px;
          filter: drop-shadow(0px 4px 6px rgba(0, 0, 0, 0.35));
        }
        .custom-marker-body {
          width: 28px;
          height: 28px;
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          border: 2px solid #ffffff;
          box-shadow: 0 0 10px rgba(0, 0, 0, 0.5);
          color: #ffffff;
          font-size: 13px;
          font-weight: bold;
          transition: transform 0.2s ease-in-out;
        }
        .custom-marker-wrapper:hover .custom-marker-body {
          transform: scale(1.15);
        }
        .custom-marker-tip {
          width: 0;
          height: 0;
          border-left: 5px solid transparent;
          border-right: 5px solid transparent;
          margin-top: -1px;
        }

        /* Başlangıç/Bitiş Rota Animasyonları */
        .route-pulse-marker {
          width: 14px;
          height: 14px;
          border-radius: 50%;
          border: 2px solid #ffffff;
        }
        .pulse-green {
          background-color: #4CAF50;
          box-shadow: 0 0 0 0 rgba(76, 175, 80, 0.7);
          animation: pulse-green-anim 1.8s infinite;
        }
        .pulse-red {
          background-color: #EF4444;
          box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.7);
          animation: pulse-red-anim 1.8s infinite;
        }
        @keyframes pulse-green-anim {
          0% { box-shadow: 0 0 0 0 rgba(76, 175, 80, 0.7); }
          70% { box-shadow: 0 0 0 8px rgba(76, 175, 80, 0); }
          100% { box-shadow: 0 0 0 0 rgba(76, 175, 80, 0); }
        }
        @keyframes pulse-red-anim {
          0% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.7); }
          70% { box-shadow: 0 0 0 8px rgba(239, 68, 68, 0); }
          100% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0); }
        }
      `;
      document.head.appendChild(popupStyle);
    }

    const unicodeIconForCategory = (cat: PlaceDisplayCategory): string => {
      const map: Record<PlaceDisplayCategory, string> = {
        history: "🏛️",
        food: "🍴",
        coast: "🌊",
        park: "🌳",
        culture: "🎨",
        shopping: "🛍️",
        service: "🔧",
        other: "📍",
      };
      return map[cat] || "📍";
    };

    const initMap = () => {
      const L = (window as any).L;
      if (!L || !mapRef.current) return;

      // Eski harita örneğini temizle
      if (leafletMapInstance.current) {
        leafletMapInstance.current.remove();
        leafletMapInstance.current = null;
      }

      // Başlangıç koordinatı (Aliağa Merkez)
      let initialLat = 38.7950;
      let initialLng = 26.9760;
      let initialZoom = 12;

      // Eğer aktif bir rota varsa, haritayı rotanın ortasına taşı
      if (activeRoute && activeRoute.coordinates.length > 0) {
        const lats = activeRoute.coordinates.map(c => c.latitude);
        const lngs = activeRoute.coordinates.map(c => c.longitude);
        initialLat = (Math.min(...lats) + Math.max(...lats)) / 2;
        initialLng = (Math.min(...lngs) + Math.max(...lngs)) / 2;
        initialZoom = 13;
      }

      const map = L.map(mapRef.current, {
        zoomControl: true,
        attributionControl: true
      }).setView([initialLat, initialLng], initialZoom);
      
      leafletMapInstance.current = map;

      // CartoDB Dark Matter - Koyu Tema Harita Katmanı
      L.tileLayer("https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png", {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
        subdomains: 'abcd',
        maxZoom: 20
      }).addTo(map);

      // ── Mekan Pinlerini Ekle ──────────────────────────────────────────
      displayPlaces.forEach((place) => {
        if (!place.latitude || !place.longitude) return;

        const color = markerColorForPlace(place);
        const iconEmoji = unicodeIconForCategory(categoryOfPlace(place));
        const customIcon = L.divIcon({
          className: "custom-div-icon",
          html: `
            <div class="custom-marker-wrapper">
              <div class="custom-marker-body" style="background-color: ${color};">
                ${iconEmoji}
              </div>
              <div class="custom-marker-tip" style="border-top: 5px solid ${color};"></div>
            </div>
          `,
          iconSize: [30, 35],
          iconAnchor: [15, 35]
        });

        const marker = L.marker([place.latitude, place.longitude], { icon: customIcon }).addTo(map);

        const popupEl = document.createElement("div");
        popupEl.style.fontFamily = "'Plus Jakarta Sans', 'Outfit', sans-serif";
        popupEl.style.width = "220px";
        popupEl.innerHTML = `
          <div style="display: flex; align-items: center; gap: 6px; margin-bottom: 4px;">
            <span style="color: ${color}; font-weight: bold; font-size: 13px;">●</span>
            <div style="font-weight: 700; font-size: 13px; color: #ffffff; text-overflow: ellipsis; overflow: hidden; white-space: nowrap; max-width: 180px;">${place.name}</div>
          </div>
          <div style="font-size: 11px; color: rgba(200, 169, 110, 0.85); margin-bottom: 6px; font-weight: 500;">${labelForPlaceCategory(categoryOfPlace(place))}</div>
          ${place.description ? `
            <div style="font-size: 11px; color: rgba(255,255,255,0.75); margin-bottom: 10px; line-height: 1.4; max-height: 80px; overflow-y: auto; word-break: break-word; padding-right: 2px;">
              ${place.description}
            </div>
          ` : ""}
          <button id="dir-btn-${place.id}" style="width: 100%; border: none; background-color: #C8A96E; color: #0A0A0A; padding: 6px 10px; border-radius: 6px; font-size: 11px; font-weight: bold; cursor: pointer; display: flex; align-items: center; justify-content: center; gap: 4px; transition: background-color 0.2s; outline: none;">
            🗺️ Yol Tarifi Al
          </button>
        `;

        marker.bindPopup(popupEl, {
          className: "custom-leaflet-popup",
          closeButton: false
        });

        // Pop-up açıldığında Yol Tarifi butonuna tıklama olayını bağla
        marker.on("popupopen", () => {
          const btn = document.getElementById(`dir-btn-${place.id}`);
          if (btn) {
            btn.addEventListener("click", () => {
              const url = `https://www.google.com/maps/dir/?api=1&destination=${place.latitude},${place.longitude}`;
              window.open(url, "_blank");
            });
          }
        });
      });

      // ── Aktif Rotayı Çiz ──────────────────────────────────────────────
      if (activeRoute && activeRoute.coordinates.length >= 2) {
        const latLngs = activeRoute.coordinates.map(c => [c.latitude, c.longitude]);

        // Başlangıç Pini (Pulse Animasyonlu)
        L.marker(latLngs[0], {
          icon: L.divIcon({
            className: "start-marker-pulse",
            html: `<div class="route-pulse-marker pulse-green"></div>`,
            iconSize: [14, 14],
            iconAnchor: [7, 7]
          })
        }).addTo(map).bindPopup("<div style='font-family: sans-serif; font-size: 11px; font-weight: bold; color: #4CAF50;'>🟢 Başlangıç Noktası</div>", { className: "custom-leaflet-popup", closeButton: false });

        // Bitiş Pini (Pulse Animasyonlu)
        L.marker(latLngs[latLngs.length - 1], {
          icon: L.divIcon({
            className: "end-marker-pulse",
            html: `<div class="route-pulse-marker pulse-red"></div>`,
            iconSize: [14, 14],
            iconAnchor: [7, 7]
          })
        }).addTo(map).bindPopup("<div style='font-family: sans-serif; font-size: 11px; font-weight: bold; color: #EF4444;'>🔴 Bitiş Noktası</div>", { className: "custom-leaflet-popup", closeButton: false });

        // Rota çizgisi (Altın sarısı)
        L.polyline(latLngs, {
          color: colors.primary,
          weight: 5,
          opacity: 0.85,
          lineJoin: "round"
        }).addTo(map);

        // Haritayı rotaya sığdır
        map.fitBounds(latLngs, { padding: [50, 50] });
      } else if (displayPlaces.length > 0) {
        // ── Haritayı Mekanlara Otomatik Odakla (Auto Zoom) ──────────────────
        const bounds = displayPlaces
          .filter(p => p.latitude && p.longitude)
          .map(p => [p.latitude, p.longitude]);
        if (bounds.length > 0) {
          map.fitBounds(bounds, { padding: [60, 60], maxZoom: 15 });
        }
      }
    };

    // Script zaten yüklü ise doğrudan başlat
    let jsScript = document.getElementById("leaflet-js") as HTMLScriptElement;
    if (!jsScript) {
      jsScript = document.createElement("script");
      jsScript.id = "leaflet-js";
      jsScript.src = "https://unpkg.com/leaflet@1.9.4/dist/leaflet.js";
      jsScript.onload = initMap;
      document.head.appendChild(jsScript);
    } else {
      if ((window as any).L) {
        initMap();
      } else {
        jsScript.addEventListener("load", initMap);
      }
    }

    return () => {
      if (leafletMapInstance.current) {
        leafletMapInstance.current.remove();
        leafletMapInstance.current = null;
      }
    };
  }, [displayPlaces, activeRoute]);

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <View style={styles.headerLeft}>
          <Ionicons name="map-outline" size={16} color={colors.primary} />
          <Text style={styles.headerTitle}>
            {selectedFilter === "route" ? "Rota Görünümü" : "Harita (Web)"}
          </Text>
        </View>
        <View style={styles.fitButton}>
          <Ionicons name="location-outline" size={14} color={colors.primary} />
          <Text style={styles.fitText}>
            {selectedFilter === "route" && activeRoute 
              ? `${activeRoute.coordinates.length} durak`
              : `${filteredPlaces.length} nokta`
            }
          </Text>
        </View>
      </View>
      <View style={styles.mapWrap}>
        <div 
          ref={mapRef} 
          style={{ 
            width: "100%", 
            height: "100%", 
            backgroundColor: "#0A0A0C",
            backgroundImage: "radial-gradient(rgba(200, 169, 110, 0.08) 1.2px, transparent 1.2px)",
            backgroundSize: "24px 24px",
            zIndex: 1
          }} 
        />
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
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.md,
    borderBottomWidth: 1,
    borderBottomColor: "rgba(200,169,110,0.10)",
  },
  headerLeft: { 
    flexDirection: "row", 
    alignItems: "center", 
    gap: spacing.xs 
  },
  headerTitle: { 
    ...typography.captionSmall, 
    color: colors.primary, 
    letterSpacing: 1.2 
  },
  fitButton: {
    flexDirection: "row",
    alignItems: "center",
    gap: 4,
    paddingHorizontal: spacing.sm,
    paddingVertical: 6,
    borderRadius: borderRadius.full,
    borderWidth: 1,
    borderColor: "rgba(200,169,110,0.28)",
    backgroundColor: "rgba(200,169,110,0.08)",
  },
  fitText: { 
    ...typography.captionSmall, 
    color: colors.primary 
  },
  // Web harita kapsayıcısı
  mapWrap: { 
    height: 340, 
    position: "relative" as any 
  },
});
