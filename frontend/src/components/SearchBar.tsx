import React from "react";
import {
  View,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  ActivityIndicator,
  Platform,
} from "react-native";
import { BlurView } from "expo-blur";
import { Ionicons } from "@expo/vector-icons";
import { colors, spacing, borderRadius, typography, shadows } from "../theme";

interface SearchBarProps {
  value: string;
  onChangeText: (text: string) => void;
  onSubmit: () => void;
  placeholder?: string;
  loading?: boolean;
}

export function SearchBar({
  value,
  onChangeText,
  onSubmit,
  placeholder = "Aliağa hakkında bir şey sor...",
  loading = false,
}: SearchBarProps) {
  return (
    <View style={styles.wrapper}>
      <BlurView intensity={60} tint="dark" style={styles.container}>
        <Ionicons
          name="chatbubble-ellipses-outline"
          size={20}
          color={colors.secondary}
          style={styles.icon}
        />
        <TextInput
          style={styles.input}
          value={value}
          onChangeText={onChangeText}
          placeholder={placeholder}
          placeholderTextColor={colors.textSecondary}
          multiline={false}
          returnKeyType="send"
          onSubmitEditing={onSubmit}
          editable={!loading}
        />
        <TouchableOpacity 
          onPress={onSubmit} 
          style={[styles.action, (!value.trim() || loading) && styles.actionDisabled]}
          disabled={!value.trim() || loading}
          activeOpacity={0.7}
        >
          {loading ? (
            <ActivityIndicator size="small" color="white" />
          ) : (
            <Ionicons name="arrow-up" size={20} color="white" />
          )}
        </TouchableOpacity>
      </BlurView>
    </View>
  );
}

const styles = StyleSheet.create({
  wrapper: {
    paddingHorizontal: spacing.xl,
    paddingBottom: spacing.xl,
    paddingTop: spacing.sm,
  },
  container: {
    flexDirection: "row",
    alignItems: "center",
    borderRadius: borderRadius.xxl,
    paddingHorizontal: spacing.md,
    paddingVertical: Platform.OS === "ios" ? spacing.sm : 2,
    borderWidth: 1,
    borderColor: colors.borderLight,
    ...shadows.glow,
    overflow: "hidden",
    backgroundColor: colors.glassDark,
  },
  icon: {
    marginLeft: spacing.sm,
    marginRight: spacing.sm,
  },
  input: {
    flex: 1,
    ...typography.body,
    color: colors.text,
    minHeight: 48,
  },
  action: {
    width: 36,
    height: 36,
    borderRadius: 18,
    backgroundColor: colors.secondary,
    justifyContent: "center",
    alignItems: "center",
    marginLeft: spacing.sm,
    ...shadows.glow,
  },
  actionDisabled: {
    backgroundColor: colors.textTertiary,
    opacity: 0.5,
  },
});
