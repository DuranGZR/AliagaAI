import React from "react";
import {
  View,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  ActivityIndicator,
  Platform,
} from "react-native";
import { Ionicons } from "@expo/vector-icons";
import { colors, spacing, borderRadius, typography } from "../theme";

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
  placeholder = "Asistan'a bir şey söyle...",
  loading = false,
}: SearchBarProps) {
  return (
    <View style={styles.wrapper}>
      <View style={styles.container}>
        <TextInput
          style={styles.input}
          value={value}
          onChangeText={onChangeText}
          placeholder={placeholder}
          placeholderTextColor={colors.textTertiary}
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
            <ActivityIndicator size="small" color={colors.textInverse} />
          ) : (
            <Ionicons name="arrow-up" size={18} color={colors.textInverse} />
          )}
        </TouchableOpacity>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  wrapper: {
    paddingHorizontal: spacing.xl,
    paddingBottom: spacing.md,
    paddingTop: spacing.sm,
  },
  container: {
    flexDirection: "row",
    alignItems: "center",
    borderRadius: borderRadius.xxl,
    paddingHorizontal: spacing.lg,
    paddingVertical: Platform.OS === "ios" ? spacing.sm : 2,
    borderWidth: 1,
    borderColor: colors.border,
    backgroundColor: colors.surface,
  },
  input: {
    flex: 1,
    ...typography.body,
    color: colors.text,
    minHeight: 44,
  },
  action: {
    width: 34,
    height: 34,
    borderRadius: 17,
    backgroundColor: colors.primary,
    justifyContent: "center",
    alignItems: "center",
    marginLeft: spacing.sm,
  },
  actionDisabled: {
    backgroundColor: colors.textTertiary,
    opacity: 0.4,
  },
});
