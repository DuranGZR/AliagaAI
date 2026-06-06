import React, { useState } from "react";
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ScrollView,
  Alert,
  Image,
  Modal,
  Switch,
  Platform,
} from "react-native";
import { BlurView } from "expo-blur";
import { SafeAreaView } from "react-native-safe-area-context";
import { Ionicons } from "@expo/vector-icons";
import { useNavigation } from "@react-navigation/native";
import { LinearGradient } from "expo-linear-gradient";
import { colors, spacing, typography, borderRadius } from "../theme";
import { useAuth } from "../context/AuthContext";
import { showAlert, showConfirm } from "../utils/alert";

export function SettingsProfileScreen() {
  const navigation = useNavigation<any>();
  const { user, logout, resetOnboarding } = useAuth();

  // Custom Modal States
  const [modalType, setModalType] = useState<"notifications" | "about" | "support" | null>(null);

  // Mock switches for notification settings
  const [notifyAI, setNotifyAI] = useState(true);
  const [notifyOutages, setNotifyOutages] = useState(true);
  const [notifyNews, setNotifyNews] = useState(false);

  const handleLogout = () => {
    showConfirm(
      "Çıkış Yap",
      "Hesabınızdan çıkış yapmak istediğinize emin misiniz?",
      async () => {
        await logout();
        navigation.goBack(); // Modalı kapat
      },
      "Çıkış Yap",
      "İptal"
    );
  };

  const handleResetOnboarding = () => {
    showConfirm(
      "Tanıtımı Sıfırla",
      "Tanıtım (Splash) ekranlarını sıfırlamak ve uygulamayı yeniden başlatmak istiyor musunuz?",
      async () => {
        await resetOnboarding();
        navigation.goBack();
      },
      "Sıfırla",
      "İptal"
    );
  };

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
          <View style={{ width: 28 }} />
        </View>

        <ScrollView contentContainerStyle={styles.scrollContent} showsVerticalScrollIndicator={false}>
          {/* Profile Section */}
          <LinearGradient colors={colors.gradients.surface} style={styles.profileCard}>
            {user?.avatar_url ? (
              user.avatar_url.startsWith("symbol:") ? (
                <View style={styles.profileAvatar}>
                  <Ionicons name={(user.avatar_url.split(":")[1] || "person") as any} size={32} color={colors.primary} />
                </View>
              ) : (
                <Image source={{ uri: user.avatar_url }} style={styles.profileAvatarImage} />
              )
            ) : (
              <View style={styles.profileAvatar}>
                <Ionicons name="person" size={32} color={colors.primary} />
              </View>
            )}
            
            <View style={styles.profileInfo}>
              <View style={styles.nameRow}>
                <Text style={styles.profileName} numberOfLines={1}>
                  {user?.full_name || "Aliağa Sakini"}
                </Text>
                {user?.is_google_user && (
                  <View style={styles.googleBadge}>
                    <Ionicons name="logo-google" size={10} color={colors.background} />
                  </View>
                )}
              </View>
              <Text style={styles.profileEmail} numberOfLines={1}>
                {user?.email || "kullanici@aliaga.com"}
              </Text>
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
              onPress={() => setModalType("notifications")}
            >
              <View style={styles.optionIconContainer}>
                <Ionicons name="notifications" size={20} color={colors.text} />
              </View>
              <Text style={styles.optionText}>Bildirimler</Text>
              <Ionicons name="chevron-forward" size={20} color={colors.textSecondary} />
            </TouchableOpacity>
          </View>

          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Uygulama & Geliştirici</Text>

            <TouchableOpacity
              style={styles.optionRow}
              onPress={handleResetOnboarding}
            >
              <View style={styles.optionIconContainer}>
                <Ionicons name="refresh-circle" size={20} color={colors.primary} />
              </View>
              <Text style={styles.optionText}>Tanıtımı Sıfırla (Onboarding)</Text>
              <Ionicons name="chevron-forward" size={20} color={colors.textSecondary} />
            </TouchableOpacity>

            <TouchableOpacity
              style={styles.optionRow}
              onPress={() => setModalType("about")}
            >
              <View style={styles.optionIconContainer}>
                <Ionicons name="information-circle" size={20} color={colors.text} />
              </View>
              <Text style={styles.optionText}>Hakkında</Text>
              <Ionicons name="chevron-forward" size={20} color={colors.textSecondary} />
            </TouchableOpacity>

            <TouchableOpacity
              style={styles.optionRow}
              onPress={() => setModalType("support")}
            >
              <View style={styles.optionIconContainer}>
                <Ionicons name="mail" size={20} color={colors.text} />
              </View>
              <Text style={styles.optionText}>İletişim & Destek</Text>
              <Ionicons name="chevron-forward" size={20} color={colors.textSecondary} />
            </TouchableOpacity>
          </View>

          {/* Çıkış Butonu */}
          <TouchableOpacity
            style={styles.logoutButton}
            onPress={handleLogout}
          >
            <Ionicons name="log-out-outline" size={20} color={colors.error} />
            <Text style={styles.logoutText}>Çıkış Yap</Text>
          </TouchableOpacity>

          <Text style={styles.versionText}>AliağaAI v3.0.0</Text>
        </ScrollView>
      </SafeAreaView>

      {/* Detay Açıklama Modalı */}
      <Modal
        visible={modalType !== null}
        transparent={true}
        animationType="slide"
        onRequestClose={() => setModalType(null)}
      >
        <View style={styles.modalOverlay}>
          <TouchableOpacity 
            style={styles.modalOverlayDismiss}
            activeOpacity={1}
            onPress={() => setModalType(null)}
          />
          <View style={styles.modalContent}>
            {/* Modal Drag Indicator */}
            <View style={styles.modalIndicator} />
            
            {/* Modal Header */}
            <View style={styles.modalHeader}>
              <Text style={styles.modalTitle}>
                {modalType === "notifications" && "Bildirim Ayarları"}
                {modalType === "about" && "AliağaAI Hakkında"}
                {modalType === "support" && "İletişim & Destek"}
              </Text>
              <TouchableOpacity onPress={() => setModalType(null)} style={styles.modalCloseButton}>
                <Ionicons name="close" size={24} color={colors.text} />
              </TouchableOpacity>
            </View>

            {/* Modal Body */}
            <ScrollView showsVerticalScrollIndicator={false} contentContainerStyle={styles.modalBody}>
              {modalType === "notifications" && (
                <View style={styles.modalSubSection}>
                  <Text style={styles.modalDescription}>
                    AliağaAI'den anlık bildirimler alarak şehirdeki gelişmelerden anında haberdar olun.
                  </Text>
                  
                  <View style={styles.switchRow}>
                    <View style={styles.switchTextContainer}>
                      <Text style={styles.switchTitle}>Yapay Zeka Asistanı</Text>
                      <Text style={styles.switchSubtitle}>Sorularınıza verilen yanıt bildirimleri</Text>
                    </View>
                    <Switch
                      value={notifyAI}
                      onValueChange={setNotifyAI}
                      trackColor={{ false: "rgba(255,255,255,0.08)", true: colors.primary }}
                      thumbColor={notifyAI ? colors.background : colors.textSecondary}
                    />
                  </View>

                  <View style={styles.switchRow}>
                    <View style={styles.switchTextContainer}>
                      <Text style={styles.switchTitle}>Arıza & Kesintiler</Text>
                      <Text style={styles.switchSubtitle}>Su ve elektrik kesintisi duyuruları</Text>
                    </View>
                    <Switch
                      value={notifyOutages}
                      onValueChange={setNotifyOutages}
                      trackColor={{ false: "rgba(255,255,255,0.08)", true: colors.primary }}
                      thumbColor={notifyOutages ? colors.background : colors.textSecondary}
                    />
                  </View>

                  <View style={styles.switchRow}>
                    <View style={styles.switchTextContainer}>
                      <Text style={styles.switchTitle}>Haberler & Etkinlikler</Text>
                      <Text style={styles.switchSubtitle}>Aliağa'daki güncel kültür sanat haberleri</Text>
                    </View>
                    <Switch
                      value={notifyNews}
                      onValueChange={setNotifyNews}
                      trackColor={{ false: "rgba(255,255,255,0.08)", true: colors.primary }}
                      thumbColor={notifyNews ? colors.background : colors.textSecondary}
                    />
                  </View>
                </View>
              )}

              {modalType === "about" && (
                <View style={styles.modalSubSection}>
                  <View style={styles.aboutBranding}>
                    <Ionicons name="hardware-chip" size={48} color={colors.primary} />
                    <Text style={styles.aboutAppName}>AliağaAI</Text>
                    <Text style={styles.aboutVersion}>Sürüm 3.0.0 (Gold Edition)</Text>
                  </View>
                  <Text style={styles.aboutText}>
                    Aliağa Belediyesi'nin akıllı ve modern şehircilik vizyonunun bir parçası olarak geliştirilen AliağaAI; vatandaşlarımızın güncel nöbetçi eczanelere, ulaşım sefer saatlerine, su ve elektrik kesintilerine, semt pazarı bilgilerine ve haberlere anında erişmesini hedefleyen yapay zeka destekli bir asistan uygulamasıdır.
                  </Text>
                  <View style={styles.aboutFooter}>
                    <Text style={styles.aboutFooterText}>Aliağa Belediyesi Bilgi İşlem Müdürlüğü</Text>
                    <Text style={styles.aboutFooterSubtext}>© 2026 Tüm Hakları Saklıdır.</Text>
                  </View>
                </View>
              )}

              {modalType === "support" && (
                <View style={styles.modalSubSection}>
                  <Text style={styles.modalDescription}>
                    Sorularınız, önerileriniz veya teknik destek ihtiyaçlarınız için aşağıdaki resmi belediye iletişim kanallarını kullanabilirsiniz.
                  </Text>

                  <TouchableOpacity style={styles.supportCard} activeOpacity={0.8}>
                    <Ionicons name="call" size={20} color={colors.primary} />
                    <View style={styles.supportCardContent}>
                      <Text style={styles.supportCardTitle}>Belediye Çağrı Merkezi</Text>
                      <Text style={styles.supportCardValue}>ALO SES 153</Text>
                    </View>
                    <Ionicons name="chevron-forward" size={16} color={colors.textTertiary} />
                  </TouchableOpacity>

                  <TouchableOpacity style={styles.supportCard} activeOpacity={0.8}>
                    <Ionicons name="mail" size={20} color={colors.primary} />
                    <View style={styles.supportCardContent}>
                      <Text style={styles.supportCardTitle}>Destek E-posta Adresi</Text>
                      <Text style={styles.supportCardValue}>destek@aliaga.bel.tr</Text>
                    </View>
                    <Ionicons name="chevron-forward" size={16} color={colors.textTertiary} />
                  </TouchableOpacity>

                  <TouchableOpacity style={styles.supportCard} activeOpacity={0.8}>
                    <Ionicons name="globe" size={20} color={colors.primary} />
                    <View style={styles.supportCardContent}>
                      <Text style={styles.supportCardTitle}>Resmi Web Portalı</Text>
                      <Text style={styles.supportCardValue}>www.aliaga.bel.tr</Text>
                    </View>
                    <Ionicons name="chevron-forward" size={16} color={colors.textTertiary} />
                  </TouchableOpacity>
                </View>
              )}
            </ScrollView>
          </View>
        </View>
      </Modal>
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
    marginBottom: spacing.xxl,
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
  profileAvatarImage: {
    width: 60,
    height: 60,
    borderRadius: 30,
    marginRight: spacing.lg,
    borderWidth: 1,
    borderColor: colors.primary,
  },
  profileInfo: {
    flex: 1,
  },
  nameRow: {
    flexDirection: "row",
    alignItems: "center",
    marginBottom: 4,
  },
  profileName: {
    ...typography.h3,
    color: colors.text,
    marginRight: spacing.xs,
    maxWidth: "80%",
  },
  googleBadge: {
    width: 16,
    height: 16,
    borderRadius: 8,
    backgroundColor: colors.primary,
    justifyContent: "center",
    alignItems: "center",
  },
  profileEmail: {
    ...typography.bodySmall,
    color: colors.textSecondary,
    maxWidth: "95%",
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
    backgroundColor: "rgba(239, 68, 68, 0.1)",
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
  modalOverlay: {
    flex: 1,
    backgroundColor: "rgba(0,0,0,0.85)",
    justifyContent: "flex-end",
  },
  modalOverlayDismiss: {
    position: "absolute",
    top: 0,
    bottom: 0,
    left: 0,
    right: 0,
  },
  modalContent: {
    backgroundColor: "rgba(22, 22, 26, 0.98)",
    borderTopLeftRadius: 30,
    borderTopRightRadius: 30,
    borderWidth: 1,
    borderColor: "rgba(200, 169, 110, 0.25)",
    paddingHorizontal: spacing.xl,
    paddingTop: spacing.md,
    paddingBottom: spacing.huge,
    maxHeight: "85%",
  },
  modalIndicator: {
    width: 44,
    height: 4,
    borderRadius: 2,
    backgroundColor: "rgba(255,255,255,0.15)",
    alignSelf: "center",
    marginBottom: spacing.md,
  },
  modalHeader: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    marginBottom: spacing.lg,
    borderBottomWidth: 1,
    borderBottomColor: "rgba(255, 255, 255, 0.05)",
    paddingBottom: spacing.sm,
  },
  modalTitle: {
    ...typography.h3,
    color: colors.primary,
    fontWeight: "800",
  },
  modalCloseButton: {
    width: 32,
    height: 32,
    borderRadius: 16,
    backgroundColor: "rgba(255,255,255,0.05)",
    justifyContent: "center",
    alignItems: "center",
  },
  modalBody: {
    paddingBottom: spacing.xxl,
  },
  modalSubSection: {
    gap: spacing.lg,
  },
  modalDescription: {
    ...typography.bodyMedium,
    color: colors.textSecondary,
    lineHeight: 22,
    marginBottom: spacing.sm,
  },
  switchRow: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    backgroundColor: "rgba(255, 255, 255, 0.02)",
    padding: spacing.md,
    borderRadius: borderRadius.md,
    borderWidth: 1,
    borderColor: "rgba(255, 255, 255, 0.05)",
  },
  switchTextContainer: {
    flex: 1,
    paddingRight: spacing.md,
  },
  switchTitle: {
    ...typography.bodyMedium,
    color: colors.text,
    fontWeight: "700",
    marginBottom: 2,
  },
  switchSubtitle: {
    ...typography.captionSmall,
    color: colors.textSecondary,
  },
  aboutBranding: {
    alignItems: "center",
    marginVertical: spacing.md,
    gap: spacing.xs,
  },
  aboutAppName: {
    ...typography.h2,
    color: colors.text,
    fontFamily: "Outfit_700Bold",
  },
  aboutVersion: {
    ...typography.caption,
    color: colors.primary,
    letterSpacing: 1.5,
  },
  aboutText: {
    ...typography.bodyMedium,
    color: colors.textSecondary,
    lineHeight: 24,
    textAlign: "center",
    paddingHorizontal: spacing.sm,
  },
  aboutFooter: {
    alignItems: "center",
    marginTop: spacing.xl,
  },
  aboutFooterText: {
    ...typography.caption,
    color: colors.textSecondary,
    fontWeight: "600",
  },
  aboutFooterSubtext: {
    ...typography.captionSmall,
    color: colors.textTertiary,
    marginTop: 2,
  },
  supportCard: {
    flexDirection: "row",
    alignItems: "center",
    backgroundColor: "rgba(255, 255, 255, 0.02)",
    padding: spacing.lg,
    borderRadius: borderRadius.md,
    borderWidth: 1,
    borderColor: "rgba(250, 204, 21, 0.12)",
    gap: spacing.md,
  },
  supportCardContent: {
    flex: 1,
  },
  supportCardTitle: {
    ...typography.caption,
    color: colors.textSecondary,
    marginBottom: 2,
  },
  supportCardValue: {
    ...typography.bodyMedium,
    color: colors.text,
    fontWeight: "700",
  },
});
