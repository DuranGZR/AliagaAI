import React, { useEffect, useMemo, useState } from "react";
import {
  ActivityIndicator,
  Image,
  ScrollView,
  StyleSheet,
  Text,
  TouchableOpacity,
  View,
} from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { LinearGradient } from "expo-linear-gradient";
import { Ionicons } from "@expo/vector-icons";
import { useNavigation } from "@react-navigation/native";

import { AppHeader } from "../components/AppHeader";
import { eventService, newsService, placeService } from "../services/api";
import { EventItem, NewsItem, Place } from "../types";
import { borderRadius, colors, spacing, typography } from "../theme";

function relativeTime(input?: string | null): string {
  if (!input) return "Bugün";
  const ts = new Date(input).getTime();
  if (!Number.isFinite(ts)) return "Bugün";
  const hours = Math.max(1, Math.floor((Date.now() - ts) / (1000 * 60 * 60)));
  if (hours < 24) return `${hours} saat önce`;
  const days = Math.floor(hours / 24);
  return days <= 1 ? "Dün" : `${days} gün önce`;
}

export function ExploreScreen() {
  const navigation = useNavigation<any>();
  const [loading, setLoading] = useState(true);
  const [events, setEvents] = useState<EventItem[]>([]);
  const [news, setNews] = useState<NewsItem[]>([]);
  const [places, setPlaces] = useState<Place[]>([]);

  useEffect(() => {
    const load = async () => {
      try {
        const [eventRows, newsRows, placeRows] = await Promise.all([
          eventService.getUpcoming(8),
          newsService.getAll(8),
          placeService.getAll(undefined, 20),
        ]);
        setEvents(eventRows || []);
        setNews(newsRows || []);
        setPlaces(placeRows || []);
      } catch (error) {
        console.error("explore_load_error", error);
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  const featuredEvent = events[0] || null;
  const routePlaces = useMemo(() => places.slice(0, 8), [places]);

  return (
    <View style={styles.container}>
      <SafeAreaView style={styles.safeArea} edges={["top"]}>
        <AppHeader />

        {loading ? (
          <View style={styles.loadingWrap}>
            <ActivityIndicator size="large" color={colors.primary} />
          </View>
        ) : (
          <ScrollView contentContainerStyle={styles.scrollContent} showsVerticalScrollIndicator={false}>
            <View style={styles.titleWrap}>
              <Text style={styles.pageTitle}>Keşfet</Text>
              <Text style={styles.pageSubtitle}>Aliağa'nın ritmini yakalayın.</Text>
            </View>

            {featuredEvent && (
              <TouchableOpacity style={styles.featuredCard} activeOpacity={0.9}>
                {featuredEvent.image_url ? (
                  <Image source={{ uri: featuredEvent.image_url }} style={styles.featuredImage} resizeMode="cover" />
                ) : (
                  <LinearGradient
                    colors={["rgba(56, 34, 16, 0.45)", "rgba(18, 18, 20, 0.95)"]}
                    style={styles.featuredImage}
                  />
                )}
                <LinearGradient colors={["transparent", "rgba(0,0,0,0.92)"]} style={styles.featuredOverlay} />

                <View style={styles.featuredChips}>
                  <View style={styles.chip}>
                    <Text style={styles.chipText}>ÖNE ÇIKAN ETKİNLİK</Text>
                  </View>
                  <View style={styles.chip}>
                    <Text style={styles.chipText}>BU HAFTA SONU</Text>
                  </View>
                </View>

                <View style={styles.featuredContent}>
                  <Text style={styles.featuredMeta}>BU HAFTA SONU</Text>
                  <Text style={styles.featuredTitle} numberOfLines={2}>
                    {featuredEvent.title}
                  </Text>
                  <Text style={styles.featuredDesc} numberOfLines={2}>
                    {featuredEvent.description || "Açık havada yıldızların altında keyifli bir şehir akşamı."}
                  </Text>
                </View>
              </TouchableOpacity>
            )}

            <View style={styles.sectionHeader}>
              <Text style={styles.sectionTitle}>ŞEHİRDEN HABERLER</Text>
            </View>

            {news.slice(0, 3).map((item, index) => (
              <TouchableOpacity
                key={`${item.id}-${index}`}
                style={[styles.newsCard, index === 1 && styles.newsImageCard]}
                onPress={() => navigation.navigate("NewsDetail", { news: item })}
                activeOpacity={0.9}
              >
                {index === 1 && item.image_url ? (
                  <>
                    <Image source={{ uri: item.image_url }} style={styles.newsImage} resizeMode="cover" />
                    <LinearGradient colors={["transparent", "rgba(0,0,0,0.9)"]} style={styles.newsOverlay} />
                  </>
                ) : null}

                <View style={styles.newsContent}>
                  <Text style={styles.newsMeta}>
                    {(item.category || "Genel")} • {relativeTime(item.published_at)}
                  </Text>
                  <Text style={styles.newsTitle} numberOfLines={index === 2 ? 4 : 2}>
                    {item.title}
                  </Text>
                  {index === 2 && item.content ? (
                    <Text style={styles.newsDesc} numberOfLines={3}>
                      {item.content}
                    </Text>
                  ) : null}
                </View>
              </TouchableOpacity>
            ))}

            <View style={[styles.sectionHeader, styles.routesHeader]}>
              <Text style={styles.sectionTitle}>KEŞİF ROTALARI / MEKANLAR</Text>
              <TouchableOpacity>
                <Text style={styles.allText}>TÜMÜ →</Text>
              </TouchableOpacity>
            </View>

            <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={styles.placesRow}>
              {routePlaces.map((place, idx) => (
                <TouchableOpacity
                  key={`${place.id}-${idx}`}
                  style={styles.placeCard}
                  onPress={() => navigation.navigate("PlaceDetail", { ...place })}
                  activeOpacity={0.9}
                >
                  {place.image_url ? (
                    <Image source={{ uri: place.image_url }} style={styles.placeImage} resizeMode="cover" />
                  ) : (
                    <LinearGradient
                      colors={["rgba(22, 40, 58, 0.7)", "rgba(17,17,20,0.95)"]}
                      style={styles.placeImage}
                    />
                  )}
                  <LinearGradient colors={["transparent", "rgba(0,0,0,0.95)"]} style={styles.placeOverlay} />

                  <View style={styles.placeTag}>
                    <Text style={styles.placeTagText}>TARİHİ</Text>
                  </View>

                  <View style={styles.placeContent}>
                    <Text style={styles.placeCategory} numberOfLines={1}>
                      {place.category || "Keşif"}
                    </Text>
                    <Text style={styles.placeTitle} numberOfLines={2}>
                      {place.name}
                    </Text>
                  </View>
                </TouchableOpacity>
              ))}
            </ScrollView>
          </ScrollView>
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
  loadingWrap: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
  },
  scrollContent: {
    paddingHorizontal: spacing.xl,
    paddingBottom: 120,
  },
  titleWrap: {
    marginTop: spacing.lg,
    marginBottom: spacing.xl,
  },
  pageTitle: {
    fontSize: 42,
    lineHeight: 46,
    fontWeight: "400",
    color: colors.text,
    marginBottom: spacing.xs,
  },
  pageSubtitle: {
    ...typography.body,
    color: colors.textSecondary,
  },
  featuredCard: {
    height: 380,
    borderRadius: borderRadius.lg,
    overflow: "hidden",
    borderWidth: 1,
    borderColor: colors.borderLight,
    marginBottom: spacing.xxxl,
  },
  featuredImage: {
    ...StyleSheet.absoluteFillObject,
  },
  featuredOverlay: {
    ...StyleSheet.absoluteFillObject,
  },
  featuredChips: {
    position: "absolute",
    top: spacing.lg,
    left: spacing.lg,
    right: spacing.lg,
    flexDirection: "row",
    justifyContent: "space-between",
  },
  chip: {
    borderWidth: 1,
    borderColor: "rgba(255,255,255,0.45)",
    borderRadius: borderRadius.full,
    backgroundColor: "rgba(0,0,0,0.55)",
    paddingHorizontal: spacing.md,
    paddingVertical: 6,
  },
  chipText: {
    ...typography.captionSmall,
    color: colors.text,
    letterSpacing: 0.8,
  },
  featuredContent: {
    position: "absolute",
    left: spacing.lg,
    right: spacing.lg,
    bottom: spacing.lg,
  },
  featuredMeta: {
    ...typography.caption,
    color: colors.primary,
    marginBottom: spacing.xs,
  },
  featuredTitle: {
    fontSize: 18,
    lineHeight: 24,
    fontWeight: "500",
    color: colors.text,
    marginBottom: spacing.sm,
  },
  featuredDesc: {
    ...typography.body,
    color: colors.textSecondary,
  },
  sectionHeader: {
    marginBottom: spacing.md,
    borderBottomWidth: 1,
    borderBottomColor: colors.borderLight,
    paddingBottom: spacing.sm,
  },
  sectionTitle: {
    ...typography.caption,
    color: colors.primary,
    letterSpacing: 1.5,
  },
  newsCard: {
    backgroundColor: "rgba(20,20,24,0.96)",
    borderWidth: 1,
    borderColor: colors.borderLight,
    borderRadius: borderRadius.md,
    padding: spacing.lg,
    marginBottom: spacing.lg,
    minHeight: 120,
    overflow: "hidden",
  },
  newsImageCard: {
    minHeight: 170,
    padding: 0,
  },
  newsImage: {
    ...StyleSheet.absoluteFillObject,
  },
  newsOverlay: {
    ...StyleSheet.absoluteFillObject,
  },
  newsContent: {
    position: "relative",
    zIndex: 1,
  },
  newsMeta: {
    ...typography.captionSmall,
    color: colors.textSecondary,
    marginBottom: spacing.sm,
  },
  newsTitle: {
    fontSize: 16,
    lineHeight: 22,
    fontWeight: "400",
    color: colors.text,
  },
  newsDesc: {
    ...typography.body,
    color: colors.textSecondary,
    marginTop: spacing.sm,
  },
  routesHeader: {
    marginTop: spacing.xl,
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
  },
  allText: {
    ...typography.caption,
    color: colors.textSecondary,
    letterSpacing: 1,
  },
  placesRow: {
    paddingBottom: spacing.xl,
    gap: spacing.md,
  },
  placeCard: {
    width: 300,
    height: 430,
    borderRadius: borderRadius.lg,
    overflow: "hidden",
    borderWidth: 1,
    borderColor: colors.borderLight,
    marginRight: spacing.md,
  },
  placeImage: {
    ...StyleSheet.absoluteFillObject,
  },
  placeOverlay: {
    ...StyleSheet.absoluteFillObject,
  },
  placeTag: {
    position: "absolute",
    top: spacing.lg,
    right: spacing.lg,
    borderWidth: 1,
    borderColor: "rgba(255,255,255,0.4)",
    backgroundColor: "rgba(0,0,0,0.45)",
    borderRadius: borderRadius.full,
    paddingHorizontal: spacing.sm,
    paddingVertical: 4,
  },
  placeTagText: {
    ...typography.captionSmall,
    color: colors.text,
  },
  placeContent: {
    position: "absolute",
    left: spacing.lg,
    right: spacing.lg,
    bottom: spacing.lg,
  },
  placeCategory: {
    ...typography.caption,
    color: colors.textSecondary,
    marginBottom: spacing.xs,
  },
  placeTitle: {
    fontSize: 20,
    lineHeight: 26,
    fontWeight: "400",
    color: colors.text,
  },
});
