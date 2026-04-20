import React from "react";
import {
  View,
  StyleSheet,
  Text,
  TouchableOpacity,
  ScrollView,
} from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { LinearGradient } from "expo-linear-gradient";
import { Ionicons } from "@expo/vector-icons";
import { useNavigation } from "@react-navigation/native";
import { BottomTabNavigationProp } from "@react-navigation/bottom-tabs";

import { colors, spacing, typography, shadows, borderRadius } from "../theme";

type RootTabParamList = {
  Home: undefined;
  Chat: undefined;
  Dashboard: undefined;
};

type NavigationProp = BottomTabNavigationProp<RootTabParamList, 'Home'>;

export function HomeScreen() {
  const navigation = useNavigation<NavigationProp>();

  return (
    <LinearGradient
      colors={colors.gradients.bg as any}
      style={styles.container}
    >
      <SafeAreaView style={styles.safeArea} edges={["top"]}>
        <View style={styles.header}>
            <View>
                <Text style={styles.title}>AliağaAI</Text>
                <Text style={styles.subtitle}>İlham Veren Şehir Rehberin</Text>
            </View>
            <TouchableOpacity style={styles.headerAction}>
                <Ionicons name="sparkles" size={24} color={colors.primary} />
            </TouchableOpacity>
        </View>

        <ScrollView contentContainerStyle={styles.scrollContent} showsVerticalScrollIndicator={false}>
          <View style={styles.heroSection}>
            <LinearGradient
              colors={colors.gradients.accent as any}
              style={styles.heroIconContainer}
            >
              <Ionicons name="planet" size={48} color={colors.background} />
            </LinearGradient>
            
            <Text style={styles.heroTitle}>Aigai'den Günümüze</Text>
            <Text style={styles.heroSubtitle}>
              Kültürel mirası ve modern yaşamı keşfet. Ben senin kişisel Aliağa asistanınım.
            </Text>
          </View>
          
          <View style={styles.suggestionsGrid}>
            {[
              { icon: "medical", title: "Nöbetçi Eczaneler", nav: "Dashboard" },
              { icon: "partly-sunny", title: "Hava Durumu", nav: "Dashboard" },
              { icon: "restaurant", title: "Lezzet Durakları", nav: "Chat" },
              { icon: "camera", title: "Antik Kentler", nav: "Chat" },
            ].map((item) => (
              <TouchableOpacity
                key={item.title}
                style={styles.suggestionBox}
                onPress={() => item.nav === "Chat" ? navigation.navigate("Chat") : navigation.navigate("Dashboard")}
              >
                <View style={styles.suggestionIconWrapper}>
                  <Ionicons name={item.icon as any} size={28} color={colors.primary} />
                </View>
                <Text style={styles.suggestionText}>{item.title}</Text>
              </TouchableOpacity>
            ))}
          </View>

          <TouchableOpacity style={styles.searchBarFake} onPress={() => navigation.navigate("Chat")}>
            <Ionicons name="search" size={20} color={colors.textSecondary} />
            <Text style={styles.searchBarFakeText}>Aliağa hakkında bir şeyler sor...</Text>
            <View style={styles.searchBarMic}>
              <Ionicons name="mic" size={18} color={colors.background} />
            </View>
          </TouchableOpacity>
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
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
  },
  title: {
    ...typography.h1,
    color: colors.text,
  },
  subtitle: {
    ...typography.bodySmall,
    color: colors.textSecondary,
    marginTop: -4,
  },
  headerAction: {
    width: 44,
    height: 44,
    borderRadius: 22,
    backgroundColor: colors.surfaceHighlight,
    justifyContent: "center",
    alignItems: "center",
    borderWidth: 1,
    borderColor: colors.borderLight,
    ...shadows.glow,
  },
  scrollContent: {
    paddingBottom: 120, // Leave space for Pill Tab Bar
  },
  heroSection: {
    justifyContent: "center",
    alignItems: "center",
    paddingHorizontal: spacing.huge,
    marginTop: spacing.xl,
  },
  heroIconContainer: {
    width: 96,
    height: 96,
    borderRadius: 32,
    justifyContent: "center",
    alignItems: "center",
    marginBottom: spacing.xxl,
    ...shadows.glow,
  },
  heroTitle: {
    ...typography.h2,
    color: colors.text,
    textAlign: "center",
    marginBottom: spacing.sm,
  },
  heroSubtitle: {
    ...typography.body,
    color: colors.textSecondary,
    textAlign: "center",
    lineHeight: 24,
    marginBottom: spacing.xxxl,
  },
  suggestionsGrid: {
    flexDirection: "row",
    flexWrap: "wrap",
    paddingHorizontal: spacing.lg,
    justifyContent: "space-between",
    gap: spacing.md,
    marginBottom: spacing.xxxl,
  },
  suggestionBox: {
    width: "47%",
    padding: spacing.md,
    borderRadius: borderRadius.lg,
    backgroundColor: colors.surface,
    borderWidth: 1,
    borderColor: colors.borderLight,
    alignItems: "center",
    ...shadows.soft,
  },
  suggestionIconWrapper: {
    width: 48,
    height: 48,
    borderRadius: 24,
    backgroundColor: colors.primaryLight,
    justifyContent: "center",
    alignItems: "center",
    marginBottom: spacing.sm,
  },
  suggestionText: {
    ...typography.bodyMedium,
    color: colors.text,
    textAlign: "center",
  },
  searchBarFake: {
    flexDirection: "row",
    alignItems: "center",
    backgroundColor: colors.glassDark,
    marginHorizontal: spacing.xl,
    paddingHorizontal: spacing.lg,
    height: 56,
    borderRadius: borderRadius.full,
    borderWidth: 1,
    borderColor: colors.borderLight,
  },
  searchBarFakeText: {
    flex: 1,
    marginLeft: spacing.sm,
    ...typography.body,
    color: colors.textSecondary,
  },
  searchBarMic: {
    width: 32,
    height: 32,
    borderRadius: 16,
    backgroundColor: colors.primary,
    justifyContent: "center",
    alignItems: "center",
  }
});
