import React, { useEffect, useState } from "react";
import {
  View,
  StyleSheet,
  Text,
  TouchableOpacity,
  FlatList,
  ActivityIndicator,
  Linking,
} from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { Ionicons } from "@expo/vector-icons";
import { useNavigation } from "@react-navigation/native";
import { LinearGradient } from "expo-linear-gradient";

import { colors, spacing, typography, borderRadius } from "../theme";
import { pharmacyService } from "../services/api";
import { Pharmacy } from "../types";

export function PharmacyListScreen() {
  const navigation = useNavigation<any>();
  const [pharmacies, setPharmacies] = useState<Pharmacy[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchPharmacies = async () => {
      try {
        const data = await pharmacyService.getToday();
        setPharmacies(data || []);
      } catch (error) {
        console.error("Eczaneler çekilirken hata:", error);
      } finally {
        setLoading(false);
      }
    };
    fetchPharmacies();
  }, []);

  const openDirections = (pharmacyName: string) => {
    Linking.openURL(
      `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(
        pharmacyName + " Eczanesi Aliağa"
      )}`
    );
  };

  const renderItem = ({ item }: { item: Pharmacy }) => (
    <LinearGradient colors={colors.gradients.surface} style={styles.pharmacyCard}>
      <View style={styles.pharmacyInfo}>
        <View style={styles.pharmacyHeaderRow}>
          <Ionicons name="medical" size={16} color={colors.primary} />
          <Text style={styles.pharmacyName}>{item.name}</Text>
        </View>
        <View style={styles.pharmacyDetailRow}>
          <Ionicons name="location" size={14} color={colors.textTertiary} />
          <Text style={styles.pharmacyAddress}>
            {item.address || "Adres bilgisi bulunmuyor"}
          </Text>
        </View>
        {item.phone && (
          <View style={styles.pharmacyDetailRow}>
            <Ionicons name="call" size={14} color={colors.textTertiary} />
            <Text style={styles.pharmacyPhone}>{item.phone}</Text>
          </View>
        )}
      </View>
      <TouchableOpacity
        style={styles.directionsButton}
        onPress={() => openDirections(item.name)}
      >
        <Ionicons name="navigate" size={16} color={colors.background} />
        <Text style={styles.directionsText}>Yol Tarifi</Text>
      </TouchableOpacity>
    </LinearGradient>
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
          <Text style={styles.headerTitle}>Nöbetçi Eczaneler</Text>
          <View style={{ width: 24 }} />
        </View>

        {loading ? (
          <View style={styles.center}>
            <ActivityIndicator size="large" color={colors.primary} />
          </View>
        ) : pharmacies.length === 0 ? (
          <View style={styles.center}>
            <Text style={styles.emptyText}>Bugün için nöbetçi eczane bulunamadı.</Text>
          </View>
        ) : (
          <FlatList
            data={pharmacies}
            keyExtractor={(item, index) => (item.id ? item.id.toString() : index.toString())}
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
  pharmacyCard: {
    padding: spacing.lg,
    borderRadius: borderRadius.lg,
    marginBottom: spacing.md,
    borderWidth: 1,
    borderColor: "rgba(255, 255, 255, 0.05)",
  },
  pharmacyInfo: {
    marginBottom: spacing.md,
  },
  pharmacyHeaderRow: {
    flexDirection: "row",
    alignItems: "center",
    gap: spacing.sm,
    marginBottom: spacing.sm,
  },
  pharmacyName: {
    ...typography.h3,
    color: colors.text,
  },
  pharmacyDetailRow: {
    flexDirection: "row",
    alignItems: "center",
    gap: spacing.xs,
    marginBottom: spacing.xs,
  },
  pharmacyAddress: {
    ...typography.bodySmall,
    color: colors.textSecondary,
    flex: 1,
  },
  pharmacyPhone: {
    ...typography.bodySmall,
    color: colors.textSecondary,
  },
  directionsButton: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "center",
    gap: spacing.xs,
    backgroundColor: colors.primary,
    paddingVertical: spacing.md,
    borderRadius: borderRadius.md,
  },
  directionsText: {
    ...typography.button,
    color: colors.background,
    fontSize: 14,
  },
});
