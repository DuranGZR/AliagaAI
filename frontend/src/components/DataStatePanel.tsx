import React from "react";
import { StyleSheet, Text, View } from "react-native";
import { Ionicons } from "@expo/vector-icons";

import { borderRadius, colors, spacing, typography } from "../theme";

type Props = {
  title: string;
  text: string;
  tone?: "info" | "warning" | "error" | "success";
};

export function DataStatePanel({ title, text, tone = "info" }: Props) {
  const toneColor =
    tone === "error"
      ? colors.error
      : tone === "warning"
        ? colors.warning
        : tone === "success"
          ? colors.success
          : colors.info;

  return (
    <View style={[styles.panel, { borderColor: `${toneColor}38` }]}>
      <View style={[styles.iconWrap, { backgroundColor: `${toneColor}22` }]}>
        <Ionicons
          name={tone === "error" ? "warning-outline" : tone === "success" ? "checkmark-circle-outline" : "information-circle-outline"}
          size={20}
          color={toneColor}
        />
      </View>
      <View style={styles.copy}>
        <Text style={styles.title}>{title}</Text>
        <Text style={styles.text}>{text}</Text>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  panel: {
    minHeight: 78,
    borderRadius: borderRadius.lg,
    borderWidth: 1,
    backgroundColor: "rgba(24,24,28,0.9)",
    padding: spacing.md,
    flexDirection: "row",
    alignItems: "center",
  },
  iconWrap: {
    width: 36,
    height: 36,
    borderRadius: 18,
    alignItems: "center",
    justifyContent: "center",
    marginRight: spacing.md,
  },
  copy: {
    flex: 1,
  },
  title: {
    ...typography.bodyMedium,
    color: colors.text,
    fontWeight: "700",
  },
  text: {
    ...typography.bodySmall,
    color: colors.textSecondary,
    marginTop: 2,
  },
});

