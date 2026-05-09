import React from "react";
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ScrollView,
  Alert,
} from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { Ionicons } from "@expo/vector-icons";
import { useNavigation } from "@react-navigation/native";
import { LinearGradient } from "expo-linear-gradient";
import { colors, spacing, typography, borderRadius } from "../theme";

export function SettingsProfileScreen() {
  const navigation = useNavigation<any>();

  return (
    <View style={styles.container}>
      <SafeAreaView style={styles.safeArea} edges={["top", "bottom"]}>
        {/* Header */}
        <View style={styles.header}>
          <TouchableOpacity
            style={styles.backButton}
            onPress={() => navigation.goBack()}
          >
            <Ionicons name="close" size={28} color={colors.text} />
          </TouchableOpacity>
          <Text style={styles.headerTitle}>Ayarlar & Profil</Text>
          <View style={{ width: 28 }} /> {/* Placeholder for balance */}
        </View>

        <ScrollView contentContainerStyle={styles.scrollContent} showsVerticalScrollIndicator={false}>
          {/* Profile Section */}
          <LinearGradient colors={colors.gradients.surface} style={styles.profileCard}>
            <View style={styles.profileAvatar}>
              <Ionicons name="person" size={32} color={colors.primary} />
            </View>
            <View style={styles.profileInfo}>
              <Text style={styles.profileName}>Aliağa Sakini</Text>
              <Text style={styles.profileEmail}>kullanici@aliaga.com</Text>
            </View>
            <TouchableOpacity
              style={styles.editButton}
              onPress={() => navigation.navigate("EditProfile")}
            >
              <Ionicons name="pencil" size={16} color={colors.textSecondary} />
            </TouchableOpacity>
          </LinearGradient>

          {/* Settings Options */}
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Tercihler</Text>

            <TouchableOpacity
              style={styles.optionRow}
              onPress={() => Alert.alert("Yakında", "Bildirim ayarları yakında eklenecektir.")}
            >
              <View style={styles.optionIconContainer}>
                <Ionicons name="notifications" size={20} color={colors.text} />
              </View>
              <Text style={styles.optionText}>Bildirimler</Text>
              <Ionicons name="chevron-forward" size={20} color={colors.textSecondary} />
            </TouchableOpacity>

            <TouchableOpacity
              style={styles.optionRow}
              onPress={() => Alert.alert("Yakında", "Aydınlık/Karanlık tema seçeneği çok yakında!")}
            >
              <View style={styles.optionIconContainer}>
                <Ionicons name="moon" size={20} color={colors.text} />
              </View>
              <Text style={styles.optionText}>Tema</Text>
              <Text style={styles.optionValue}>Karanlık</Text>
              <Ionicons name="chevron-forward" size={20} color={colors.textSecondary} />
            </TouchableOpacity>
          </View>

          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Uygulama</Text>

            <TouchableOpacity
              style={styles.optionRow}
              onPress={() => Alert.alert("Hakkında", "AliağaAI v1.0.0\nAliağa Belediyesi için geliştirilmiş akıllı asistan.")}
            >
              <View style={styles.optionIconContainer}>
                <Ionicons name="information-circle" size={20} color={colors.text} />
              </View>
              <Text style={styles.optionText}>Hakkında</Text>
              <Ionicons name="chevron-forward" size={20} color={colors.textSecondary} />
            </TouchableOpacity>

            <TouchableOpacity
              style={styles.optionRow}
              onPress={() => Alert.alert("İletişim", "Destek için destek@aliaga.com adresine e-posta gönderebilirsiniz.")}
            >
              <View style={styles.optionIconContainer}>
                <Ionicons name="mail" size={20} color={colors.text} />
              </View>
              <Text style={styles.optionText}>İletişim & Destek</Text>
              <Ionicons name="chevron-forward" size={20} color={colors.textSecondary} />
            </TouchableOpacity>
          </View>

          <TouchableOpacity
            style={styles.logoutButton}
            onPress={() => Alert.alert("Çıkış", "Çıkış yapmak istediğinize emin misiniz?", [{ text: "İptal", style: "cancel" }, { text: "Çıkış Yap", style: "destructive" }])}
          >
            <Ionicons name="log-out-outline" size={20} color={colors.error} />
            <Text style={styles.logoutText}>Çıkış Yap</Text>
          </TouchableOpacity>

          <Text style={styles.versionText}>AliağaAI v1.0.0</Text>
        </ScrollView>
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
    padding: spacing.xs,
  },
  headerTitle: {
    ...typography.h3,
    color: colors.text,
  },
  scrollContent: {
    padding: spacing.xl,
  },
  profileCard: {
    flexDirection: "row",
    alignItems: "center",
    padding: spacing.lg,
    borderRadius: borderRadius.xl,
    borderWidth: 1,
    borderColor: "rgba(255, 255, 255, 0.05)",
    marginBottom: spacing.xxxl,
  },
  profileAvatar: {
    width: 60,
    height: 60,
    borderRadius: 30,
    backgroundColor: "rgba(200, 169, 110, 0.15)",
    justifyContent: "center",
    alignItems: "center",
    marginRight: spacing.lg,
  },
  profileInfo: {
    flex: 1,
  },
  profileName: {
    ...typography.h3,
    color: colors.text,
    marginBottom: 4,
  },
  profileEmail: {
    ...typography.bodySmall,
    color: colors.textSecondary,
  },
  editButton: {
    padding: spacing.sm,
    backgroundColor: colors.surfaceLight,
    borderRadius: borderRadius.full,
  },
  section: {
    marginBottom: spacing.xxl,
  },
  sectionTitle: {
    ...typography.caption,
    color: colors.textSecondary,
    marginBottom: spacing.md,
    paddingLeft: spacing.xs,
  },
  optionRow: {
    flexDirection: "row",
    alignItems: "center",
    backgroundColor: colors.surface,
    padding: spacing.lg,
    borderRadius: borderRadius.lg,
    marginBottom: spacing.sm,
    borderWidth: 1,
    borderColor: "rgba(255, 255, 255, 0.05)",
  },
  optionIconContainer: {
    width: 32,
    height: 32,
    borderRadius: 8,
    backgroundColor: colors.surfaceLight,
    justifyContent: "center",
    alignItems: "center",
    marginRight: spacing.md,
  },
  optionText: {
    ...typography.bodyMedium,
    color: colors.text,
    flex: 1,
  },
  optionValue: {
    ...typography.bodySmall,
    color: colors.textSecondary,
    marginRight: spacing.sm,
  },
  logoutButton: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "center",
    padding: spacing.lg,
    backgroundColor: "rgba(239, 68, 68, 0.1)", // Error color transparent
    borderRadius: borderRadius.lg,
    marginTop: spacing.xl,
    borderWidth: 1,
    borderColor: "rgba(239, 68, 68, 0.2)",
  },
  logoutText: {
    ...typography.bodyMedium,
    color: colors.error,
    marginLeft: spacing.sm,
    fontWeight: "600",
  },
  versionText: {
    ...typography.captionSmall,
    color: colors.textTertiary,
    textAlign: "center",
    marginTop: spacing.xxxl,
    marginBottom: spacing.xl,
  },
});
