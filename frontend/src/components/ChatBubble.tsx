import React from "react";
import { View, Text, StyleSheet } from "react-native";
import { Ionicons } from "@expo/vector-icons";
import { colors, spacing, borderRadius, typography } from "../theme";

interface ChatBubbleProps {
  role: "user" | "assistant";
  content: string;
}

export function ChatBubble({ role, content }: ChatBubbleProps) {
  const isUser = role === "user";

  if (isUser) {
    return (
      <View style={[styles.row, styles.rowUser]}>
        <View style={[styles.bubble, styles.bubbleUser]}>
          <Text style={[styles.text, styles.textUser]}>{content}</Text>
        </View>
      </View>
    );
  }

  return (
    <View style={styles.row}>
      <View style={styles.assistantContainer}>
        {/* AI Badge */}
        <View style={styles.aiBadge}>
          <Ionicons name="hardware-chip" size={14} color={colors.primary} />
          <Text style={styles.aiBadgeText}>ALİAĞA DOSTU</Text>
        </View>
        {/* Mesaj */}
        <Text style={[styles.text, styles.textAssistant]}>{content}</Text>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  row: {
    flexDirection: "row",
    marginBottom: spacing.xs,
    paddingHorizontal: spacing.lg,
  },
  rowUser: {
    justifyContent: "flex-end",
  },
  bubble: {
    maxWidth: "85%",
    paddingHorizontal: spacing.xl,
    paddingVertical: spacing.md,
    borderRadius: borderRadius.xl,
  },
  bubbleUser: {
    backgroundColor: colors.userBubble,
    borderBottomRightRadius: 4,
  },
  assistantContainer: {
    maxWidth: "90%",
    paddingRight: spacing.md,
    padding: spacing.md,
    backgroundColor: "rgba(255, 255, 255, 0.03)",
    borderRadius: borderRadius.md,
    borderLeftWidth: 2,
    borderLeftColor: colors.primary,
  },
  aiBadge: {
    flexDirection: "row",
    alignItems: "center",
    gap: spacing.xs,
    marginBottom: spacing.sm,
  },
  aiBadgeText: {
    ...typography.captionSmall,
    color: colors.primary,
    fontWeight: "700",
    letterSpacing: 1,
  },
  text: {
    ...typography.body,
    lineHeight: 24,
  },
  textUser: {
    color: colors.text,
  },
  textAssistant: {
    color: colors.text,
  },
});
