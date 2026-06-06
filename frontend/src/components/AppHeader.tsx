import React from "react";
import { View, Text, TouchableOpacity, StyleSheet, Image, Platform } from "react-native";
import { Ionicons } from "@expo/vector-icons";
import { useNavigation } from "@react-navigation/native";
import { BlurView } from "expo-blur";
import { colors, spacing, typography } from "../theme";

interface AppHeaderProps {
  onNotificationPress?: () => void;
}

export function AppHeader({ onNotificationPress }: AppHeaderProps) {
  const navigation = useNavigation<any>();

  const content = (
    <>
      <TouchableOpacity
        style={styles.iconButton}
        onPress={() => navigation.navigate("SettingsProfile")}
        hitSlop={{ top: 10, bottom: 10, left: 10, right: 10 }}
      >
        <Ionicons name="menu" size={22} color={colors.textSecondary} />
      </TouchableOpacity>

      <Image
        source={require("../../assets/logo.png")}
        style={styles.logoImage}
        resizeMode="contain"
      />

      <TouchableOpacity
        style={styles.iconButton}
        onPress={onNotificationPress}
        hitSlop={{ top: 10, bottom: 10, left: 10, right: 10 }}
      >
        <Ionicons name="notifications" size={20} color={colors.textSecondary} />
        <View style={styles.dot} />
      </TouchableOpacity>
    </>
  );

  if (Platform.OS === "web") {
    return <View style={styles.container}>{content}</View>;
  }

  return (
    <BlurView intensity={60} tint="dark" style={styles.blurContainer}>
      <View style={styles.innerRow}>{content}</View>
    </BlurView>
  );
}

const styles = StyleSheet.create({
  container: {
    position: "absolute",
    top: 0,
    left: 0,
    right: 0,
    zIndex: 100,
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    paddingHorizontal: spacing.xl,
    paddingVertical: spacing.lg,
    borderBottomWidth: 1,
    borderBottomColor: colors.borderLight,
    backgroundColor: "rgba(10, 10, 10, 0.88)",
    ...Platform.select({
      web: {
        backdropFilter: "blur(20px)",
        WebkitBackdropFilter: "blur(20px)",
      } as any
    }),
  },
  blurContainer: {
    position: "absolute",
    top: 0,
    left: 0,
    right: 0,
    zIndex: 100,
    borderBottomWidth: 1,
    borderBottomColor: colors.borderLight,
    overflow: "hidden",
  },
  innerRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    paddingHorizontal: spacing.xl,
    paddingVertical: spacing.lg,
    backgroundColor: "rgba(10, 10, 10, 0.55)",
  },
  iconButton: {
    width: 36,
    height: 36,
    justifyContent: "center",
    alignItems: "center",
    position: "relative",
  },
  logoImage: {
    width: 140,
    height: 34,
  },
  dot: {
    position: "absolute",
    top: 6,
    right: 6,
    width: 8,
    height: 8,
    borderRadius: 4,
    backgroundColor: colors.primary,
  },
});