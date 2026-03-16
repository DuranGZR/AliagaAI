import React, { useEffect, useState, useCallback } from "react";
import {
  View,
  Text,
  SectionList,
  StyleSheet,
  ActivityIndicator,
  RefreshControl,
} from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { Ionicons } from "@expo/vector-icons";
import { newsService, eventService } from "../services/api";
import { NewsItem, EventItem } from "../types";
import { colors, spacing, typography, borderRadius, shadows } from "../theme";

type SectionItem = EventItem | NewsItem;

type Section = {
  title: string;
  icon: string;
  data: SectionItem[];
  type: "events" | "news";
};

export function NewsScreen() {
  const [events, setEvents] = useState<EventItem[]>([]);
  const [news, setNews] = useState<NewsItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const fetchData = useCallback(async () => {
    try {
      const [eventsData, newsData] = await Promise.all([
        eventService.getUpcoming(),
        newsService.getAll(),
      ]);
      setEvents(eventsData);
      setNews(newsData);
    } catch {
      // silent
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const onRefresh = useCallback(() => {
    setRefreshing(true);
    fetchData();
  }, [fetchData]);

  if (loading) {
    return (
      <View style={styles.centered}>
        <ActivityIndicator size="large" color={colors.primary} />
      </View>
    );
  }

  const sections: Section[] = [
    { title: "Yaklaşan Etkinlikler", icon: "calendar", data: events, type: "events" },
    { title: "Son Haberler", icon: "newspaper", data: news, type: "news" },
  ];

  return (
    <SafeAreaView style={styles.container} edges={["top"]}>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Gündem</Text>
      </View>

      <SectionList<SectionItem, Section>
        sections={sections}
        keyExtractor={(item) => item.id.toString()}
        renderSectionHeader={({ section }) => (
          <View style={styles.sectionHeader}>
            <Ionicons
              name={section.icon as keyof typeof Ionicons.glyphMap}
              size={18}
              color={colors.primary}
            />
            <Text style={styles.sectionTitle}>{section.title}</Text>
          </View>
        )}
        renderItem={({ item, section }) => {
          if (section.type === "events") {
            const event = item as EventItem;
            return (
              <View style={styles.eventCard}>
                <View style={styles.dateBadge}>
                  <Text style={styles.dateDay}>
                    {event.event_date
                      ? new Date(event.event_date).getDate().toString()
                      : "—"}
                  </Text>
                  <Text style={styles.dateMonth}>
                    {event.event_date
                      ? new Date(event.event_date).toLocaleDateString("tr-TR", {
                          month: "short",
                        })
                      : ""}
                  </Text>
                </View>
                <View style={styles.eventInfo}>
                  <Text style={styles.eventTitle} numberOfLines={2}>
                    {event.title}
                  </Text>
                  {event.location && (
                    <Text style={styles.eventMeta}>
                      📍 {event.location}
                      {event.event_time ? ` • ${event.event_time}` : ""}
                    </Text>
                  )}
                  {event.is_free && (
                    <View style={styles.freeBadge}>
                      <Text style={styles.freeText}>Ücretsiz</Text>
                    </View>
                  )}
                </View>
              </View>
            );
          }

          const newsItem = item as NewsItem;
          return (
            <View style={styles.newsCard}>
              <Text style={styles.newsTitle} numberOfLines={2}>
                {newsItem.title}
              </Text>
              {newsItem.summary && (
                <Text style={styles.newsSummary} numberOfLines={3}>
                  {newsItem.summary}
                </Text>
              )}
              <Text style={styles.newsMeta}>
                {newsItem.published_date
                  ? new Date(newsItem.published_date).toLocaleDateString("tr-TR")
                  : ""}
              </Text>
            </View>
          );
        }}
        contentContainerStyle={styles.list}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
        stickySectionHeadersEnabled={false}
      />
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
  },
  centered: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
    backgroundColor: colors.background,
  },
  header: {
    paddingHorizontal: spacing.xl,
    paddingTop: spacing.md,
    paddingBottom: spacing.sm,
  },
  headerTitle: {
    ...typography.h1,
    color: colors.text,
  },
  list: {
    paddingHorizontal: spacing.lg,
    paddingBottom: spacing.xxxl,
  },
  sectionHeader: {
    flexDirection: "row",
    alignItems: "center",
    gap: spacing.sm,
    paddingVertical: spacing.md,
    marginTop: spacing.md,
  },
  sectionTitle: {
    ...typography.h3,
    color: colors.text,
  },
  eventCard: {
    flexDirection: "row",
    backgroundColor: colors.surface,
    borderRadius: borderRadius.md,
    padding: spacing.md,
    marginBottom: spacing.sm,
    gap: spacing.md,
    ...shadows.sm,
  },
  dateBadge: {
    backgroundColor: colors.primaryLight,
    borderRadius: borderRadius.sm,
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
    alignItems: "center",
    justifyContent: "center",
    minWidth: 52,
  },
  dateDay: {
    ...typography.h2,
    color: colors.primary,
  },
  dateMonth: {
    ...typography.caption,
    color: colors.primary,
    textTransform: "uppercase",
  },
  eventInfo: {
    flex: 1,
    justifyContent: "center",
  },
  eventTitle: {
    ...typography.body,
    fontWeight: "600",
    color: colors.text,
  },
  eventMeta: {
    ...typography.caption,
    color: colors.textSecondary,
    marginTop: 2,
  },
  freeBadge: {
    alignSelf: "flex-start",
    backgroundColor: "#D1FAE5",
    paddingHorizontal: spacing.sm,
    paddingVertical: 1,
    borderRadius: borderRadius.sm,
    marginTop: spacing.xs,
  },
  freeText: {
    ...typography.caption,
    color: colors.success,
    fontWeight: "600",
  },
  newsCard: {
    backgroundColor: colors.surface,
    borderRadius: borderRadius.md,
    padding: spacing.lg,
    marginBottom: spacing.sm,
    ...shadows.sm,
  },
  newsTitle: {
    ...typography.body,
    fontWeight: "600",
    color: colors.text,
    marginBottom: spacing.xs,
  },
  newsSummary: {
    ...typography.bodySmall,
    color: colors.textSecondary,
    marginBottom: spacing.sm,
  },
  newsMeta: {
    ...typography.caption,
    color: colors.textTertiary,
  },
});
