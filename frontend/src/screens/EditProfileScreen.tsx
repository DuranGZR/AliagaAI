import React, { useState } from "react";
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  TextInput,
  KeyboardAvoidingView,
  Platform,
  Alert,
  ActivityIndicator,
  ScrollView,
  Image,
  Modal,
} from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { Ionicons } from "@expo/vector-icons";
import { useNavigation } from "@react-navigation/native";
import { LinearGradient } from "expo-linear-gradient";

import { colors, spacing, typography, borderRadius, shadows } from "../theme";
import { useAuth } from "../context/AuthContext";
import { showAlert, showPrompt } from "../utils/alert";

const PRESET_AVATARS = [
  { icon: "person", label: "Klasik", value: "symbol:person" },
  { icon: "sparkles", label: "Asistan", value: "symbol:sparkles" },
  { icon: "compass", label: "Gezgin", value: "symbol:compass" },
  { icon: "business", label: "Vatandaş", value: "symbol:business" },
  { icon: "leaf", label: "Doğa", value: "symbol:leaf" },
  { icon: "heart", label: "Yardım", value: "symbol:heart" },
  { icon: "star", label: "Yıldız", value: "symbol:star" },
  { icon: "shield", label: "Güvenli", value: "symbol:shield" },
  { icon: "water", label: "Doğal", value: "symbol:water" },
] as const;

