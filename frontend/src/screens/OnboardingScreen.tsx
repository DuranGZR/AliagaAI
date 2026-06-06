import React, { useState, useEffect, useRef } from "react";
import {
  View,
  Text,
  StyleSheet,
  Dimensions,
  TouchableOpacity,
  SafeAreaView,
  Platform,
  Animated,
  Image,
} from "react-native";
import { Ionicons } from "@expo/vector-icons";
import { LinearGradient } from "expo-linear-gradient";
import { colors, spacing, typography, borderRadius } from "../theme";
import { useAuth } from "../context/AuthContext";

const { width, height } = Dimensions.get("window");

interface OnboardingSlide {
  id: string;
  title: string;
  subtitle: string;
  description: string;
  icon: string;
  accentColor: string;
  gradient: readonly [string, string, ...string[]];
}

const slides: OnboardingSlide[] = [
  {
    id: "1",
    title: "AliağaAI",
    subtitle: "Şehir Asistanı",
    description:
      "Aliağa hakkında merak ettiğiniz her şeyi yapay zekaya sorun. Tarihi yerlerden resmi kurumlara kadar her bilgiye anında ulaşın.",
    icon: "chatbubble-ellipses-outline",
    accentColor: "#C8A96E", // Premium Gold
    gradient: ["#000000", "#050403", "#0B0906"] as const,
  },
  {
    id: "2",
    title: "Rehber & Ulaşım",
    subtitle: "Hayatı Kolaylaştırın",
    description:
      "Nöbetçi eczaneler, güncel İZBAN sefer saatleri, otobüs hatları ve keşfedilmeyi bekleyen rotalar tek dokunuşla parmaklarınızın ucunda.",
    icon: "location-outline",
    accentColor: "#4E7E63", // Subtle Emerald/Gold
    gradient: ["#000000", "#020403", "#040806"] as const,
  },
  {
    id: "3",
    title: "Belediye & İletişim",
    subtitle: "Daima Bağlantıda Kalın",
    description:
      "Etkinlikler, duyurular, aktif iş ilanları ve belediyeniz ile kesintisiz iletişim kanalları. Şehrin nabzını buradan takip edin.",
    icon: "library-outline",
    accentColor: "#5B749E", // Subtle Sapphire/Gold
    gradient: ["#000000", "#020305", "#04060A"] as const,
  },
];

