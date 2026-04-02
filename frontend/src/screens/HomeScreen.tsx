import React, { useState, useRef, useCallback } from "react";
import {
  View,
  FlatList,
  StyleSheet,
  KeyboardAvoidingView,
  Platform,
  Text,
  ActivityIndicator,
  TouchableOpacity,
} from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { LinearGradient } from "expo-linear-gradient";
import { BlurView } from "expo-blur";
import { Ionicons } from "@expo/vector-icons";

import { SearchBar } from "../components/SearchBar";
import { ChatBubble } from "../components/ChatBubble";
import { PlaceCard } from "../components/PlaceCard";
import { chatService } from "../services/api";
import { ChatMessage } from "../types";
import { colors, spacing, typography, shadows, borderRadius } from "../theme";

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
                <Text style={styles.title}>AliağaAI</Text>
                <Text style={styles.subtitle}>İlham Veren Şehir Rehberin</Text>
            </View>
            <TouchableOpacity style={styles.headerAction}>
                <Ionicons name="sparkles" size={24} color={colors.primary} />
            </TouchableOpacity>
        </View>

        {messages.length === 0 ? (
          <View style={styles.emptyContainer}>
            <LinearGradient
              colors={["#3B82F6", "#2563EB"]}
              style={styles.heroIconContainer}
            >
              <Ionicons name="chatbubbles" size={48} color="white" />
            </LinearGradient>
            
            <Text style={styles.heroTitle}>Nasıl yardımcı olabilirim?</Text>
            <Text style={styles.heroSubtitle}>
              Aliağa'nın tarihi, lezzet durakları veya nöbetçi eczaneleri... Merak ettiğin her şeyi bana sorabilirsin.
            </Text>
            
            <View style={styles.suggestionsGrid}>
              {[
                "Nöbetçi Eczaneler",
                "Gezilecek Yerler",
                "Haftalık Etkinlikler",
                "Lezzet Durakları",
              ].map((s) => (
                <TouchableOpacity
                  key={s}
                  style={styles.suggestionItem}
                  onPress={() => setInput(s)}
                >
                  <Text style={styles.suggestionText}>{s}</Text>
                </TouchableOpacity>
              ))}
            </View>
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
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
  },
  title: {
    ...typography.h1,
    color: colors.text,
  },
  subtitle: {
    ...typography.bodySmall,
    color: colors.textSecondary,
    marginTop: -4,
  },
  headerAction: {
    width: 44,
    height: 44,
    borderRadius: 22,
    backgroundColor: "white",
    justifyContent: "center",
    alignItems: "center",
    ...shadows.soft,
  },
  emptyContainer: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
    paddingHorizontal: spacing.huge,
  },
  heroIconContainer: {
    width: 96,
    height: 96,
    borderRadius: 32,
    justifyContent: "center",
    alignItems: "center",
    marginBottom: spacing.xxl,
    ...shadows.premium,
  },
  heroTitle: {
    ...typography.h2,
    color: colors.text,
    textAlign: "center",
    marginBottom: spacing.sm,
  },
  heroSubtitle: {
    ...typography.body,
    color: colors.textSecondary,
    textAlign: "center",
    lineHeight: 24,
    marginBottom: spacing.huge,
  },
  suggestionsGrid: {
    flexDirection: "row",
    flexWrap: "wrap",
    justifyContent: "center",
    gap: spacing.md,
  },
  suggestionItem: {
    paddingHorizontal: spacing.xl,
    paddingVertical: spacing.md,
    borderRadius: borderRadius.xl,
    backgroundColor: "white",
    borderWidth: 1,
    borderColor: colors.border,
    ...shadows.soft,
  },
  suggestionText: {
    ...typography.bodyMedium,
    color: colors.primary,
  },
  listContent: {
    paddingVertical: spacing.lg,
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
});