export function EditProfileScreen() {
  const navigation = useNavigation();
  const { user, updateProfile } = useAuth();

  const [name, setName] = useState(user?.full_name || "");
  const [email, setEmail] = useState(user?.email || "");
  const [password, setPassword] = useState("");
  const [avatarUrl, setAvatarUrl] = useState(user?.avatar_url || "");
  const [showAvatarModal, setShowAvatarModal] = useState(false);

  const [nameError, setNameError] = useState("");
  const [emailError, setEmailError] = useState("");
  const [passwordError, setPasswordError] = useState("");

  const handleNameChange = (val: string) => {
    setName(val);
    if (nameError) setNameError("");
  };

  const handleEmailChange = (val: string) => {
    setEmail(val);
    if (emailError) setEmailError("");
  };

  const handlePasswordChange = (val: string) => {
    setPassword(val);
    if (passwordError) setPasswordError("");
  };
  
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleSave = async () => {
    let hasError = false;

    if (!name.trim()) {
      setNameError("Ad Soyad alanı zorunludur.");
      hasError = true;
    } else {
      setNameError("");
    }

    if (!email.trim()) {
      setEmailError("E-posta alanı zorunludur.");
      hasError = true;
    } else if (!/\S+@\S+\.\S+/.test(email)) {
      setEmailError("Geçersiz e-posta formatı.");
      hasError = true;
    } else {
      setEmailError("");
    }

    if (password && password.length < 6) {
      setPasswordError("Şifre en az 6 karakter olmalıdır.");
      hasError = true;
    } else {
      setPasswordError("");
    }

    if (hasError) return;

    try {
      setLoading(true);
      await updateProfile({
        full_name: name.trim(),
        email: email.trim(),
        password: password ? password : undefined,
        avatar_url: avatarUrl ? avatarUrl.trim() : undefined,
      });
      
      showAlert("Başarılı", "Profiliniz başarıyla güncellendi.");
      navigation.goBack();
    } catch (error: any) {
      const errMsg = error.response?.data?.detail || "Profil güncellenirken bir hata oluştu.";
      showAlert("Hata", errMsg);
    } finally {
      setLoading(false);
    }
  };

  const handleSelectAvatar = () => {
    setShowAvatarModal(true);
  };

  return (
    <View style={styles.container}>
      <SafeAreaView style={styles.safeArea}>
        
        {/* Header */}
        <View style={styles.header}>
          <TouchableOpacity
            style={styles.backButton}
            onPress={() => navigation.goBack()}
            hitSlop={{ top: 10, bottom: 10, left: 10, right: 10 }}
          >
            <Ionicons name="arrow-back" size={24} color={colors.text} />
          </TouchableOpacity>
          <Text style={styles.headerTitle}>Profili Düzenle</Text>
          <View style={{ width: 24 }} />
        </View>

        <KeyboardAvoidingView
          style={{ flex: 1 }}
          behavior={Platform.OS === "ios" ? "padding" : "height"}
        >
          <ScrollView contentContainerStyle={styles.scrollContent} keyboardShouldPersistTaps="handled">
            
            {/* Avatar Section */}
            <View style={styles.avatarSection}>
              <View style={styles.avatarContainer}>
                {avatarUrl ? (
                  avatarUrl.startsWith("symbol:") ? (
                    <Ionicons name={(avatarUrl.split(":")[1] || "person") as any} size={48} color={colors.primary} />
                  ) : (
                    <Image source={{ uri: avatarUrl }} style={styles.avatarImage} />
                  )
                ) : (
                  <Ionicons name="person" size={48} color={colors.primary} />
                )}
                <TouchableOpacity style={styles.changeAvatarButton} onPress={handleSelectAvatar}>
                  <Ionicons name="camera" size={16} color={colors.background} />
                </TouchableOpacity>
              </View>
              <TouchableOpacity onPress={handleSelectAvatar}>
                <Text style={styles.changeAvatarText}>Profil Resmini Değiştir</Text>
              </TouchableOpacity>
            </View>

            {/* Form */}
            <View style={styles.formSection}>
              {/* Ad Soyad */}
              <View style={styles.inputGroup}>
                <Text style={styles.inputLabel}>Ad Soyad</Text>
                <View style={[styles.inputContainer, nameError ? styles.inputErrorBorder : null]}>
                  <Ionicons name="person-outline" size={20} color={colors.textTertiary} style={styles.inputIcon} />
                  <TextInput
                    style={styles.input}
                    value={name}
                    onChangeText={handleNameChange}
                    placeholder="Ad Soyad"
                    placeholderTextColor={colors.textTertiary}
                    autoCapitalize="words"
                    autoCorrect={false}
                  />
                </View>
                {nameError ? <Text style={styles.errorText}>{nameError}</Text> : null}
              </View>

              {/* E-posta */}
              <View style={styles.inputGroup}>
                <Text style={styles.inputLabel}>E-posta</Text>
                <View style={[styles.inputContainer, emailError ? styles.inputErrorBorder : null, user?.is_google_user && styles.disabledInput]}>
                  <Ionicons name="mail-outline" size={20} color={colors.textTertiary} style={styles.inputIcon} />
                  <TextInput
                    style={[styles.input, user?.is_google_user && { color: colors.textSecondary }]}
                    value={email}
                    onChangeText={handleEmailChange}
                    placeholder="E-posta Adresi"
                    placeholderTextColor={colors.textTertiary}
                    keyboardType="email-address"
                    autoCapitalize="none"
                    autoCorrect={false}
                    editable={!user?.is_google_user}
                  />
                </View>
                {emailError ? <Text style={styles.errorText}>{emailError}</Text> : null}
                {user?.is_google_user && (
                  <Text style={styles.helperText}>Google hesabına bağlı e-posta adresi değiştirilemez.</Text>
                )}
              </View>

              {/* Şifre (Sadece normal kullanıcılar değiştirebilir) */}
              {!user?.is_google_user ? (
                <View style={styles.inputGroup}>
                  <Text style={styles.inputLabel}>Yeni Şifre (Değiştirmek istemiyorsanız boş bırakın)</Text>
                  <View style={[styles.inputContainer, passwordError ? styles.inputErrorBorder : null]}>
                    <Ionicons name="lock-closed-outline" size={20} color={colors.textTertiary} style={styles.inputIcon} />
                    <TextInput
                      style={styles.input}
                      value={password}
                      onChangeText={handlePasswordChange}
                      placeholder="Yeni Şifre (en az 6 karakter)"
                      placeholderTextColor={colors.textTertiary}
                      secureTextEntry={!showPassword}
                      autoCapitalize="none"
                      autoCorrect={false}
                    />
                    <TouchableOpacity onPress={() => setShowPassword(!showPassword)} style={styles.eyeIcon}>
                      <Ionicons
                        name={showPassword ? "eye-off-outline" : "eye-outline"}
                        size={20}
                        color={colors.textSecondary}
                      />
                    </TouchableOpacity>
                  </View>
                  {passwordError ? <Text style={styles.errorText}>{passwordError}</Text> : null}
                </View>
              ) : (
                <View style={styles.inputGroup}>
                  <Text style={styles.inputLabel}>Şifre</Text>
                  <View style={[styles.inputContainer, styles.disabledInput]}>
                    <Ionicons name="lock-closed-outline" size={20} color={colors.textTertiary} style={styles.inputIcon} />
                    <Text style={styles.disabledText}>Google hesabı şifre gerektirmez.</Text>
                  </View>
                </View>
              )}
            </View>

            {/* Save Button */}
            <TouchableOpacity style={styles.saveButton} onPress={handleSave} disabled={loading}>
              <LinearGradient
                colors={colors.gradients.primary as any}
                style={styles.saveButtonGradient}
                start={{ x: 0, y: 0 }}
                end={{ x: 1, y: 0 }}
              >
                {loading ? (
                  <ActivityIndicator color={colors.background} size="small" />
                ) : (
                  <Text style={styles.saveButtonText}>Değişiklikleri Kaydet</Text>
                )}
              </LinearGradient>
            </TouchableOpacity>

          </ScrollView>
        </KeyboardAvoidingView>
      </SafeAreaView>

      {/* Avatar Seçici Modalı */}
      <Modal
        visible={showAvatarModal}
        transparent={true}
        animationType="fade"
        onRequestClose={() => setShowAvatarModal(false)}
      >
        <View style={styles.modalOverlay}>
          <View style={styles.modalContent}>
            <View style={styles.modalHeader}>
              <Ionicons name="images-outline" size={22} color={colors.primary} />
              <Text style={styles.modalTitle}>Profil Resmi Seçin</Text>
              <TouchableOpacity onPress={() => setShowAvatarModal(false)} style={styles.modalCloseButton}>
                <Ionicons name="close" size={24} color={colors.text} />
              </TouchableOpacity>
            </View>
            <Text style={styles.modalSubtitle}>Kullanmak istediğiniz ön tanımlı avatarı seçin:</Text>

            <View style={styles.avatarGrid}>
              {PRESET_AVATARS.map((item, index) => {
                const isSelected = avatarUrl === item.value;
                return (
                  <TouchableOpacity
                    key={index}
                    style={[styles.avatarGridItem, isSelected && styles.avatarGridItemSelected]}
                    onPress={() => {
                      setAvatarUrl(item.value);
                      setShowAvatarModal(false);
                    }}
                  >
                    <View style={styles.modalAvatarSymbolContainer}>
                      <Ionicons name={item.icon as any} size={28} color={colors.primary} />
                      <Text style={styles.modalAvatarSymbolLabel}>{item.label}</Text>
                    </View>
                    {isSelected && (
                      <View style={styles.checkmarkBadge}>
                        <Ionicons name="checkmark" size={12} color={colors.background} />
                      </View>
                    )}
                  </TouchableOpacity>
                );
              })}
            </View>

            <TouchableOpacity 
              style={styles.modalCustomButton}
              onPress={() => {
                setShowAvatarModal(false);
                setTimeout(() => {
                  showPrompt(
                    "Profil Fotoğrafı",
                    "Kullanmak istediğiniz profil resmi URL'sini girin:",
                    (url: string) => {
                      if (url) {
                        setAvatarUrl(url);
                      }
                    },
                    avatarUrl
                  );
                }, 400);
              }}
            >
              <Text style={styles.modalCustomButtonText}>Özel URL Tanımla...</Text>
            </TouchableOpacity>
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
  scrollContent: {
    padding: spacing.xl,
    flexGrow: 1,
  },
  avatarSection: {
    alignItems: "center",
    marginVertical: spacing.xl,
  },
  avatarContainer: {
    width: 100,
    height: 100,
    borderRadius: 50,
    backgroundColor: "rgba(200, 169, 110, 0.15)",
    justifyContent: "center",
    alignItems: "center",
    position: "relative",
    marginBottom: spacing.md,
  },
  avatarImage: {
    width: 100,
    height: 100,
    borderRadius: 50,
    borderWidth: 2,
    borderColor: colors.primary,
  },
  changeAvatarButton: {
    position: "absolute",
    bottom: 0,
    right: 0,
    backgroundColor: colors.primary,
    width: 32,
    height: 32,
    borderRadius: 16,
    justifyContent: "center",
    alignItems: "center",
    borderWidth: 3,
    borderColor: colors.background,
  },
  changeAvatarText: {
    ...typography.bodyMedium,
    color: colors.primary,
    fontWeight: "600",
  },
  formSection: {
    gap: spacing.lg,
    marginBottom: spacing.xxxl,
  },
  inputGroup: {
    marginBottom: spacing.sm,
  },
  inputLabel: {
    ...typography.bodySmall,
    color: colors.textSecondary,
    marginBottom: spacing.sm,
    marginLeft: spacing.xs,
  },
  inputContainer: {
    flexDirection: "row",
    alignItems: "center",
    backgroundColor: colors.surface,
    borderRadius: borderRadius.md,
    borderWidth: 1,
    borderColor: colors.borderLight,
    paddingHorizontal: spacing.md,
    height: 56,
  },
  disabledInput: {
    backgroundColor: "rgba(255, 255, 255, 0.02)",
    borderColor: "transparent",
  },
  inputIcon: {
    marginRight: spacing.md,
  },
  input: {
    flex: 1,
    ...typography.body,
    color: colors.text,
    height: "100%",
  },
  disabledText: {
    ...typography.body,
    color: colors.textTertiary,
  },
  helperText: {
    ...typography.captionSmall,
    color: colors.textTertiary,
    marginTop: spacing.xs,
    marginLeft: spacing.xs,
  },
  eyeIcon: {
    padding: spacing.xs,
  },
  saveButton: {
    marginTop: spacing.md,
    marginBottom: spacing.xl,
    borderRadius: borderRadius.full,
    overflow: "hidden",
    ...shadows.glow,
  },
  saveButtonGradient: {
    height: 56,
    justifyContent: "center",
    alignItems: "center",
  },
  saveButtonText: {
    ...typography.button,
    color: colors.background,
  },
  inputErrorBorder: {
    borderColor: colors.error,
  },
  errorText: {
    ...typography.captionSmall,
    color: colors.error,
    marginTop: spacing.xs,
    marginLeft: spacing.xs,
  },
  modalOverlay: {
    flex: 1,
    backgroundColor: "rgba(0, 0, 0, 0.75)",
    justifyContent: "flex-end",
  },
  modalContent: {
    backgroundColor: "#18181A",
    borderTopLeftRadius: borderRadius.xl,
    borderTopRightRadius: borderRadius.xl,
    padding: spacing.xl,
    paddingBottom: spacing.huge,
    borderTopWidth: 1,
    borderTopColor: colors.borderLight,
  },
  modalHeader: {
    flexDirection: "row",
    alignItems: "center",
    marginBottom: spacing.lg,
  },
  modalTitle: {
    ...typography.h3,
    color: colors.text,
    flex: 1,
    marginLeft: spacing.md,
    fontWeight: "700",
  },
  modalCloseButton: {
    padding: spacing.xs,
  },
  modalSubtitle: {
    ...typography.bodySmall,
    color: colors.textSecondary,
    marginBottom: spacing.xl,
  },
  avatarGrid: {
    flexDirection: "row",
    flexWrap: "wrap",
    justifyContent: "space-between",
    gap: spacing.md,
    marginBottom: spacing.xl,
  },
  avatarGridItem: {
    width: "30%",
    aspectRatio: 1,
    borderRadius: borderRadius.md,
    overflow: "hidden",
    borderWidth: 2,
    borderColor: "transparent",
    position: "relative",
  },
  avatarGridItemSelected: {
    borderColor: colors.primary,
  },
  modalAvatarSymbolContainer: {
    flex: 1,
    backgroundColor: "rgba(255, 255, 255, 0.02)",
    justifyContent: "center",
    alignItems: "center",
    padding: spacing.xs,
    borderRadius: borderRadius.md,
    borderWidth: 1,
    borderColor: "rgba(255, 255, 255, 0.05)",
  },
  modalAvatarSymbolLabel: {
    ...typography.captionSmall,
    color: colors.textSecondary,
    marginTop: 4,
    textAlign: "center",
    fontSize: 10,
    textTransform: "none",
  },
  checkmarkBadge: {
    position: "absolute",
    bottom: 4,
    right: 4,
    backgroundColor: colors.primary,
    width: 20,
    height: 20,
    borderRadius: 10,
    justifyContent: "center",
    alignItems: "center",
  },
  modalCustomButton: {
    backgroundColor: "rgba(255, 255, 255, 0.03)",
    borderWidth: 1,
    borderColor: "rgba(200, 169, 110, 0.25)",
    borderRadius: borderRadius.full,
    paddingVertical: spacing.md,
    alignItems: "center",
  },
  modalCustomButtonText: {
    ...typography.bodyMedium,
    color: colors.primary,
    fontWeight: "700",
  },
});