export function OnboardingScreen() {
  const { completeOnboarding } = useAuth();
  const [currentIndex, setCurrentIndex] = useState(0);

  const fadeAnim = useRef(new Animated.Value(0)).current;
  const buttonScale = useRef(new Animated.Value(1)).current;

  useEffect(() => {
    // Reset and start fade transition for text layout
    fadeAnim.setValue(0);
    Animated.timing(fadeAnim, {
      toValue: 1,
      duration: 650,
      useNativeDriver: Platform.OS !== "web",
    }).start();
  }, [currentIndex]);

  const handleNext = () => {
    if (currentIndex < slides.length - 1) {
      setCurrentIndex(currentIndex + 1);
    } else {
      completeOnboarding();
    }
  };

  const handleSkip = () => {
    completeOnboarding();
  };

  const handleNextPressIn = () => {
    Animated.spring(buttonScale, {
      toValue: 0.95,
      friction: 7,
      tension: 50,
      useNativeDriver: Platform.OS !== "web",
    }).start();
  };

  const handleNextPressOut = () => {
    Animated.spring(buttonScale, {
      toValue: 1,
      friction: 7,
      tension: 50,
      useNativeDriver: Platform.OS !== "web",
    }).start();
  };

  const currentSlide = slides[currentIndex];

  return (
    <View style={styles.container}>
      {/* 
        Key={currentIndex} forces React to destroy and rebuild the slide view 
        when the index changes, preventing caching issues on React Native Web.
      */}
      <LinearGradient
        key={currentIndex}
        colors={currentSlide.gradient}
        style={styles.slide}
        start={{ x: 0.5, y: 0 }}
        end={{ x: 0.5, y: 1 }}
      >
        {/* Glow Effects in the Background */}
        <View style={[styles.bgGlow, { backgroundColor: currentSlide.accentColor }]} />
        <View style={[styles.bgGlowSecondary, { backgroundColor: currentSlide.accentColor }]} />

        {/* Center Content */}
        <SafeAreaView style={styles.contentContainer}>
          {/* Brand Logo Header */}
          <Image
            source={require("../../assets/logo.png")}
            style={styles.headerLogo}
            resizeMode="contain"
          />

          {/* Main Visual Symbol (Clean Gold Outline Icon) */}
          <View style={styles.iconWrapper}>
            <Ionicons 
              name={currentSlide.icon as any} 
              size={84} 
              color={currentSlide.accentColor} 
              style={styles.centerIcon}
            />
          </View>

          {/* Premium Clean Text Layout with Fade Transition */}
          <Animated.View style={{ opacity: fadeAnim, width: "100%" }}>
            <View style={styles.textContainer}>
              <Text style={[styles.tagText, { color: currentSlide.accentColor }]}>
                {currentSlide.subtitle.toUpperCase()}
              </Text>
              <Text style={styles.title}>{currentSlide.title}</Text>
              <View style={[styles.titleDivider, { backgroundColor: currentSlide.accentColor }]} />
              <Text style={styles.description}>{currentSlide.description}</Text>
            </View>
          </Animated.View>
        </SafeAreaView>
      </LinearGradient>

      {/* Control Footer */}
      <SafeAreaView style={styles.footer}>
        {/* Pagination Dots */}
        <View style={styles.pagination}>
          {slides.map((_, index) => (
            <TouchableOpacity
              key={index}
              onPress={() => setCurrentIndex(index)}
              style={styles.dotTouchable}
              hitSlop={{ top: 10, bottom: 10, left: 10, right: 10 }}
            >
              <View
                style={[
                  styles.dot,
                  currentIndex === index && [
                    styles.activeDot,
                    { backgroundColor: currentSlide.accentColor, shadowColor: currentSlide.accentColor }
                  ],
                ]}
              />
            </TouchableOpacity>
          ))}
        </View>

        {/* Buttons Action Bar */}
        <View style={styles.buttonContainer}>
          {currentIndex < slides.length - 1 ? (
            <TouchableOpacity onPress={handleSkip} style={styles.skipButton} activeOpacity={0.7}>
              <Text style={styles.skipButtonText}>Geç</Text>
            </TouchableOpacity>
          ) : (
            <View style={{ width: 60 }} />
          )}

          <Animated.View style={{ transform: [{ scale: buttonScale }] }}>
            <TouchableOpacity
              onPress={handleNext}
              onPressIn={handleNextPressIn}
              onPressOut={handleNextPressOut}
              style={[
                styles.nextButton,
                { borderColor: currentSlide.accentColor }
              ]}
              activeOpacity={0.85}
            >
              <Text style={[styles.nextButtonText, { color: currentSlide.accentColor }]}>
                {currentIndex === slides.length - 1 ? "Başla" : "İleri"}
              </Text>
              <Ionicons
                name={
                  currentIndex === slides.length - 1
                    ? "arrow-forward"
                    : "arrow-forward-outline"
                }
                size={16}
                color={currentSlide.accentColor}
                style={styles.nextIcon}
              />
            </TouchableOpacity>
          </Animated.View>
        </View>
      </SafeAreaView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#000000",
  },
  slide: {
    width: width,
    height: height,
    justifyContent: "center",
    alignItems: "center",
    position: "relative",
  },
  bgGlow: {
    position: "absolute",
    top: height * 0.18,
    width: width * 0.7,
    height: width * 0.7,
    borderRadius: (width * 0.7) / 2,
    opacity: 0.05,
    filter: "blur(80px)" as any, // Web compatibility
    ...Platform.select({
      ios: {
        shadowOpacity: 0.6,
        shadowRadius: 100,
        backgroundColor: colors.primary,
      },
    }),
  },
  bgGlowSecondary: {
    position: "absolute",
    bottom: height * 0.25,
    right: -width * 0.1,
    width: width * 0.5,
    height: width * 0.5,
    borderRadius: (width * 0.5) / 2,
    opacity: 0.04,
    filter: "blur(70px)" as any,
  },
  contentContainer: {
    alignItems: "center",
    width: "100%",
    paddingHorizontal: spacing.xl,
    marginTop: -spacing.xl,
  },
  headerLogo: {
    width: 140,
    height: 34,
    marginBottom: spacing.huge,
  },
  iconWrapper: {
    width: 140,
    height: 140,
    justifyContent: "center",
    alignItems: "center",
    marginBottom: spacing.xl,
  },
  centerIcon: {
    textShadowColor: "rgba(200, 169, 110, 0.2)",
    textShadowOffset: { width: 0, height: 4 },
    textShadowRadius: 15,
  },
  textContainer: {
    width: "100%",
    paddingHorizontal: spacing.md,
    alignItems: "center",
  },
  tagText: {
    ...typography.caption,
    fontFamily: "Outfit_700Bold",
    letterSpacing: 2.5,
    marginBottom: spacing.xs,
  },
  title: {
    ...typography.h2,
    fontFamily: "Outfit_800ExtraBold",
    color: colors.text,
    textAlign: "center",
    letterSpacing: 0.5,
  },
  titleDivider: {
    width: 48,
    height: 2,
    borderRadius: 1,
    marginVertical: spacing.md,
  },
  description: {
    ...typography.bodyMedium,
    color: colors.textSecondary,
    textAlign: "center",
    lineHeight: 23,
    opacity: 0.85,
  },
  footer: {
    position: "absolute",
    bottom: spacing.xxl,
    left: spacing.xl,
    right: spacing.xl,
    alignItems: "center",
  },
  pagination: {
    flexDirection: "row",
    marginBottom: spacing.xl,
    height: 24,
    alignItems: "center",
  },
  dotTouchable: {
    padding: spacing.xs,
  },
  dot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    backgroundColor: "rgba(255, 255, 255, 0.16)",
  },
  activeDot: {
    width: 24,
    shadowOffset: { width: 0, height: 0 },
    shadowOpacity: 0.6,
    shadowRadius: 6,
    elevation: 3,
  },
  buttonContainer: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    width: "100%",
    paddingHorizontal: spacing.sm,
  },
  skipButton: {
    paddingVertical: spacing.sm,
    paddingHorizontal: spacing.md,
  },
  skipButtonText: {
    ...typography.bodyMedium,
    color: colors.textTertiary,
    fontWeight: "600",
    letterSpacing: 0.5,
  },
  nextButton: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "center",
    paddingVertical: spacing.md,
    paddingHorizontal: spacing.xxl,
    minWidth: 120,
    height: 48,
    borderRadius: borderRadius.full,
    borderWidth: 1,
    backgroundColor: "transparent",
  },
  nextButtonText: {
    ...typography.button,
    fontWeight: "700",
    marginRight: spacing.xs,
    letterSpacing: 0.5,
  },
  nextIcon: {
    marginLeft: spacing.xs,
  },
});
