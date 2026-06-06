import React from "react";
import { View, Text, StyleSheet, Platform } from "react-native";
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

  // Helper function to render inline styles (bold text)
  const renderInlineStyles = (text: string) => {
    const parts = [];
    const boldRegex = /\*\*(.*?)\*\*/g;
    let lastIndex = 0;
    let match;

    while ((match = boldRegex.exec(text)) !== null) {
      const matchIndex = match.index;
      
      // Plain text chunk
      if (matchIndex > lastIndex) {
        parts.push(text.substring(lastIndex, matchIndex));
      }
      
      // Bold text chunk
      parts.push(
        <Text key={`bold-${matchIndex}`} style={styles.boldText}>
          {match[1]}
        </Text>
      );
      
      lastIndex = boldRegex.lastIndex;
    }

    if (lastIndex < text.length) {
      parts.push(text.substring(lastIndex));
    }

    return parts.length > 0 ? parts : text;
  };

  // Helper function to parse markdown lines into React Native components
  const parseMarkdown = (text: string) => {
    if (!text) return null;
    const lines = text.split("\n");
    const components = [];
    
    let inCodeBlock = false;
    let codeLanguage = "";
    let codeLines: string[] = [];
    
    for (let i = 0; i < lines.length; i++) {
      const line = lines[i];
      const trimmed = line.trim();
      
      if (trimmed.startsWith("```")) {
        if (inCodeBlock) {
          // Close code block
          const codeText = codeLines.join("\n");
          const displayLang = codeLanguage.toUpperCase() || "CODE";
          components.push(
            <View key={`code-${i}`} style={styles.codeBlockContainer}>
              <View style={styles.codeBlockHeader}>
                <Text style={styles.codeBlockLang}>{displayLang}</Text>
                <View style={styles.codeBlockDot} />
              </View>
              <Text style={styles.codeBlockText}>{codeText}</Text>
            </View>
          );
          inCodeBlock = false;
          codeLanguage = "";
          codeLines = [];
        } else {
          // Open code block
          inCodeBlock = true;
          codeLanguage = trimmed.replace("```", "").trim();
        }
        continue;
      }
      
      if (inCodeBlock) {
        codeLines.push(line);
        continue;
      }
      
      // Empty lines
      if (!trimmed) {
        components.push(<View key={`empty-${i}`} style={styles.emptyLine} />);
        continue;
      }

      // Headings: ### Title or #### Title
      const headingMatch = line.match(/^(#{1,6})\s+(.*)$/);
      if (headingMatch) {
        const level = headingMatch[1].length;
        let headerText = headingMatch[2];
        // Strip any extra bold markers inside header
        headerText = headerText.replace(/\*\*/g, "");
        
        components.push(
          <Text
            key={`heading-${i}`}
            style={[
              styles.text,
              styles.textAssistant,
              styles.heading,
              level === 1 ? styles.h1 : level === 2 ? styles.h2 : styles.h3,
            ]}
          >
            {headerText}
          </Text>
        );
        continue;
      }

      // Bullet list items starting with "* " or "- "
      const bulletMatch = line.match(/^[\*\-]\s+(.*)$/);
      if (bulletMatch) {
        const bulletContent = bulletMatch[1];
        components.push(
          <View key={`bullet-${i}`} style={styles.bulletRow}>
            <Text style={[styles.text, styles.textAssistant, styles.bulletDot]}>•</Text>
            <Text style={[styles.text, styles.textAssistant, styles.bulletText]}>
              {renderInlineStyles(bulletContent)}
            </Text>
          </View>
        );
        continue;
      }

      // Numbered list items starting with "1. " or "2. " etc.
      const numberedMatch = line.match(/^(\d+)\.\s+(.*)$/);
      if (numberedMatch) {
        const num = numberedMatch[1];
        const content = numberedMatch[2];
        components.push(
          <View key={`number-${i}`} style={styles.bulletRow}>
            <Text style={[styles.text, styles.textAssistant, styles.bulletDot]}>{num}.</Text>
            <Text style={[styles.text, styles.textAssistant, styles.bulletText]}>
              {renderInlineStyles(content)}
            </Text>
          </View>
        );
        continue;
      }

      // Standard paragraph
      components.push(
        <Text key={`para-${i}`} style={[styles.text, styles.textAssistant, styles.paragraph]}>
          {renderInlineStyles(line)}
        </Text>
      );
    }
    
    // If the block is not closed at the end of the message, render what we have
    if (inCodeBlock && codeLines.length > 0) {
      const codeText = codeLines.join("\n");
      const displayLang = codeLanguage.toUpperCase() || "CODE";
      components.push(
        <View key={`code-unfinished`} style={styles.codeBlockContainer}>
          <View style={styles.codeBlockHeader}>
            <Text style={styles.codeBlockLang}>{displayLang}</Text>
            <View style={styles.codeBlockDot} />
          </View>
          <Text style={styles.codeBlockText}>{codeText}</Text>
        </View>
      );
    }
    
    return components;
  };

  return (
    <View style={styles.row}>
      <View style={styles.assistantContainer}>
        {/* AI Badge */}
        <View style={styles.aiBadge}>
          <Ionicons name="hardware-chip" size={14} color={colors.primary} />
          <Text style={styles.aiBadgeText}>ALİAĞA DOSTU</Text>
        </View>
        {/* Mesaj */}
        <View style={styles.markdownContainer}>
          {parseMarkdown(content)}
        </View>
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
  markdownContainer: {
    width: "100%",
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
  emptyLine: {
    height: spacing.xs,
  },
  heading: {
    fontFamily: "Outfit_700Bold",
    color: colors.primary,
    marginTop: spacing.md,
    marginBottom: spacing.xs,
  },
  h1: {
    ...typography.h1,
  },
  h2: {
    ...typography.h2,
  },
  h3: {
    ...typography.h3,
  },
  paragraph: {
    marginBottom: spacing.xs,
  },
  boldText: {
    fontFamily: "PlusJakartaSans_700Bold",
  },
  bulletRow: {
    flexDirection: "row",
    alignItems: "flex-start",
    marginBottom: spacing.xs,
    paddingLeft: spacing.sm,
    width: "100%",
  },
  bulletDot: {
    color: colors.primary,
    fontWeight: "700",
    marginRight: spacing.sm,
  },
  bulletText: {
    flex: 1,
  },
  codeBlockContainer: {
    marginVertical: spacing.md,
    backgroundColor: "rgba(10, 10, 10, 0.95)",
    borderWidth: 1.2,
    borderColor: "rgba(200, 169, 110, 0.25)",
    borderRadius: borderRadius.md,
    overflow: "hidden",
  },
  codeBlockHeader: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    backgroundColor: "rgba(200, 169, 110, 0.08)",
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.xs,
    borderBottomWidth: 1,
    borderBottomColor: "rgba(200, 169, 110, 0.15)",
  },
  codeBlockLang: {
    ...typography.captionSmall,
    color: colors.primary,
    fontWeight: "700",
    letterSpacing: 0.8,
  },
  codeBlockDot: {
    width: 6,
    height: 6,
    borderRadius: 3,
    backgroundColor: colors.primary,
  },
  codeBlockText: {
    fontFamily: Platform.OS === "ios" ? "Courier" : "monospace",
    fontSize: 13,
    color: "#E2D3B8",
    padding: spacing.md,
    lineHeight: 18,
  },
});
