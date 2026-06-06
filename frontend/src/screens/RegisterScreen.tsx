import React, { useState, useRef } from "react";
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
  Animated,
} from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { Ionicons } from "@expo/vector-icons";
import { useNavigation } from "@react-navigation/native";
import { LinearGradient } from "expo-linear-gradient";

import { colors, spacing, typography, borderRadius, shadows } from "../theme";
import { useAuth } from "../context/AuthContext";
import { showAlert } from "../utils/alert";

export function RegisterScreen() {
  const navigation = useNavigation<any>();
  const { register } = useAuth();

  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");

  const [nameError, setNameError] = useState("");
  const [emailError, setEmailError] = useState("");
  const [passwordError, setPasswordError] = useState("");
  const [confirmPasswordError, setConfirmPasswordError] = useState("");

  const [isNameFocused, setIsNameFocused] = useState(false);
  const [isEmailFocused, setIsEmailFocused] = useState(false);
  const [isPasswordFocused, setIsPasswordFocused] = useState(false);
  const [isConfirmPasswordFocused, setIsConfirmPasswordFocused] = useState(false);

  const shakeName = useRef(new Animated.Value(0)).current;
  const shakeEmail = useRef(new Animated.Value(0)).current;
  const shakePassword = useRef(new Animated.Value(0)).current;
  const shakeConfirmPassword = useRef(new Animated.Value(0)).current;

  const triggerShake = (anim: Animated.Value) => {
    Animated.sequence([
      Animated.timing(anim, { toValue: 10, duration: 60, useNativeDriver: Platform.OS !== "web" }),
      Animated.timing(anim, { toValue: -10, duration: 60, useNativeDriver: Platform.OS !== "web" }),
      Animated.timing(anim, { toValue: 10, duration: 60, useNativeDriver: Platform.OS !== "web" }),
      Animated.timing(anim, { toValue: -10, duration: 60, useNativeDriver: Platform.OS !== "web" }),
      Animated.timing(anim, { toValue: 0, duration: 60, useNativeDriver: Platform.OS !== "web" }),
    ]).start();
  };

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

  const handleConfirmPasswordChange = (val: string) => {
    setConfirmPassword(val);
    if (confirmPasswordError) setConfirmPasswordError("");
  };
  
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleRegister = async () => {
    let hasError = false;

    // Validations
    if (!name.trim()) {
      setNameError("Ad Soyad zorunludur.");
      triggerShake(shakeName);
      hasError = true;
    } else {
      setNameError("");
    }

    if (!email.trim() || !/\S+@\S+\.\S+/.test(email)) {
      if (!email.trim()) {
        setEmailError("E-posta adresi zorunludur.");
      } else {
        setEmailError("Geçersiz e-posta formatı.");
      }
      triggerShake(shakeEmail);
      hasError = true;
    } else {
      setEmailError("");
    }

    if (!password || password.length < 6) {
      if (!password) {
        setPasswordError("Şifre zorunludur.");
      } else {
        setPasswordError("Şifreniz en az 6 karakter olmalıdır.");
      }
      triggerShake(shakePassword);
      hasError = true;
    } else {
      setPasswordError("");
    }

    if (!confirmPassword || password !== confirmPassword) {
      if (!confirmPassword) {
        setConfirmPasswordError("Şifre tekrarı zorunludur.");
      } else {
        setConfirmPasswordError("Şifreler uyuşmuyor.");
      }
      triggerShake(shakeConfirmPassword);
      hasError = true;
    } else {
      setConfirmPasswordError("");
    }

    if (hasError) return;

    try {
      setLoading(true);
      await register(name.trim(), email.trim(), password);
    } catch (error: any) {
      const errMsg = error.response?.data?.detail || "Kayıt olurken bir hata oluştu. Lütfen tekrar deneyin.";
      showAlert("Hata", errMsg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <View style={styles.container}>
      <SafeAreaView style={styles.safeArea}>
        <KeyboardAvoidingView
          style={{ flex: 1 }}
          behavior={Platform.OS === "ios" ? "padding" : "height"}
        >
          <ScrollView contentContainerStyle={styles.scrollContent} keyboardShouldPersistTaps="handled">
            
            {/* Geri Butonu */}
            <TouchableOpacity
              style={styles.backButton}
              onPress={() => navigation.goBack()}
              hitSlop={{ top: 10, bottom: 10, left: 10, right: 10 }}
            >
              <Ionicons name="arrow-back" size={24} color={colors.text} />
            </TouchableOpacity>

            {/* Logo ve Başlık */}
            <View style={styles.header}>
              <View style={styles.logoContainer}>
                <Ionicons name="person-add" size={38} color={colors.primary} />
                <View style={styles.logoGlow} />
              </View>
              <Text style={styles.title}>Hesap Oluştur</Text>
              <Text style={styles.subtitle}>AliağaAI ailesine katılın</Text>
            </View>

            {/* Form */}
            <View style={styles.form}>
              
              {/* Ad Soyad */}
              <View style={styles.inputGroup}>
                <Text style={styles.inputLabel}>Ad Soyad</Text>
                <Animated.View style={[
                  styles.inputContainer, 
                  nameError ? styles.inputErrorBorder : null,
                  isNameFocused ? styles.inputFocusedBorder : null,
                  { transform: [{ translateX: shakeName }] }
                ]}>
                  <Ionicons name="person-outline" size={20} color={isNameFocused ? colors.primary : colors.textTertiary} style={styles.inputIcon} />
                  <TextInput
                    style={styles.input}
                    value={name}
                    onChangeText={handleNameChange}
                    placeholder="Adınız Soyadınız"
                    placeholderTextColor={colors.textTertiary}
                    autoCapitalize="words"
                    autoCorrect={false}
                    onFocus={() => setIsNameFocused(true)}
                    onBlur={() => setIsNameFocused(false)}
                  />
                </Animated.View>
                {nameError ? <Text style={styles.errorText}>{nameError}</Text> : null}
              </View>

              {/* E-posta */}
              <View style={styles.inputGroup}>
                <Text style={styles.inputLabel}>E-posta Adresi</Text>
                <Animated.View style={[
                  styles.inputContainer, 
                  emailError ? styles.inputErrorBorder : null,
                  isEmailFocused ? styles.inputFocusedBorder : null,
                  { transform: [{ translateX: shakeEmail }] }
                ]}>
                  <Ionicons name="mail-outline" size={20} color={isEmailFocused ? colors.primary : colors.textTertiary} style={styles.inputIcon} />
                  <TextInput
                    style={styles.input}
                    value={email}
                    onChangeText={handleEmailChange}
                    placeholder="ornek@aliaga.com"
                    placeholderTextColor={colors.textTertiary}
                    keyboardType="email-address"
                    autoCapitalize="none"
                    autoCorrect={false}
                    onFocus={() => setIsEmailFocused(true)}
                    onBlur={() => setIsEmailFocused(false)}
                  />
                </Animated.View>
                {emailError ? <Text style={styles.errorText}>{emailError}</Text> : null}
              </View>

              {/* Şifre */}
              <View style={styles.inputGroup}>
                <Text style={styles.inputLabel}>Şifre</Text>
                <Animated.View style={[
                  styles.inputContainer, 
                  passwordError ? styles.inputErrorBorder : null,
                  isPasswordFocused ? styles.inputFocusedBorder : null,
                  { transform: [{ translateX: shakePassword }] }
                ]}>
                  <Ionicons name="lock-closed-outline" size={20} color={isPasswordFocused ? colors.primary : colors.textTertiary} style={styles.inputIcon} />
                  <TextInput
                    style={styles.input}
                    value={password}
                    onChangeText={handlePasswordChange}
                    placeholder="En az 6 karakter"
                    placeholderTextColor={colors.textTertiary}
                    secureTextEntry={!showPassword}
                    autoCapitalize="none"
                    autoCorrect={false}
                    onFocus={() => setIsPasswordFocused(true)}
                    onBlur={() => setIsPasswordFocused(false)}
                  />
                  <TouchableOpacity onPress={() => setShowPassword(!showPassword)} style={styles.eyeIcon}>
                    <Ionicons
                      name={showPassword ? "eye-off-outline" : "eye-outline"}
                      size={20}
                      color={isPasswordFocused ? colors.primary : colors.textSecondary}
                    />
                  </TouchableOpacity>
                </Animated.View>
                {passwordError ? <Text style={styles.errorText}>{passwordError}</Text> : null}
              </View>

              {/* Şifre Tekrar */}
              <View style={styles.inputGroup}>
                <Text style={styles.inputLabel}>Şifre Tekrar</Text>
                <Animated.View style={[
                  styles.inputContainer, 
                  confirmPasswordError ? styles.inputErrorBorder : null,
                  isConfirmPasswordFocused ? styles.inputFocusedBorder : null,
                  { transform: [{ translateX: shakeConfirmPassword }] }
                ]}>
                  <Ionicons name="lock-closed-outline" size={20} color={isConfirmPasswordFocused ? colors.primary : colors.textTertiary} style={styles.inputIcon} />
                  <TextInput
                    style={styles.input}
                    value={confirmPassword}
                    onChangeText={handleConfirmPasswordChange}
                    placeholder="Şifreyi tekrar girin"
                    placeholderTextColor={colors.textTertiary}
                    secureTextEntry={!showConfirmPassword}
                    autoCapitalize="none"
                    autoCorrect={false}
                    onFocus={() => setIsConfirmPasswordFocused(true)}
                    onBlur={() => setIsConfirmPasswordFocused(false)}
                  />
                  <TouchableOpacity onPress={() => setShowConfirmPassword(!showConfirmPassword)} style={styles.eyeIcon}>
                    <Ionicons
                      name={showConfirmPassword ? "eye-off-outline" : "eye-outline"}
                      size={20}
                      color={isConfirmPasswordFocused ? colors.primary : colors.textSecondary}
                    />
                  </TouchableOpacity>
                </Animated.View>
                {confirmPasswordError ? <Text style={styles.errorText}>{confirmPasswordError}</Text> : null}
              </View>

              {/* Kaydol Butonu */}
              <TouchableOpacity style={styles.registerButton} onPress={handleRegister} disabled={loading}>
                <LinearGradient
                  colors={colors.gradients.primary as any}
                  style={styles.registerButtonGradient}
                  start={{ x: 0, y: 0 }}
                  end={{ x: 1, y: 0 }}
                >
                  {loading ? (
                    <ActivityIndicator color={colors.background} size="small" />
                  ) : (
                    <Text style={styles.registerButtonText}>Hesap Oluştur</Text>
                  )}
                </LinearGradient>
              </TouchableOpacity>
            </View>

            {/* Yönlendirme */}
            <View style={styles.footer}>
              <Text style={styles.footerText}>Zaten bir hesabınız var mı?</Text>
              <TouchableOpacity onPress={() => navigation.navigate("Login")}>
                <Text style={styles.loginLink}> Giriş Yapın</Text>
              </TouchableOpacity>
            </View>

          </ScrollView>
        </KeyboardAvoidingView>
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
  scrollContent: {
    padding: spacing.xl,
    flexGrow: 1,
    justifyContent: "center",
  },
  backButton: {
    position: "absolute",
    top: spacing.md,
    left: spacing.xl,
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: colors.surfaceLight,
    justifyContent: "center",
    alignItems: "center",
    zIndex: 10,
  },
  header: {
    alignItems: "center",
    marginBottom: spacing.xxl,
    marginTop: spacing.xxl,
  },
  logoContainer: {
    width: 80,
    height: 80,
    borderRadius: 40,
    backgroundColor: "rgba(200, 169, 110, 0.12)",
    justifyContent: "center",
    alignItems: "center",
    marginBottom: spacing.md,
    position: "relative",
  },
  logoGlow: {
    position: "absolute",
    width: 70,
    height: 70,
    borderRadius: 35,
    borderWidth: 1,
    borderColor: "rgba(200, 169, 110, 0.2)",
    ...shadows.glow,
  },
  title: {
    ...typography.h2,
    color: colors.text,
    fontWeight: "800",
  },
  subtitle: {
    ...typography.bodyMedium,
    color: colors.textSecondary,
    marginTop: spacing.xs,
  },
  form: {
    width: "100%",
  },
  inputGroup: {
    marginBottom: spacing.lg,
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
  inputIcon: {
    marginRight: spacing.md,
  },
  input: {
    flex: 1,
    ...typography.body,
    color: colors.text,
    height: "100%",
  },
  eyeIcon: {
    padding: spacing.xs,
  },
  registerButton: {
    marginTop: spacing.xl,
    borderRadius: borderRadius.full,
    overflow: "hidden",
    ...shadows.glow,
  },
  registerButtonGradient: {
    height: 56,
    justifyContent: "center",
    alignItems: "center",
  },
  registerButtonText: {
    ...typography.button,
    color: colors.background,
    fontWeight: "700",
  },
  footer: {
    flexDirection: "row",
    justifyContent: "center",
    alignItems: "center",
    marginTop: spacing.xxl,
    marginBottom: spacing.xl,
  },
  footerText: {
    ...typography.bodyMedium,
    color: colors.textSecondary,
  },
  loginLink: {
    ...typography.bodyMedium,
    color: colors.primary,
    fontWeight: "700",
  },
  inputErrorBorder: {
    borderColor: colors.error,
  },
  inputFocusedBorder: {
    borderColor: colors.primary,
    shadowColor: colors.primary,
    shadowOffset: { width: 0, height: 0 },
    shadowOpacity: 0.25,
    shadowRadius: 8,
    elevation: 4,
  },
  errorText: {
    ...typography.captionSmall,
    color: colors.error,
    marginTop: spacing.xs,
    marginLeft: spacing.xs,
  },
});
