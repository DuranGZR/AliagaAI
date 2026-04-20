import React from 'react';
import { View, Text, StyleSheet, ScrollView, TouchableOpacity, Image } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { LinearGradient } from 'expo-linear-gradient';
import { Ionicons } from '@expo/vector-icons';
import { useNavigation, useRoute } from '@react-navigation/native';

import { colors, spacing, typography, shadows, borderRadius } from '../theme';

export function PlaceDetailScreen() {
  const navigation = useNavigation();
  const route = useRoute();
  
  // Dummy data if accessed directly without props
  const item: any = route.params || {
    name: "Aigai Antik Kenti",
    category: "Tarihi Yer",
    address: "Yuntdağı, Köseler Köyü, Manisa (Aliağa Sınırı)",
    description: "Aigai (Aiolis), Batı Anadolu'da kurulan 12 Aiol kentinden biridir. Yunt Dağı silsilesi üzerinde, Gün Dağı'nın eteklerinde kurulmuş antik bir kenttir. Kültürel mirası ile Ege'nin en önemli duraklarından biridir.",
    rating: 4.8,
    tags: ["Tarihi", "Açık Hava", "Müze/Ören Yeri"]
  };

  return (
    <LinearGradient colors={colors.gradients.bg as any} style={styles.container}>
      <SafeAreaView style={styles.safeArea}>
        
        {/* Header Image Area (Mock text pattern for now) */}
        <View style={styles.imagePlaceholder}>
           <LinearGradient colors={['rgba(28,42,65,0.2)', 'rgba(5,15,25,1)']} style={styles.imageOverlay} />
           <TouchableOpacity style={styles.backButton} onPress={() => navigation.goBack()}>
             <Ionicons name="arrow-back" size={24} color={colors.text} />
           </TouchableOpacity>
        </View>

        <ScrollView contentContainerStyle={styles.content}>
          <View style={styles.titleRow}>
            <View style={styles.titleInfo}>
               <Text style={styles.title}>{item.name}</Text>
               <Text style={styles.category}>{item.category}</Text>
            </View>
            {item.rating && (
                <View style={styles.ratingBadge}>
                  <Ionicons name="star" size={16} color={colors.background} />
                  <Text style={styles.ratingText}>{item.rating}</Text>
                </View>
            )}
          </View>

          <View style={styles.tagsContainer}>
            {item.tags?.map((tag: string, i: number) => (
              <View key={i} style={styles.tag}>
                <Text style={styles.tagText}>{tag}</Text>
              </View>
            ))}
          </View>

          <View style={styles.infoRow}>
            <Ionicons name="location" size={20} color={colors.tertiary} />
            <Text style={styles.infoText}>{item.address}</Text>
          </View>

          {item.phone && (
            <View style={styles.infoRow}>
              <Ionicons name="call" size={20} color={colors.secondary} />
              <Text style={styles.infoText}>{item.phone}</Text>
            </View>
          )}

          <View style={styles.divider} />

          <Text style={styles.sectionTitle}>Hakkında</Text>
          <Text style={styles.description}>{item.description || "Bu mekan hakkında detaylı bilgi bulunmuyor."}</Text>

        </ScrollView>

        {/* Action Bottom Bar */}
        <View style={styles.bottomBar}>
          <TouchableOpacity style={styles.actionButton}>
            <Ionicons name="map-outline" size={20} color={colors.background} />
            <Text style={styles.actionButtonText}>Yol Tarifi Al</Text>
          </TouchableOpacity>
        </View>
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
    height: 300,
    backgroundColor: colors.surfaceContainer,
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
  titleRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: spacing.md,
  },
  titleInfo: {
    flex: 1,
    paddingRight: spacing.md,
  },
  title: {
    ...typography.h1,
    color: colors.text,
    fontSize: 28,
  },
  category: {
    ...typography.bodyMedium,
    color: colors.secondary,
    marginTop: 4,
  },
  ratingBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: colors.secondary,
    paddingHorizontal: spacing.sm,
    paddingVertical: 6,
    borderRadius: borderRadius.md,
  },
  ratingText: {
    ...typography.bodySmall,
    fontWeight: '700',
    color: colors.background,
    marginLeft: 4,
  },
  tagsContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: spacing.sm,
    marginBottom: spacing.xl,
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
    ...typography.caption,
    color: colors.textSecondary,
  },
  infoRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: spacing.md,
  },
  infoText: {
    ...typography.body,
    color: colors.text,
    marginLeft: spacing.md,
    flex: 1,
  },
  divider: {
    height: 1,
    backgroundColor: colors.borderLight,
    marginVertical: spacing.xl,
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
