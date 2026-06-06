import React, { useEffect, useState } from 'react';
import { View, Text, StyleSheet, FlatList, TouchableOpacity, ActivityIndicator, Dimensions } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { LinearGradient } from 'expo-linear-gradient';
import { Ionicons } from '@expo/vector-icons';
import { useNavigation, useRoute } from '@react-navigation/native';

import { colors, spacing, typography, borderRadius, shadows } from '../theme';
import { GalleryItem } from '../types';
import { galleryService } from '../services/api';
import { ReliableImage } from '../components/ReliableImage';
import { openExternalUrl } from '../utils/externalActions';

const { width } = Dimensions.get('window');
const COLUMN_COUNT = 2;
const IMAGE_SIZE = (width - spacing.lg * 2 - spacing.sm * (COLUMN_COUNT - 1)) / COLUMN_COUNT;

export function GalleryDetailScreen() {
  const navigation = useNavigation<any>();
  const route = useRoute<any>();
  const galleryId = route.params?.galleryId;

  const [gallery, setGallery] = useState<GalleryItem | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (galleryId) {
      fetchGallery();
    }
  }, [galleryId]);

  const fetchGallery = async () => {
    try {
      const data = await galleryService.getById(galleryId);
      setGallery(data);
    } catch (error) {
      console.error("Gallery fetch error:", error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <LinearGradient colors={colors.gradients.bg as any} style={styles.centerContainer}>
        <ActivityIndicator size="large" color={colors.primary} />
      </LinearGradient>
    );
  }

  if (!gallery) {
    return (
      <LinearGradient colors={colors.gradients.bg as any} style={styles.centerContainer}>
        <Text style={styles.emptyText}>Galeri bulunamadı.</Text>
        <TouchableOpacity style={{ marginTop: 20 }} onPress={() => navigation.goBack()}>
          <Text style={{ color: colors.primary }}>Geri Dön</Text>
        </TouchableOpacity>
      </LinearGradient>
    );
  }

  const renderImage = ({ item }: { item: any }) => {
    return (
      <TouchableOpacity 
        style={styles.imageContainer}
        onPress={() => {
          // Geliştirme: Fancybox veya tam ekran modal eklenebilir
          // Şimdilik sadece resme tıklanabiliyor
        }}
        activeOpacity={0.9}
      >
        <ReliableImage 
          uri={item.image_url} 
          fallbackUri="https://images.unsplash.com/photo-1504711434969-e33886168f5c?auto=format&fit=crop&w=600&q=80"
          style={styles.image}
          resizeMode="cover"
        />
        {item.description ? (
          <LinearGradient colors={['transparent', 'rgba(0,0,0,0.7)']} style={styles.imageOverlay}>
            <Text style={styles.imageDesc} numberOfLines={2}>{item.description}</Text>
          </LinearGradient>
        ) : null}
      </TouchableOpacity>
    );
  };

  return (
    <LinearGradient colors={colors.gradients.bg as any} style={styles.container}>
      <SafeAreaView style={styles.safeArea}>
        <View style={styles.header}>
          <TouchableOpacity onPress={() => navigation.goBack()} style={styles.backButton}>
            <Ionicons name="arrow-back" size={24} color={colors.text} />
          </TouchableOpacity>
          <Text style={styles.headerTitle} numberOfLines={1}>{gallery.title}</Text>
          {gallery.source_url ? (
            <TouchableOpacity onPress={() => void openExternalUrl(gallery.source_url!)} style={styles.backButton}>
              <Ionicons name="globe-outline" size={24} color={colors.text} />
            </TouchableOpacity>
          ) : (
            <View style={{ width: 44 }} />
          )}
        </View>

        <FlatList
          data={gallery.images || []}
          keyExtractor={(item) => item.id.toString()}
          renderItem={renderImage}
          contentContainerStyle={styles.listContent}
          numColumns={COLUMN_COUNT}
          columnWrapperStyle={styles.row}
          ListHeaderComponent={
            <View style={styles.listHeader}>
              <Text style={styles.title}>{gallery.title}</Text>
              <Text style={styles.countText}>{gallery.images?.length || 0} Fotoğraf</Text>
            </View>
          }
          ListEmptyComponent={
            <View style={[styles.centerContainer, { height: 200 }]}>
              <Text style={styles.emptyText}>Bu galeride henüz fotoğraf yok.</Text>
            </View>
          }
        />
      </SafeAreaView>
    </LinearGradient>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1 },
  safeArea: { flex: 1 },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.md,
  },
  backButton: {
    width: 44,
    height: 44,
    borderRadius: 22,
    backgroundColor: colors.surface,
    justifyContent: 'center',
    alignItems: 'center',
    borderWidth: 1,
    borderColor: colors.borderLight,
  },
  headerTitle: {
    ...typography.h3,
    color: colors.text,
    flex: 1,
    textAlign: 'center',
    paddingHorizontal: spacing.sm,
  },
  centerContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  emptyText: {
    ...typography.body,
    color: colors.textSecondary,
  },
  listContent: {
    padding: spacing.lg,
    paddingBottom: 100,
  },
  listHeader: {
    marginBottom: spacing.lg,
    alignItems: 'center',
  },
  title: {
    ...typography.h2,
    color: colors.text,
    textAlign: 'center',
    marginBottom: spacing.xs,
  },
  countText: {
    ...typography.subtitle,
    color: colors.primary,
  },
  row: {
    justifyContent: 'space-between',
    marginBottom: spacing.sm,
  },
  imageContainer: {
    width: IMAGE_SIZE,
    height: IMAGE_SIZE,
    borderRadius: borderRadius.md,
    overflow: 'hidden',
    backgroundColor: colors.surface,
  },
  image: {
    width: '100%',
    height: '100%',
  },
  imageOverlay: {
    position: 'absolute',
    bottom: 0,
    left: 0,
    right: 0,
    padding: spacing.sm,
    paddingTop: spacing.lg,
  },
  imageDesc: {
    ...typography.captionSmall,
    color: colors.background,
  }
});
