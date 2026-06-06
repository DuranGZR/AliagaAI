import React, { useState, useEffect, useRef } from "react";
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
  Modal,
  Animated,
} from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { Ionicons } from "@expo/vector-icons";
import { useNavigation } from "@react-navigation/native";
import { LinearGradient } from "expo-linear-gradient";
import * as WebBrowser from "expo-web-browser";
import * as Google from "expo-auth-session/providers/google";

import { colors, spacing, typography, borderRadius, shadows } from "../theme";
import { useAuth } from "../context/AuthContext";
import { showAlert } from "../utils/alert";

WebBrowser.maybeCompleteAuthSession();

export function LoginScreen() {
  const navigation = useNavigation<any>();
  const { login, loginWithGoogle } = useAuth();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);

  // Inline Hata Durumları
  const [emailError, setEmailError] = useState("");
  const [passwordError, setPasswordError] = useState("");

  const [isEmailFocused, setIsEmailFocused] = useState(false);
  const [isPasswordFocused, setIsPasswordFocused] = useState(false);

  const shakeEmail = useRef(new Animated.Value(0)).current;
  const shakePassword = useRef(new Animated.Value(0)).current;

  const triggerShake = (anim: Animated.Value) => {
    Animated.sequence([
      Animated.timing(anim, { toValue: 10, duration: 60, useNativeDriver: Platform.OS !== "web" }),
      Animated.timing(anim, { toValue: -10, duration: 60, useNativeDriver: Platform.OS !== "web" }),
      Animated.timing(anim, { toValue: 10, duration: 60, useNativeDriver: Platform.OS !== "web" }),
      Animated.timing(anim, { toValue: -10, duration: 60, useNativeDriver: Platform.OS !== "web" }),
      Animated.timing(anim, { toValue: 0, duration: 60, useNativeDriver: Platform.OS !== "web" }),
    ]).start();
  };

  const handleEmailChange = (val: string) => {
    setEmail(val);
    if (emailError) setEmailError("");
  };

  const handlePasswordChange = (val: string) => {
    setPassword(val);
    if (passwordError) setPasswordError("");
  };
  


  // Google OAuth Ayarları (Kullanıcı kendi ID'lerini .env'den tanımlayacak)
  // Web platformunda webClientId'nin zorunlu olmasından dolayı, hata almamak için geçici bir dummy Client ID veriyoruz.
  const [request, response, promptAsync] = Google.useAuthRequest({
    clientId: process.env.EXPO_PUBLIC_WEB_CLIENT_ID || "dummy-client-id-for-web-simulation.apps.googleusercontent.com",
    androidClientId: process.env.EXPO_PUBLIC_ANDROID_CLIENT_ID || undefined,
    iosClientId: process.env.EXPO_PUBLIC_IOS_CLIENT_ID || undefined,
    webClientId: process.env.EXPO_PUBLIC_WEB_CLIENT_ID || "dummy-client-id-for-web-simulation.apps.googleusercontent.com",
    responseType: "id_token",
    scopes: ["openid", "profile", "email"],
  });

  useEffect(() => {
    if (response?.type === "success") {
      const { authentication } = response;
      const idToken = authentication?.idToken;
      if (idToken) {
        handleGoogleLoginWithToken(idToken);
      } else {
        showAlert("Google Giriş", "Google ID Token alınamadı.");
      }
    }
  }, [response]);

  // Web redirect akışında sayfa sıfırdan yüklendiği için URL'deki hash parametrelerini elle parse ediyoruz.
  useEffect(() => {
    if (Platform.OS === "web") {
      const hash = window.location.hash;
      if (hash) {
        const params = new URLSearchParams(hash.substring(1));
        const idToken = params.get("id_token");
        if (idToken) {
          // Hassas token bilgisini tarayıcı adres çubuğundan temizle
          window.history.replaceState({}, document.title, window.location.pathname + window.location.search);
          void handleGoogleLoginWithToken(idToken);
          return;
        }
      }

      const search = window.location.search;
      if (search) {
        const params = new URLSearchParams(search);
        const idToken = params.get("id_token");
        if (idToken) {
          window.history.replaceState({}, document.title, window.location.pathname);
          void handleGoogleLoginWithToken(idToken);
        }
      }
    }
  }, []);

  const handleGoogleLoginWithToken = async (token: string) => {
    try {
      setLoading(true);
      await loginWithGoogle(token);
    } catch (error: any) {
      const errMsg = error.response?.data?.detail || "Google ile giriş yapılırken bir hata oluştu.";
      showAlert("Hata", errMsg);
    } finally {
      setLoading(false);
    }
  };

  const triggerGoogleLogin = async () => {
    try {
      setLoading(true);
      await promptAsync({ windowName: "_self" });
    } catch (error: any) {
      console.warn("Real Google login trigger failed:", error);
      showAlert("Hata", "Google ile giriş başlatılamadı.");
    } finally {
      setLoading(false);
    }
  };

  const handleLogin = async () => {
    let hasError = false;
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
        setPasswordError("Şifre en az 6 karakter olmalıdır.");
      }
      triggerShake(shakePassword);
      hasError = true;
    } else {
      setPasswordError("");
    }

    if (hasError) return;

    try {
      setLoading(true);
      await login(email.trim(), password);
    } catch (error: any) {
      const errMsg = error.response?.data?.detail || "Giriş başarısız. Lütfen bilgilerinizi kontrol edin.";
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
            {/* Logo ve Başlık */}
            <View style={styles.header}>
              <View style={styles.logoContainer}>
                <Ionicons name="hardware-chip" size={48} color={colors.primary} />
                <View style={styles.logoGlow} />
              </View>
              <Text style={styles.appName}>ALİAĞAİ</Text>
              <Text style={styles.subtitle}>Şehrin Akıllı Asistanı</Text>
            </View>

            {/* Form */}
            <View style={styles.form}>
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
                    placeholder="••••••"
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

              {/* Giriş Butonu */}
              <TouchableOpacity style={styles.loginButton} onPress={handleLogin} disabled={loading}>
                <LinearGradient
                  colors={colors.gradients.primary as any}
                  style={styles.loginButtonGradient}
                  start={{ x: 0, y: 0 }}
                  end={{ x: 1, y: 0 }}
                >
                  {loading ? (
                    <ActivityIndicator color={colors.background} size="small" />
                  ) : (
                    <Text style={styles.loginButtonText}>Giriş Yap</Text>
                  )}
                </LinearGradient>
              </TouchableOpacity>

              <View style={styles.dividerContainer}>
                <View style={styles.dividerLine} />
                <Text style={styles.dividerText}>VEYA</Text>
                <View style={styles.dividerLine} />
              </View>

              {/* Google ile Giriş */}
              <TouchableOpacity style={styles.googleButton} onPress={triggerGoogleLogin} disabled={loading}>
                <Ionicons name="logo-google" size={20} color={colors.primary} style={styles.googleIcon} />
                <Text style={styles.googleButtonText}>Google ile Giriş Yap</Text>
              </TouchableOpacity>
            </View>

            {/* Yönlendirme */}
            <View style={styles.footer}>
              <Text style={styles.footerText}>Henüz bir hesabınız yok mu?</Text>
              <TouchableOpacity onPress={() => navigation.navigate("Register")}>
                <Text style={styles.registerLink}> Kaydolun</Text>
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
  header: {
    alignItems: "center",
    marginBottom: spacing.xxxl,
  },
  logoContainer: {
    width: 90,
    height: 90,
    borderRadius: 45,
    backgroundColor: "rgba(200, 169, 110, 0.12)",
    justifyContent: "center",
    alignItems: "center",
    marginBottom: spacing.md,
    position: "relative",
  },
  logoGlow: {
    position: "absolute",
    width: 80,
    height: 80,
    borderRadius: 40,
    borderWidth: 1,
    borderColor: "rgba(200, 169, 110, 0.2)",
    ...shadows.glow,
  },
  appName: {
    ...typography.logo,
    color: colors.text,
    fontSize: 26,
    letterSpacing: 4,
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
  loginButton: {
    marginTop: spacing.xl,
    borderRadius: borderRadius.full,
    overflow: "hidden",
    ...shadows.glow,
  },
  loginButtonGradient: {
    height: 56,
    justifyContent: "center",
    alignItems: "center",
  },
  loginButtonText: {
    ...typography.button,
    color: colors.background,
    fontWeight: "700",
  },
  dividerContainer: {
    flexDirection: "row",
    alignItems: "center",
    marginVertical: spacing.xl,
  },
  dividerLine: {
    flex: 1,
    height: 1,
    backgroundColor: colors.borderLight,
  },
  dividerText: {
    ...typography.caption,
    color: colors.textTertiary,
    marginHorizontal: spacing.md,
  },
  googleButton: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "center",
    backgroundColor: colors.surface,
    borderWidth: 1,
    borderColor: colors.border,
    height: 56,
    borderRadius: borderRadius.full,
    marginBottom: spacing.lg,
  },
  googleIcon: {
    marginRight: spacing.md,
  },
  googleButtonText: {
    ...typography.bodyMedium,
    color: colors.text,
    fontWeight: "600",
  },
  footer: {
    flexDirection: "row",
    justifyContent: "center",
    alignItems: "center",
    marginTop: spacing.xxl,
  },
  footerText: {
    ...typography.bodyMedium,
    color: colors.textSecondary,
  },
  registerLink: {
    ...typography.bodyMedium,
    color: colors.primary,
    fontWeight: "700",
  },
  // Modal Tasarımı
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
  googleAccountItem: {
    flexDirection: "row",
    alignItems: "center",
    padding: spacing.md,
    backgroundColor: "rgba(255,255,255,0.03)",
    borderRadius: borderRadius.lg,
    marginBottom: spacing.md,
    borderWidth: 1,
    borderColor: colors.borderLight,
  },
  googleAvatar: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: "#4285F4",
    justifyContent: "center",
    alignItems: "center",
    marginRight: spacing.md,
  },
  googleAvatarText: {
    ...typography.bodyMedium,
    color: colors.text,
    fontWeight: "700",
  },
  googleAccountInfo: {
    flex: 1,
  },
  googleAccountName: {
    ...typography.bodyMedium,
    color: colors.text,
    fontWeight: "600",
  },
  googleAccountEmail: {
    ...typography.bodySmall,
    color: colors.textSecondary,
  },
  modalFooterNote: {
    ...typography.captionSmall,
    color: colors.textTertiary,
    textAlign: "center",
    marginTop: spacing.xl,
    lineHeight: 16,
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
