import React from "react";
import { View, Text, StyleSheet } from "react-native";
import { BlurView } from "expo-blur";
import { colors, spacing, borderRadius, typography, shadows } from "../theme";

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
      <BlurView intensity={80} tint="light" style={[styles.bubble, styles.bubbleAssistant]}>
        <Text style={[styles.text, styles.textAssistant]}>{content}</Text>
      </BlurView>
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
    backgroundColor: colors.primary,
    borderBottomRightRadius: 4,
    ...shadows.soft,
  },
  bubbleAssistant: {
    backgroundColor: colors.surface,
    borderBottomLeftRadius: 4,
    borderWidth: 1,
    borderColor: colors.borderLight,
    ...shadows.soft,
  },
  text: {
    ...typography.body,
    lineHeight: 22,
  },
  textUser: {
    color: colors.textInverse,
    fontWeight: "500",
  },
  textAssistant: {
    color: colors.text,
  },
});
