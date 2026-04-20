import React from 'react';
import { View, Text, StyleSheet, ScrollView, TouchableOpacity } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { LinearGradient } from 'expo-linear-gradient';
import { Ionicons } from '@expo/vector-icons';

import { colors, spacing, typography, shadows, borderRadius } from '../theme';

export function DashboardScreen() {
  return (
    <LinearGradient colors={colors.gradients.bg as any} style={styles.container}>
      <SafeAreaView style={styles.safeArea} edges={['top']}>
        <View style={styles.header}>
            <View>
                <Text style={styles.title}>Şehir Yaşamı</Text>
                <Text style={styles.subtitle}>Güncel Aliağa Bilgileri</Text>
            </View>
        </View>

        <ScrollView contentContainerStyle={styles.scrollContent} showsVerticalScrollIndicator={false}>
          
          {/* Hava Durumu Widget */}
          <LinearGradient colors={['rgba(28, 42, 65, 0.8)', 'rgba(15, 25, 40, 0.8)']} style={styles.weatherWidget}>
            <View style={styles.weatherTop}>
               <View>
                 <Text style={styles.weatherCity}>Aliağa, İzmir</Text>
                 <Text style={styles.weatherDate}>Bugün, {new Date().toLocaleDateString('tr-TR', { day: 'numeric', month: 'long'})}</Text>
               </View>
               <Ionicons name="partly-sunny" size={48} color={colors.secondary} />
            </View>
            <View style={styles.weatherBottom}>
               <Text style={styles.weatherTemp}>24°</Text>
               <View style={styles.weatherDetails}>
                 <Text style={styles.weatherCondition}>Parçalı Bulutlu</Text>
                 <Text style={styles.weatherInfo}>Nem: 45% • Rüzgar: 12km/s</Text>
               </View>
            </View>
          </LinearGradient>

          {/* Nöbetçi Eczaneler */}
          <View style={styles.sectionHeader}>
            <Ionicons name="medical" size={24} color={colors.primary} />
            <Text style={styles.sectionTitle}>Nöbetçi Eczaneler</Text>
          </View>

          {[
            { name: "Merkez Eczanesi", address: "Kültür Mah. İstiklal Cad. No:45", phone: "0232 616 12 34", distance: "1.2 km" },
            { name: "Sağlık Eczanesi", address: "Siteler Mah. İnönü Bulvarı No:12", phone: "0232 616 55 66", distance: "2.4 km" }
          ].map((pharmacy, i) => (
            <TouchableOpacity key={i} style={styles.card}>
              <View style={styles.cardHeader}>
                  <Text style={styles.cardTitle}>{pharmacy.name}</Text>
                  <View style={styles.badge}>
                    <Text style={styles.badgeText}>{pharmacy.distance}</Text>
                  </View>
              </View>
              <Text style={styles.cardAddress}>{pharmacy.address}</Text>
              <View style={styles.cardFooter}>
                <Ionicons name="call-outline" size={16} color={colors.secondary} />
                <Text style={styles.cardPhone}>{pharmacy.phone}</Text>
              </View>
            </TouchableOpacity>
          ))}

        </ScrollView>
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
  header: {
    paddingHorizontal: spacing.xl,
    paddingVertical: spacing.lg,
    alignItems: 'center',
    marginBottom: spacing.md,
  },
  title: {
    ...typography.h2,
    color: colors.text,
    textAlign: 'center',
  },
  subtitle: {
    ...typography.caption,
    color: colors.textSecondary,
    textAlign: 'center',
    marginTop: 4,
  },
  scrollContent: {
    paddingHorizontal: spacing.lg,
    paddingBottom: 120, // Tab bar space
  },
  weatherWidget: {
    borderRadius: borderRadius.xl,
    padding: spacing.xl,
    marginBottom: spacing.xxxl,
    borderWidth: 1,
    borderColor: colors.borderLight,
    ...shadows.medium,
  },
  weatherTop: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: spacing.xl,
  },
  weatherCity: {
    ...typography.h3,
    color: colors.text,
  },
  weatherDate: {
    ...typography.bodySmall,
    color: colors.textSecondary,
    marginTop: 2,
  },
  weatherBottom: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  weatherTemp: {
    fontFamily: "System",
    fontSize: 56,
    fontWeight: '800',
    letterSpacing: -2,
    color: colors.text,
    marginRight: spacing.lg,
  },
  weatherDetails: {
    flex: 1,
  },
  weatherCondition: {
    ...typography.bodyMedium,
    color: colors.secondary,
  },
  weatherInfo: {
    ...typography.caption,
    color: colors.textTertiary,
    marginTop: 4,
  },
  sectionHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: spacing.lg,
    paddingHorizontal: spacing.xs,
  },
  sectionTitle: {
    ...typography.h3,
    color: colors.text,
    marginLeft: spacing.sm,
  },
  card: {
    backgroundColor: colors.surface,
    borderRadius: borderRadius.lg,
    padding: spacing.lg,
    marginBottom: spacing.md,
    borderWidth: 1,
    borderColor: colors.borderLight,
  },
  cardHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: spacing.sm,
  },
  cardTitle: {
    ...typography.h3,
    color: colors.text,
    flex: 1,
  },
  badge: {
    backgroundColor: colors.primaryLight,
    paddingHorizontal: spacing.sm,
    paddingVertical: 4,
    borderRadius: borderRadius.sm,
  },
  badgeText: {
    ...typography.caption,
    color: colors.primary,
  },
  cardAddress: {
    ...typography.bodySmall,
    color: colors.textSecondary,
    marginBottom: spacing.md,
  },
  cardFooter: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  cardPhone: {
    ...typography.bodyMedium,
    color: colors.secondary,
    marginLeft: spacing.xs,
  }
});
