import React from 'react';
import { View, Text, StyleSheet, ScrollView, TouchableOpacity, Image, Linking } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { LinearGradient } from 'expo-linear-gradient';
import { Ionicons } from '@expo/vector-icons';
import { useNavigation, useRoute } from '@react-navigation/native';

import { colors, spacing, typography, shadows, borderRadius } from '../theme';
import { NewsItem } from '../types';

export function NewsDetailScreen() {
  const navigation = useNavigation();
  const route = useRoute();
  
  const item = route.params as { news: NewsItem } | undefined;
  const news = item?.news;

  if (!news) {
    return (
      <View style={[styles.container, { justifyContent: "center", alignItems: "center" }]}>
        <Text style={{ color: colors.text }}>Haber bulunamadı.</Text>
        <TouchableOpacity style={{ marginTop: 20 }} onPress={() => navigation.goBack()}>
          <Text style={{ color: colors.primary }}>Geri Dön</Text>
        </TouchableOpacity>
      </View>
    );
  }

  // Tarih formatla
  const formattedDate = news.published_at 
    ? new Date(news.published_at).toLocaleDateString('tr-TR', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
      })
    : "";

  return (
    <LinearGradient colors={colors.gradients.bg as any} style={styles.container}>
      <SafeAreaView style={styles.safeArea}>
        
        {/* Header Image Area */}
        <View style={styles.imagePlaceholder}>
          {news.image_url ? (
            <Image
              source={{ uri: news.image_url }}
              style={StyleSheet.absoluteFillObject}
              resizeMode="cover"
            />
          ) : (
            <View style={styles.imageFallback}>
              <Ionicons name="newspaper-outline" size={64} color={colors.textTertiary} />
            </View>
          )}
          <LinearGradient colors={['rgba(10,15,20,0.3)', 'rgba(5,15,25,1)']} style={styles.imageOverlay} />
          
          <TouchableOpacity style={styles.backButton} onPress={() => navigation.goBack()}>
            <Ionicons name="arrow-back" size={24} color={colors.text} />
          </TouchableOpacity>
        </View>

        <ScrollView contentContainerStyle={styles.content}>
          <View style={styles.metaRow}>
            <View style={styles.categoryBadge}>
              <Text style={styles.categoryText}>{news.category?.toUpperCase() || "HABER"}</Text>
            </View>
            <Text style={styles.dateText}>{formattedDate}</Text>
          </View>

          <Text style={styles.title}>{news.title}</Text>
          
          <View style={styles.divider} />

          <Text style={styles.description}>
            {news.content || "Haber içeriği bulunmuyor."}
          </Text>
        </ScrollView>

        {/* Action Bottom Bar */}
        {news.source_url && (
          <View style={styles.bottomBar}>
            <TouchableOpacity 
              style={styles.actionButton}
              onPress={() => Linking.openURL(news.source_url!)}
            >
              <Ionicons name="link-outline" size={20} color={colors.background} />
              <Text style={styles.actionButtonText}>Orijinal Kaynağa Git</Text>
            </TouchableOpacity>
          </View>
        )}
      </SafeAreaView>
    </LinearGradient>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  safeArea: {
    flex: 1,
  },
  imagePlaceholder: {
    height: 280,
    backgroundColor: colors.surface,
  },
  imageFallback: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  imageOverlay: {
    ...StyleSheet.absoluteFillObject,
  },
  backButton: {
    position: 'absolute',
    top: spacing.md,
    left: spacing.lg,
    width: 44,
    height: 44,
    borderRadius: 22,
    backgroundColor: colors.glassDark,
    justifyContent: 'center',
    alignItems: 'center',
    borderWidth: 1,
    borderColor: colors.borderLight,
  },
  content: {
    padding: spacing.xl,
    paddingTop: spacing.lg,
    paddingBottom: 100,
  },
  metaRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: spacing.md,
  },
  categoryBadge: {
    backgroundColor: colors.primary,
    paddingHorizontal: spacing.sm,
    paddingVertical: 4,
    borderRadius: borderRadius.sm,
  },
  categoryText: {
    ...typography.captionSmall,
    color: colors.background,
    fontWeight: '700',
  },
  dateText: {
    ...typography.caption,
    color: colors.textSecondary,
  },
  title: {
    ...typography.h2,
    color: colors.text,
    lineHeight: 32,
  },
  divider: {
    height: 1,
    backgroundColor: colors.borderLight,
    marginVertical: spacing.lg,
  },
  description: {
    ...typography.body,
    color: colors.textSecondary,
    lineHeight: 26,
  },
  bottomBar: {
    position: 'absolute',
    bottom: 0,
    left: 0,
    right: 0,
    padding: spacing.xl,
    paddingBottom: spacing.xxl,
    backgroundColor: colors.background,
    borderTopWidth: 1,
    borderTopColor: colors.borderLight,
  },
  actionButton: {
    backgroundColor: colors.primary,
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    height: 56,
    borderRadius: borderRadius.full,
    ...shadows.glow,
  },
  actionButtonText: {
    ...typography.button,
    color: colors.background,
    marginLeft: spacing.sm,
  }
});
