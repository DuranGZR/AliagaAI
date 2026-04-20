import React, { useState, useRef, useCallback } from "react";
import {
  View,
  FlatList,
  StyleSheet,
  KeyboardAvoidingView,
  Platform,
  Text,
  ActivityIndicator,
} from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { LinearGradient } from "expo-linear-gradient";
import { Ionicons } from "@expo/vector-icons";

import { SearchBar } from "../components/SearchBar";
import { ChatBubble } from "../components/ChatBubble";
import { PlaceCard } from "../components/PlaceCard";
import { chatService } from "../services/api";
import { ChatMessage } from "../types";
import { colors, spacing, typography, borderRadius } from "../theme";

export function ChatScreen() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const flatListRef = useRef<FlatList>(null);

  const handleSend = useCallback(async () => {
    const query = input.trim();
    if (!query || loading) return;

    const userMsg: ChatMessage = {
      id: Date.now().toString(),
      role: "user",
      content: query,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setLoading(true);

    try {
      const response = await chatService.send(query);
      const assistantMsg: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: response.ai_response || "Aradığın bilgiye şu an ulaşamadım, ama Aliağa hakkında sormaya devam edebilirsin.",
        timestamp: new Date(),
        results: response.results,
      };
      setMessages((prev) => [...prev, assistantMsg]);
    } catch {
      const errorMsg: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: "Bağlantıda küçük bir aksaklık oldu. Lütfen tekrar dener misin?",
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setLoading(false);
    }
  }, [input, loading]);

  const renderItem = useCallback(({ item }: { item: ChatMessage }) => {
    return (
      <View style={styles.messageWrapper}>
        <ChatBubble role={item.role} content={item.content} />
        {item.results && item.results.length > 0 && (
          <View style={styles.resultsContainer}>
            {item.results.slice(0, 3).map((result, index) => (
              <PlaceCard
                key={`${item.id}-${index}`}
                name={result.name || result.title || "—"}
                category={result.category}
                address={result.address}
                phone={result.phone}
                rating={result.rating}
                tags={result.tags}
                maps_link={result.maps_link}
              />
            ))}
          </View>
        )}
      </View>
    );
  }, []);

  return (
    <LinearGradient
      colors={colors.gradients.bg as any}
      style={styles.container}
    >
      <SafeAreaView style={styles.safeArea} edges={["top"]}>
        <View style={styles.header}>
            <View>
                <Text style={styles.title}>Aliağa asistanı</Text>
                <Text style={styles.subtitle}>Sohbet Geçmişi</Text>
            </View>
        </View>

        {messages.length === 0 ? (
          <View style={styles.emptyContainer}>
            <Ionicons name="chatbubble-ellipses-outline" size={64} color={colors.textTertiary} />
            <Text style={styles.emptyTitle}>Sohbet Başlasın</Text>
            <Text style={styles.emptySubtitle}>
              Aliağa hakkında ne öğrenmek istersin? Restoranlar, tarihi alanlar veya eczaneler...
            </Text>
          </View>
        ) : (
          <FlatList
            ref={flatListRef}
            data={messages}
            renderItem={renderItem}
            keyExtractor={(item) => item.id}
            contentContainerStyle={styles.listContent}
            showsVerticalScrollIndicator={false}
            onContentSizeChange={() =>
              flatListRef.current?.scrollToEnd({ animated: true })
            }
          />
        )}

        {loading && (
          <View style={styles.loadingContainer}>
            <ActivityIndicator size="small" color={colors.primary} />
            <Text style={styles.loadingText}>Asistan araştırıyor...</Text>
          </View>
        )}

        <KeyboardAvoidingView
          behavior={Platform.OS === "ios" ? "padding" : undefined}
          keyboardVerticalOffset={Platform.OS === "ios" ? 0 : 20}
          style={styles.inputArea}
        >
          <SearchBar
            value={input}
            onChangeText={setInput}
            onSubmit={handleSend}
            loading={loading}
          />
        </KeyboardAvoidingView>
      </SafeAreaView>
    </LinearGradient>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  safeArea: {
    flex: 1,
  },
  header: {
    paddingHorizontal: spacing.xl,
    paddingVertical: spacing.lg,
    alignItems: "center",
  },
  title: {
    ...typography.h2,
    color: colors.text,
    textAlign: "center"
  },
  subtitle: {
    ...typography.caption,
    color: colors.textSecondary,
    textAlign: "center",
    marginTop: 4,
  },
  emptyContainer: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
    paddingHorizontal: spacing.huge,
  },
  emptyTitle: {
    ...typography.h3,
    color: colors.textSecondary,
    marginTop: spacing.lg,
    marginBottom: spacing.xs,
  },
  emptySubtitle: {
    ...typography.bodySmall,
    color: colors.textTertiary,
    textAlign: "center",
    lineHeight: 20,
  },
  listContent: {
    paddingVertical: spacing.lg,
    paddingBottom: 100, // Make room for Pill Nav
  },
  messageWrapper: {
    marginBottom: spacing.lg,
  },
  resultsContainer: {
    paddingHorizontal: spacing.lg,
    marginTop: spacing.md,
  },
  loadingContainer: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "center",
    gap: spacing.sm,
    paddingVertical: spacing.md,
  },
  loadingText: {
    ...typography.bodySmall,
    color: colors.textSecondary,
  },
  inputArea: {
    paddingBottom: 80, // Height of bottom tab
  }
});
