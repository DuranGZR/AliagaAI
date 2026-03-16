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
import { SearchBar } from "../components/SearchBar";
import { ChatBubble } from "../components/ChatBubble";
import { PlaceCard } from "../components/PlaceCard";
import { chatService } from "../services/api";
import { ChatMessage } from "../types";
import { colors, spacing, typography } from "../theme";

export function HomeScreen() {
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
        content: response.ai_response || "Sonuç bulunamadı.",
        timestamp: new Date(),
        results: response.results,
      };
      setMessages((prev) => [...prev, assistantMsg]);
    } catch {
      const errorMsg: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: "Bağlantı hatası. Lütfen tekrar deneyin.",
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setLoading(false);
    }
  }, [input, loading]);

  const renderItem = useCallback(({ item }: { item: ChatMessage }) => {
    return (
      <View>
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
    <SafeAreaView style={styles.container} edges={["top"]}>
      <View style={styles.header}>
        <Text style={styles.title}>AliağaAI</Text>
        <Text style={styles.subtitle}>Şehir Rehberin</Text>
      </View>

      {messages.length === 0 ? (
        <View style={styles.emptyState}>
          <Text style={styles.emptyIcon}>🏙️</Text>
          <Text style={styles.emptyTitle}>Merhaba!</Text>
          <Text style={styles.emptyText}>
            Aliağa hakkında bilmek istediğin her şeyi sorabilirsin.
          </Text>
          <View style={styles.suggestions}>
            {[
              "Bugün nöbetçi eczane hangisi?",
              "Restoran öner",
              "Hafta sonu etkinlik var mı?",
            ].map((s) => (
              <Text
                key={s}
                style={styles.suggestion}
                onPress={() => {
                  setInput(s);
                }}
              >
                {s}
              </Text>
            ))}
          </View>
        </View>
      ) : (
        <FlatList
          ref={flatListRef}
          data={messages}
          renderItem={renderItem}
          keyExtractor={(item) => item.id}
          contentContainerStyle={styles.messagesList}
          onContentSizeChange={() =>
            flatListRef.current?.scrollToEnd({ animated: true })
          }
        />
      )}

      {loading && (
        <View style={styles.loadingRow}>
          <ActivityIndicator size="small" color={colors.primary} />
          <Text style={styles.loadingText}>Düşünüyorum...</Text>
        </View>
      )}

      <KeyboardAvoidingView
        behavior={Platform.OS === "ios" ? "padding" : undefined}
        keyboardVerticalOffset={90}
      >
        <SearchBar
          value={input}
          onChangeText={setInput}
          onSubmit={handleSend}
          loading={loading}
        />
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
  },
  header: {
    paddingHorizontal: spacing.xl,
    paddingTop: spacing.md,
    paddingBottom: spacing.sm,
  },
  title: {
    ...typography.h1,
    color: colors.primary,
  },
  subtitle: {
    ...typography.bodySmall,
    color: colors.textSecondary,
  },
  emptyState: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
    paddingHorizontal: spacing.xxxl,
  },
  emptyIcon: {
    fontSize: 48,
    marginBottom: spacing.lg,
  },
  emptyTitle: {
    ...typography.h2,
    color: colors.text,
    marginBottom: spacing.sm,
  },
  emptyText: {
    ...typography.body,
    color: colors.textSecondary,
    textAlign: "center",
    marginBottom: spacing.xxl,
  },
  suggestions: {
    gap: spacing.sm,
    width: "100%",
  },
  suggestion: {
    ...typography.body,
    color: colors.primary,
    backgroundColor: colors.primaryLight,
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.md,
    borderRadius: 12,
    textAlign: "center",
    overflow: "hidden",
  },
  messagesList: {
    paddingTop: spacing.md,
    paddingBottom: spacing.md,
  },
  resultsContainer: {
    paddingHorizontal: spacing.lg,
    marginBottom: spacing.md,
  },
  loadingRow: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "center",
    gap: spacing.sm,
    paddingVertical: spacing.sm,
  },
  loadingText: {
    ...typography.bodySmall,
    color: colors.textSecondary,
  },
});
