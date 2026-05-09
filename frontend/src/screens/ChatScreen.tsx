import React, { useCallback, useEffect, useMemo, useRef, useState } from "react";
import {
  ActivityIndicator,
  FlatList,
  KeyboardAvoidingView,
  Platform,
  StyleSheet,
  Text,
  TextInput,
  TouchableOpacity,
  View,
} from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { Ionicons } from "@expo/vector-icons";
import { useRoute } from "@react-navigation/native";

import { AppHeader } from "../components/AppHeader";
import { chatService } from "../services/api";
import { ChatMessage, ConversationTurn } from "../types";
import { borderRadius, colors, spacing, typography } from "../theme";

type RouteParams = {
  presetPrompt?: string;
};

function toHistory(messages: ChatMessage[]): ConversationTurn[] {
  return messages
    .filter((m) => m.id !== "welcome")
    .map((m) => ({ role: m.role, content: m.content }))
    .slice(-10);
}

export function ChatScreen() {
  const route = useRoute();
  const params = (route.params || {}) as RouteParams;

  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: "welcome",
      role: "assistant",
      content: "Size nasıl yardımcı olabilirim?",
      timestamp: new Date(),
    },
  ]);
  const messagesRef = useRef<ChatMessage[]>(messages);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [presetHandled, setPresetHandled] = useState(false);
  const listRef = useRef<FlatList>(null);

  useEffect(() => {
    messagesRef.current = messages;
  }, [messages]);

  const addMessage = useCallback((message: ChatMessage) => {
    setMessages((prev) => {
      const next = [...prev, message];
      messagesRef.current = next;
      return next;
    });
  }, []);

  const sendQuery = useCallback(
    async (raw: string) => {
      const query = raw.trim();
      if (!query || loading) return;

      const userMsg: ChatMessage = {
        id: `${Date.now()}-u`,
        role: "user",
        content: query,
        timestamp: new Date(),
      };
      addMessage(userMsg);
      setInput("");
      setLoading(true);

      try {
        const history = toHistory([...messagesRef.current, userMsg]);
        const response = await chatService.send(query, history);
        const answer =
          (response as any).answer ||
          (response as any).ai_response ||
          "Aradığın bilgiye şu an ulaşamadım ama birlikte tekrar deneyebiliriz.";

        addMessage({
          id: `${Date.now()}-a`,
          role: "assistant",
          content: answer,
          timestamp: new Date(),
          results: ((response as any).sources || (response as any).results || []) as any,
        });
      } catch {
        addMessage({
          id: `${Date.now()}-e`,
          role: "assistant",
          content: "Bağlantıda kısa bir aksaklık oldu. Tekrar dener misin?",
          timestamp: new Date(),
        });
      } finally {
        setLoading(false);
      }
    },
    [addMessage, loading]
  );

  useEffect(() => {
    if (!params.presetPrompt || presetHandled) return;
    setPresetHandled(true);
    sendQuery(params.presetPrompt);
  }, [params.presetPrompt, presetHandled, sendQuery]);

  const onSend = useCallback(() => {
    sendQuery(input);
  }, [input, sendQuery]);

  const renderItem = useCallback(({ item }: { item: ChatMessage }) => {
    const isUser = item.role === "user";

    if (isUser) {
      return (
        <View style={styles.userRow}>
          <View style={styles.userBubble}>
            <Text style={styles.userText}>{item.content}</Text>
          </View>
        </View>
      );
    }

    return (
      <View style={styles.assistantWrap}>
        <View style={styles.assistantBadge}>
          <Ionicons name="hardware-chip" size={14} color={colors.primary} />
          <Text style={styles.assistantBadgeText}>ALİAĞAİ</Text>
        </View>
        <Text style={styles.assistantText}>{item.content}</Text>
      </View>
    );
  }, []);

  const hasConversation = useMemo(
    () => messages.some((m) => m.id !== "welcome"),
    [messages]
  );

  return (
    <View style={styles.container}>
      <SafeAreaView style={styles.safeArea} edges={["top"]}>
        <AppHeader />

        <View style={styles.listWrap}>
          <FlatList
            ref={listRef}
            data={messages}
            keyExtractor={(item) => item.id}
            renderItem={renderItem}
            showsVerticalScrollIndicator={false}
            contentContainerStyle={styles.listContent}
            onContentSizeChange={() => listRef.current?.scrollToEnd({ animated: true })}
            ListFooterComponent={
              loading ? (
                <View style={styles.loadingRow}>
                  <ActivityIndicator size="small" color={colors.primary} />
                </View>
              ) : null
            }
          />

          {!hasConversation && <View style={styles.emptySpacer} />}
        </View>

        <KeyboardAvoidingView
          behavior={Platform.OS === "ios" ? "padding" : undefined}
          keyboardVerticalOffset={Platform.OS === "ios" ? 0 : 20}
          style={styles.inputContainer}
        >
          <View style={styles.inputWrap}>
            <TextInput
              value={input}
              onChangeText={setInput}
              placeholder="Asistan'a bir şey söyle..."
              placeholderTextColor={colors.textTertiary}
              style={styles.input}
              onSubmitEditing={onSend}
              returnKeyType="send"
              editable={!loading}
            />
          </View>
          <TouchableOpacity
            style={[styles.sendBtn, (!input.trim() || loading) && styles.sendBtnDisabled]}
            onPress={onSend}
            disabled={!input.trim() || loading}
          >
            <Ionicons name="arrow-up" size={30} color={colors.textInverse} />
          </TouchableOpacity>
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
  listWrap: {
    flex: 1,
  },
  listContent: {
    paddingHorizontal: spacing.xl,
    paddingTop: spacing.lg,
    paddingBottom: 24,
  },
  assistantWrap: {
    marginBottom: spacing.xl,
  },
  assistantBadge: {
    flexDirection: "row",
    alignItems: "center",
    gap: spacing.xs,
    marginBottom: spacing.sm,
  },
  assistantBadgeText: {
    ...typography.caption,
    color: colors.primary,
    letterSpacing: 2,
  },
  assistantText: {
    fontSize: 16,
    lineHeight: 26,
    color: colors.text,
    fontWeight: "400",
    maxWidth: "94%",
  },
  userRow: {
    alignItems: "flex-end",
    marginBottom: spacing.xl,
  },
  userBubble: {
    maxWidth: "82%",
    backgroundColor: "rgba(26,22,18,0.98)",
    borderWidth: 1,
    borderColor: colors.borderLight,
    borderRadius: borderRadius.lg,
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.md,
  },
  userText: {
    fontSize: 16,
    lineHeight: 26,
    color: colors.text,
    fontWeight: "400",
  },
  loadingRow: {
    paddingVertical: spacing.md,
  },
  emptySpacer: {
    height: 160,
  },
  inputContainer: {
    paddingHorizontal: spacing.xl,
    paddingBottom: 84,
    paddingTop: spacing.sm,
  },
  inputWrap: {
    backgroundColor: "rgba(12,12,14,0.98)",
    borderWidth: 1,
    borderColor: colors.borderLight,
    borderRadius: borderRadius.lg,
    paddingLeft: spacing.lg,
    paddingRight: 72,
    minHeight: 62,
    justifyContent: "center",
  },
  input: {
    ...typography.body,
    color: colors.text,
  },
  sendBtn: {
    position: "absolute",
    right: spacing.xl,
    top: -6,
    width: 54,
    height: 54,
    borderRadius: borderRadius.lg,
    backgroundColor: colors.primary,
    justifyContent: "center",
    alignItems: "center",
  },
  sendBtnDisabled: {
    opacity: 0.4,
  },
});
