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
  Animated,
  Clipboard,
  ScrollView,
  Share,
} from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { Ionicons } from "@expo/vector-icons";
import { LinearGradient } from "expo-linear-gradient";
import { useNavigation, useRoute } from "@react-navigation/native";

import { AppHeader } from "../components/AppHeader";
import { chatService } from "../services/api";
import { ChatMessage, ConversationTurn, SearchResult } from "../types";
import { borderRadius, colors, spacing, typography } from "../theme";
import { openDirections, openPhone } from "../utils/externalActions";

type RouteParams = {
  presetPrompt?: string;
  presetPromptId?: string;
};

type IconName = keyof typeof Ionicons.glyphMap;

const PROMPT_SUGGESTIONS: Array<{
  icon: IconName;
  title: string;
  prompt: string;
  tone: string;
}> = [
  {
    icon: "medical-outline",
    title: "Nöbetçi Eczaneler",
    prompt: "Bugün Aliağa'daki nöbetçi eczaneleri adres, telefon ve yol tarifi bilgisiyle göster.",
    tone: colors.warning,
  },
  {
    icon: "car-outline",
    title: "Ulaşım & Taksi",
    prompt: "Aliağa ulaşım seçeneklerini, İZBAN kalkış saatlerini ve taksi duraklarını göster.",
    tone: colors.info,
  },
  {
    icon: "calendar-outline",
    title: "Etkinlik & Haber",
    prompt: "Aliağa'daki güncel haberleri ve bu haftaki etkinlikleri listele.",
    tone: colors.tertiary,
  },
  {
    icon: "water-outline",
    title: "Arıza & Kesintiler",
    prompt: "Aliağa'da bugün su veya elektrik kesintisi var mı? Mahalle bilgisiyle kontrol et.",
    tone: colors.success,
  },
];

function toHistory(messages: ChatMessage[]): ConversationTurn[] {
  return messages
    .filter((m) => m.id !== "welcome")
    .map((m) => ({ role: m.role, content: m.content }))
    .slice(-10);
}

function resultTitle(result: SearchResult): string {
  return result.name || result.title || result.content || result.type || "Kaynak";
}

function resultMeta(result: SearchResult): string {
  if (result.address) return result.address;
  if (result.phone) return result.phone;
  if (result.category) return result.category;
  if (result.date) return result.date;
  return result.type || "Sonuç";
}

function WelcomePanel({
  loading,
  onSelect,
  suggestions,
}: {
  loading: boolean;
  onSelect: (prompt: string) => void;
  suggestions: typeof PROMPT_SUGGESTIONS;
}) {
  const spinValue = useRef(new Animated.Value(0)).current;
  const pulseValue = useRef(new Animated.Value(1)).current;

  useEffect(() => {
    // Soft breathing core scale
    Animated.loop(
      Animated.sequence([
        Animated.timing(pulseValue, {
          toValue: 1.08,
          duration: 2500,
          useNativeDriver: Platform.OS !== "web",
        }),
        Animated.timing(pulseValue, {
          toValue: 1,
          duration: 2500,
          useNativeDriver: Platform.OS !== "web",
        }),
      ])
    ).start();

    // Constant ring rotation spin
    Animated.loop(
      Animated.timing(spinValue, {
        toValue: 1,
        duration: 15000,
        useNativeDriver: Platform.OS !== "web",
      })
    ).start();
  }, []);

  const spin = spinValue.interpolate({
    inputRange: [0, 1],
    outputRange: ["0deg", "360deg"],
  });

  return (
    <View style={styles.welcomeContainer}>
      {/* AI Assistant Avatar Glow */}
      <View style={styles.aiOrbContainer}>
        {/* Soft back-glow */}
        <Animated.View style={[styles.aiOrbBackGlow, { transform: [{ scale: pulseValue }] }]} />
        
        {/* Nested holographic rings */}
        <Animated.View style={[styles.aiOrbUltraOuterRing, { transform: [{ scale: pulseValue }] }]} />
        <Animated.View style={[styles.aiOrbOuterRing, { transform: [{ rotate: spin }] }]} />
        <Animated.View style={[styles.aiOrbMiddleRing, { transform: [{ scale: pulseValue }] }]} />
        
        {/* Obsidian core */}
        <Animated.View style={[styles.aiOrb, { transform: [{ scale: pulseValue }] }]}>
          <Ionicons name="sparkles" size={26} color={colors.primary} />
        </Animated.View>
      </View>

      <Text style={styles.aiKicker}>ALİAĞAİ YAPAY ZEKA ASİSTANI</Text>
      <Text style={styles.aiTitle}>Size nasıl yardımcı olabilirim?</Text>
      <Text style={styles.aiDescription}>
        Aliağa hakkında güncel nöbetçi eczaneleri, ulaşım seferlerini, kesintileri veya şehir tarihini bana sorabilirsiniz.
      </Text>

      <View style={styles.suggestionsGrid}>
        {suggestions.map((item) => (
          <TouchableOpacity
            key={item.title}
            accessibilityRole="button"
            activeOpacity={0.86}
            disabled={loading}
            style={[styles.suggestionCard, loading && styles.disabled]}
            onPress={() => onSelect(item.prompt)}
          >
            <View style={[styles.suggestionIconContainer, { backgroundColor: `${item.tone}22` }]}>
              <Ionicons name={item.icon} size={22} color={item.tone} />
            </View>
            <Text style={styles.suggestionCardTitle}>{item.title}</Text>
          </TouchableOpacity>
        ))}
      </View>
    </View>
  );
}

function BouncingDots() {
  const dot1 = useRef(new Animated.Value(0)).current;
  const dot2 = useRef(new Animated.Value(0)).current;
  const dot3 = useRef(new Animated.Value(0)).current;

  useEffect(() => {
    const createBounce = (anim: Animated.Value, delay: number) => {
      return Animated.loop(
        Animated.sequence([
          Animated.delay(delay),
          Animated.timing(anim, {
            toValue: -6,
            duration: 400,
            useNativeDriver: Platform.OS !== "web",
          }),
          Animated.timing(anim, {
            toValue: 0,
            duration: 400,
            useNativeDriver: Platform.OS !== "web",
          }),
          Animated.delay(400),
        ])
      );
    };

    const a1 = createBounce(dot1, 0);
    const a2 = createBounce(dot2, 180);
    const a3 = createBounce(dot3, 360);

    a1.start();
    a2.start();
    a3.start();

    return () => {
      a1.stop();
      a2.stop();
      a3.stop();
    };
  }, []);

  return (
    <View style={{ flexDirection: "row", gap: 5, alignItems: "center", height: 16, width: 36, paddingLeft: spacing.xs }}>
      <Animated.View style={[styles.bounceDot, { transform: [{ translateY: dot1 }] }]} />
      <Animated.View style={[styles.bounceDot, { transform: [{ translateY: dot2 }] }]} />
      <Animated.View style={[styles.bounceDot, { transform: [{ translateY: dot3 }] }]} />
    </View>
  );
}

function CodeBlock({ code, lang }: { code: string; lang: string }) {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    Clipboard.setString(code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <View style={styles.codeBlockContainer}>
      <View style={styles.codeBlockHeader}>
        <Text style={styles.codeBlockLang}>{lang.toUpperCase()}</Text>
        <TouchableOpacity style={styles.codeBlockCopyBtn} onPress={handleCopy} activeOpacity={0.8}>
          <Ionicons
            name={copied ? "checkmark-done" : "copy-outline"}
            size={13}
            color={copied ? colors.success : colors.primary}
          />
          <Text style={[styles.codeBlockCopyText, copied && { color: colors.success }]}>
            {copied ? "Kopyalandı" : "Kopyala"}
          </Text>
        </TouchableOpacity>
      </View>
      <ScrollView horizontal showsHorizontalScrollIndicator={true} contentContainerStyle={{ padding: spacing.md }}>
        <Text style={styles.codeBlockText}>{code}</Text>
      </ScrollView>
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
  
  // We will divide the text into chunks: plain markdown text chunks and code block chunks.
  const regex = /```([\s\S]*?)```/g;
  const parts = [];
  let lastIndex = 0;
  let match;

  while ((match = regex.exec(text)) !== null) {
    const matchIndex = match.index;
    
    // Add text chunk before the code block
    if (matchIndex > lastIndex) {
      parts.push({
        type: "text",
        content: text.substring(lastIndex, matchIndex),
      });
    }

    // Add code block chunk
    parts.push({
      type: "code",
      content: match[1],
    });

    lastIndex = regex.lastIndex;
  }

  // Add remaining text
  if (lastIndex < text.length) {
    parts.push({
      type: "text",
      content: text.substring(lastIndex),
    });
  }

  return parts.map((part, pIdx) => {
    if (part.type === "code") {
      // Split off language code if present (e.g. "javascript\nconsole.log(1)")
      const codeLines = part.content.trim().split("\n");
      let lang = "code";
      let codeContent = part.content.trim();
      if (codeLines.length > 0 && /^[a-zA-Z0-9_-]+$/.test(codeLines[0].trim())) {
        lang = codeLines[0].trim();
        codeContent = codeLines.slice(1).join("\n");
      }

      return (
        <CodeBlock key={`code-block-${pIdx}`} code={codeContent} lang={lang} />
      );
    }

    // Otherwise, parse standard lines
    const lines = part.content.split("\n");
    return lines.map((line, index) => {
      const trimmedLine = line.trim();

      if (!trimmedLine) {
        return <View key={`empty-${pIdx}-${index}`} style={styles.emptyLine} />;
      }

      // Headings
      const headingMatch = line.match(/^(#{1,6})\s+(.*)$/);
      if (headingMatch) {
        const level = headingMatch[1].length;
        let headerText = headingMatch[2].replace(/\*\*/g, "");
        return (
          <Text
            key={`heading-${pIdx}-${index}`}
            style={[
              styles.assistantText,
              styles.heading,
              level === 1 ? styles.h1 : level === 2 ? styles.h2 : styles.h3,
            ]}
          >
            {headerText}
          </Text>
        );
      }

      // Bullet items
      const bulletMatch = line.match(/^[\*\-]\s+(.*)$/);
      if (bulletMatch) {
        return (
          <View key={`bullet-${pIdx}-${index}`} style={styles.bulletRow}>
            <Text style={[styles.assistantText, styles.bulletDot]}>•</Text>
            <Text style={[styles.assistantText, styles.bulletText]}>
              {renderInlineStyles(bulletMatch[1])}
            </Text>
          </View>
        );
      }

      // Numbered items
      const numberedMatch = line.match(/^(\d+)\.\s+(.*)$/);
      if (numberedMatch) {
        return (
          <View key={`number-${pIdx}-${index}`} style={styles.bulletRow}>
            <Text style={[styles.assistantText, styles.bulletDot]}>{numberedMatch[1]}.</Text>
            <Text style={[styles.assistantText, styles.bulletText]}>
              {renderInlineStyles(numberedMatch[2])}
            </Text>
          </View>
        );
      }

      // Standard paragraph
      return (
        <Text key={`para-${pIdx}-${index}`} style={[styles.assistantText, styles.paragraph]}>
          {renderInlineStyles(line)}
        </Text>
      );
    });
  });
};

export function ChatScreen() {
  const route = useRoute();
  const params = (route.params || {}) as RouteParams;
  const navigation = useNavigation<any>();

  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: "welcome",
      role: "assistant",
      content: "Aliağa'da aradığın bilgiye hızlıca ulaşalım. Bulamadığın şeyi bana sorabilirsin.",
      timestamp: new Date(),
    },
  ]);
  const messagesRef = useRef<ChatMessage[]>(messages);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [isFocused, setIsFocused] = useState(false);
  const [showScrollBottom, setShowScrollBottom] = useState(false);
  const handledPresetRef = useRef<string | null>(null);
  const listRef = useRef<FlatList>(null);
  const typewriterTimerRef = useRef<any>(null);

  const hasConversation = useMemo(
    () => messages.some((m) => m.id !== "welcome"),
    [messages]
  );

  useEffect(() => {
    messagesRef.current = messages;
  }, [messages]);

  useEffect(() => {
    return () => {
      if (typewriterTimerRef.current) {
        clearInterval(typewriterTimerRef.current);
      }
    };
  }, []);

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

        const messageId = `${Date.now()}-a`;
        addMessage({
          id: messageId,
          role: "assistant",
          content: "", // typewrite starting from empty
          timestamp: new Date(),
          results: ((response as any).sources || (response as any).results || []) as any,
        });

        // Typewriter streaming effect
        if (typewriterTimerRef.current) {
          clearInterval(typewriterTimerRef.current);
        }

        let currentIndex = 0;
        const speed = 10;
        const charsPerTick = 6;
        
        typewriterTimerRef.current = setInterval(() => {
          currentIndex += charsPerTick;
          if (currentIndex >= answer.length) {
            if (typewriterTimerRef.current) {
              clearInterval(typewriterTimerRef.current);
              typewriterTimerRef.current = null;
            }
            setMessages((prev) =>
              prev.map((msg) =>
                msg.id === messageId ? { ...msg, content: answer } : msg
              )
            );
          } else {
            const partial = answer.substring(0, currentIndex);
            setMessages((prev) =>
              prev.map((msg) =>
                msg.id === messageId ? { ...msg, content: partial } : msg
              )
            );
          }
        }, speed);

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
    const presetKey = params.presetPromptId || params.presetPrompt || null;
    if (!params.presetPrompt || handledPresetRef.current === presetKey) return;
    handledPresetRef.current = presetKey;
    sendQuery(params.presetPrompt);
  }, [params.presetPrompt, params.presetPromptId, sendQuery]);

  const onSend = useCallback(() => {
    sendQuery(input);
  }, [input, sendQuery]);

  const visibleMessages = useMemo(
    () => (hasConversation ? messages.filter((m) => m.id !== "welcome") : messages),
    [hasConversation, messages]
  );

  const dynamicSuggestions = useMemo(() => {
    const now = new Date();
    const hours = now.getHours();
    const day = now.getDay();
    const suggestions = [...PROMPT_SUGGESTIONS];
    
    if (day === 5 || day === 6 || day === 0) {
      suggestions[2] = {
        icon: "map-outline",
        title: "Hafta Sonu Keşifleri",
        prompt: "Aliağa'da hafta sonu gezebileceğim en güzel doğa, sahil ve tarihi yerleri listeler misin?",
        tone: colors.primary,
      };
    } else {
      suggestions[2] = {
        icon: "business-outline",
        title: "Hizmetler & Duyurular",
        prompt: "Aliağa Belediyesi'nin güncel ilanlarını, duyurularını ve kariyer fırsatlarını listele.",
        tone: colors.primary,
      };
    }
    
    // Highlight pharmacy during night hours
    if (hours >= 19 || hours < 8) {
      suggestions[0] = {
        icon: "medical-outline",
        title: "Nöbetçi Eczaneler",
        prompt: "Aliağa'daki aktif nöbetçi eczaneleri adres ve telefon bilgileriyle listele.",
        tone: colors.warning,
      };
    }
    
    return suggestions;
  }, []);

  const handleScroll = useCallback((event: any) => {
    const yOffset = event.nativeEvent.contentOffset.y;
    if (yOffset > 300) {
      setShowScrollBottom(true);
    } else {
      setShowScrollBottom(false);
    }
  }, []);

  const handleSourcePress = useCallback((result: SearchResult) => {
    if (result.type === "news" || result.published_at) {
      navigation.navigate("NewsDetail", { news: result });
      return;
    }
    if (result.latitude && result.longitude) {
      navigation.navigate("PlaceDetail", {
        id: result.id || String(Date.now()),
        name: result.name || result.title || "Mekan",
        category: result.category || "Keşif",
        address: result.address || "Aliağa",
        description: result.content || result.description || "Aliağa Keşif Noktası",
        phone: result.phone || null,
        rating: typeof result.rating === "number" ? result.rating : null,
        latitude: result.latitude,
        longitude: result.longitude,
        tags: result.tags || [],
        image_url: result.image_url || undefined,
      });
    }
  }, [navigation]);

  useEffect(() => {
    if (hasConversation || loading) return;
    requestAnimationFrame(() => {
      listRef.current?.scrollToOffset({ offset: 0, animated: false });
    });
  }, [hasConversation, loading]);

  const renderItem = useCallback(({ item }: { item: ChatMessage }) => {
    if (item.id === "welcome") {
      return <WelcomePanel loading={loading} onSelect={sendQuery} suggestions={dynamicSuggestions} />;
    }

    if (item.role === "user") {
      return (
        <View style={styles.userRow}>
          <LinearGradient
            colors={["rgba(48,40,27,0.98)", "rgba(28,24,19,0.98)"]}
            style={styles.userBubble}
          >
            <Text style={styles.userText}>{item.content}</Text>
          </LinearGradient>
        </View>
      );
    }

    const results = (item.results || [])
      .filter((r) => {
        const type = String(r.type || "").toLowerCase();
        const cat = String(r.category || "").toLowerCase();
        const title = String(r.title || r.name || "").toLowerCase();
        return (
          type !== "city_info" &&
          type !== "city_knowledge" &&
          type !== "document_chunk" &&
          cat !== "city_info" &&
          cat !== "city_knowledge" &&
          cat !== "document_chunk" &&
          !title.includes("city_info") &&
          !title.includes("city_knowledge") &&
          !title.includes("bilgi kaynağı") &&
          !title.includes("document_chunk")
        );
      })
      .slice(0, 3);

    return (
      <View style={styles.assistantWrap}>
        <View style={styles.assistantCard}>
          <View style={styles.assistantBadge}>
            <View style={styles.assistantBadgeIcon}>
              <Ionicons name="hardware-chip" size={14} color={colors.primary} />
            </View>
            <Text style={styles.assistantBadgeText}>ALİAĞAİ</Text>
          </View>
          <View style={styles.markdownContainer}>
            {parseMarkdown(item.content)}
          </View>

          {results.length > 0 ? (
            <View style={styles.resultStrip}>
              {results.map((result, index) => (
                <TouchableOpacity
                  key={`${result.type}-${index}`}
                  style={styles.resultChip}
                  activeOpacity={0.8}
                  onPress={() => handleSourcePress(result)}
                >
                  <View style={styles.resultChipLeft}>
                    <Ionicons
                      name={
                        result.phone
                          ? "call-outline"
                          : result.latitude
                          ? "location-outline"
                          : result.published_at
                          ? "newspaper-outline"
                          : "bookmark-outline"
                      }
                      size={14}
                      color={colors.primary}
                      style={styles.resultChipIcon}
                    />
                    <View style={styles.resultChipTextWrap}>
                      <Text style={styles.resultChipTitle} numberOfLines={1}>
                        {resultTitle(result)}
                      </Text>
                      <Text style={styles.resultChipMeta} numberOfLines={1}>
                        {resultMeta(result)}
                      </Text>
                    </View>
                  </View>
                  
                  <View style={styles.resultChipActions}>
                    {result.phone && (
                      <TouchableOpacity
                        style={styles.resultActionBtn}
                        onPress={(e) => {
                          e.stopPropagation();
                          void openPhone(result.phone);
                        }}
                      >
                        <Ionicons name="call-outline" size={12} color={colors.primary} />
                      </TouchableOpacity>
                    )}
                    {result.latitude && result.longitude && (
                      <TouchableOpacity
                        style={styles.resultActionBtn}
                        onPress={(e) => {
                          e.stopPropagation();
                          const query = `${result.name || result.title || "Aliağa"} ${result.address || "Aliağa"}`;
                          void openDirections(query, result.maps_link);
                        }}
                      >
                        <Ionicons name="navigate-outline" size={12} color={colors.primary} />
                      </TouchableOpacity>
                    )}
                  </View>
                </TouchableOpacity>
              ))}
            </View>
          ) : null}

          <View style={styles.assistantActionBar}>
            <TouchableOpacity
              style={styles.actionButton}
              activeOpacity={0.7}
              onPress={() => {
                Clipboard.setString(item.content);
              }}
            >
              <Ionicons name="copy-outline" size={13} color={colors.textSecondary} />
              <Text style={styles.actionButtonText}>Kopyala</Text>
            </TouchableOpacity>
            <TouchableOpacity
              style={styles.actionButton}
              activeOpacity={0.7}
              onPress={async () => {
                try {
                  await Share.share({
                    message: item.content,
                  });
                } catch (err) {
                  console.error("share_err", err);
                }
              }}
            >
              <Ionicons name="share-social-outline" size={13} color={colors.textSecondary} />
              <Text style={styles.actionButtonText}>Paylaş</Text>
            </TouchableOpacity>
          </View>
        </View>
      </View>
    );
  }, [loading, sendQuery, dynamicSuggestions, handleSourcePress]);

  return (
    <View style={styles.container}>
      <SafeAreaView style={styles.safeArea} edges={["top"]}>
        <AppHeader />

        <View style={styles.listWrap}>
          <FlatList
            ref={listRef}
            data={visibleMessages}
            keyExtractor={(item) => item.id}
            renderItem={renderItem}
            showsVerticalScrollIndicator={false}
            contentContainerStyle={styles.listContent}
            onScroll={handleScroll}
            scrollEventThrottle={16}
            onContentSizeChange={() => {
              if (hasConversation || loading) {
                listRef.current?.scrollToEnd({ animated: true });
              }
            }}
            ListFooterComponent={
              <>
                {loading ? (
                  <View style={styles.typingCard}>
                    <BouncingDots />
                    <Text style={styles.typingText}>Yanıt hazırlanıyor</Text>
                  </View>
                ) : null}
              </>
            }
          />
        </View>

        {showScrollBottom && (
          <TouchableOpacity
            style={styles.scrollBottomFab}
            activeOpacity={0.85}
            onPress={() => listRef.current?.scrollToEnd({ animated: true })}
          >
            <Ionicons name="arrow-down-outline" size={20} color={colors.primary} />
          </TouchableOpacity>
        )}

        <KeyboardAvoidingView
          behavior={Platform.OS === "ios" ? "padding" : undefined}
          keyboardVerticalOffset={Platform.OS === "ios" ? 0 : 20}
          style={styles.inputContainer}
        >
          <View style={[
            styles.composer,
            isFocused && styles.composerFocused,
            input.trim().length > 0 && styles.composerHasText
          ]}>
            <View style={styles.inputIcon}>
              <Ionicons name="sparkles-outline" size={17} color={colors.primary} />
            </View>
            <TextInput
              value={input}
              onChangeText={setInput}
              placeholder="Aliağa hakkında sor..."
              placeholderTextColor={colors.textTertiary}
              style={styles.input}
              onSubmitEditing={onSend}
              returnKeyType="send"
              editable={!loading}
              onFocus={() => setIsFocused(true)}
              onBlur={() => setIsFocused(false)}
            />
            <TouchableOpacity
              accessibilityRole="button"
              style={[
                styles.sendBtn,
                input.trim().length > 0 ? styles.sendBtnActive : styles.sendBtnDisabled
              ]}
              onPress={onSend}
              disabled={!input.trim() || loading}
            >
              <Ionicons
                name="arrow-up"
                size={22}
                color={input.trim().length > 0 ? colors.background : colors.textTertiary}
              />
            </TouchableOpacity>
          </View>
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
    paddingHorizontal: spacing.lg,
    paddingTop: 80,
    paddingBottom: spacing.xl,
  },
  welcomeContainer: {
    alignItems: "center",
    paddingVertical: spacing.lg,
    paddingHorizontal: spacing.sm,
  },
  aiOrbContainer: {
    width: 150,
    height: 150,
    justifyContent: "center",
    alignItems: "center",
    marginBottom: spacing.md,
  },
  aiOrbBackGlow: {
    position: "absolute",
    width: 48,
    height: 48,
    borderRadius: 24,
    backgroundColor: "rgba(200, 169, 110, 0.16)",
  },
  aiOrbUltraOuterRing: {
    position: "absolute",
    width: 140,
    height: 140,
    borderRadius: 70,
    borderWidth: 0.5,
    borderColor: "rgba(200, 169, 110, 0.05)",
  },
  aiOrbOuterRing: {
    position: "absolute",
    width: 112,
    height: 112,
    borderRadius: 56,
    borderWidth: 1,
    borderColor: "rgba(200, 169, 110, 0.12)",
    borderStyle: "dashed",
  },
  aiOrbMiddleRing: {
    position: "absolute",
    width: 86,
    height: 86,
    borderRadius: 43,
    borderWidth: 1.5,
    borderColor: "rgba(200, 169, 110, 0.28)",
  },
  aiOrb: {
    width: 62,
    height: 62,
    borderRadius: 31,
    backgroundColor: "rgba(22, 22, 26, 0.85)",
    borderWidth: 1.5,
    borderColor: colors.primary,
    justifyContent: "center",
    alignItems: "center",
    shadowColor: colors.primary,
    shadowOffset: { width: 0, height: 0 },
    shadowOpacity: 0.4,
    shadowRadius: 12,
    elevation: 8,
  },
  aiKicker: {
    ...typography.caption,
    color: colors.primary,
    fontWeight: "700",
    letterSpacing: 2,
    marginBottom: spacing.xs,
    fontSize: 11,
  },
  aiTitle: {
    ...typography.h2,
    color: colors.text,
    fontWeight: "800",
    textAlign: "center",
    marginBottom: spacing.sm,
  },
  aiDescription: {
    ...typography.bodySmall,
    color: colors.textSecondary,
    textAlign: "center",
    lineHeight: 20,
    paddingHorizontal: spacing.lg,
    marginBottom: spacing.xl,
  },
  suggestionsGrid: {
    width: "100%",
    flexDirection: "row",
    flexWrap: "wrap",
    justifyContent: "space-between",
    gap: spacing.md,
  },
  suggestionCard: {
    width: "47.5%",
    backgroundColor: "rgba(25, 22, 18, 0.60)", // Warm gold-black tint
    borderWidth: 1,
    borderColor: "rgba(200, 169, 110, 0.22)", // Clear gold border
    borderRadius: 14,
    padding: spacing.md,
    alignItems: "flex-start",
    justifyContent: "space-between",
    minHeight: 110,
  },
  suggestionIconContainer: {
    width: 36,
    height: 36,
    borderRadius: 18,
    justifyContent: "center",
    alignItems: "center",
    marginBottom: spacing.xs,
  },
  suggestionCardTitle: {
    ...typography.bodySmall,
    fontFamily: "PlusJakartaSans_700Bold",
    color: colors.text,
    textAlign: "left",
    fontSize: 13,
    lineHeight: 18,
  },
  assistantWrap: {
    marginBottom: spacing.md,
  },
  assistantCard: {
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.md,
    backgroundColor: "rgba(20, 20, 24, 0.95)",
    borderWidth: 1,
    borderColor: "rgba(200, 169, 110, 0.15)",
    borderRadius: borderRadius.lg,
  },
  assistantBadge: {
    flexDirection: "row",
    alignItems: "center",
    gap: spacing.xs,
    marginBottom: spacing.md,
  },
  assistantBadgeIcon: {
    width: 26,
    height: 26,
    borderRadius: 13,
    backgroundColor: colors.primaryLight,
    alignItems: "center",
    justifyContent: "center",
  },
  assistantBadgeText: {
    ...typography.captionSmall,
    color: colors.primary,
    letterSpacing: 1.5,
  },
  assistantText: {
    fontSize: 16,
    lineHeight: 26,
    color: colors.text,
    fontWeight: "400",
  },
  userRow: {
    alignItems: "flex-end",
    marginBottom: spacing.md,
  },
  userBubble: {
    maxWidth: "82%",
    borderWidth: 1,
    borderColor: "rgba(200,169,110,0.20)",
    borderRadius: borderRadius.xl,
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.md,
  },
  userText: {
    fontSize: 16,
    lineHeight: 26,
    color: colors.text,
    fontWeight: "400",
  },
  resultStrip: {
    gap: spacing.sm,
    marginTop: spacing.md,
  },
  resultChip: {
    minHeight: 52,
    borderRadius: borderRadius.md,
    borderWidth: 1,
    borderColor: "rgba(200, 169, 110, 0.15)",
    backgroundColor: "rgba(22, 22, 26, 0.65)",
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    gap: spacing.sm,
  },
  resultChipLeft: {
    flexDirection: "row",
    alignItems: "center",
    gap: spacing.sm,
    flex: 1,
  },
  resultChipIcon: {
    width: 18,
  },
  resultChipTextWrap: {
    flex: 1,
  },
  resultChipActions: {
    flexDirection: "row",
    alignItems: "center",
    gap: spacing.sm,
  },
  resultActionBtn: {
    width: 30,
    height: 30,
    borderRadius: 15,
    backgroundColor: "rgba(200, 169, 110, 0.10)",
    borderWidth: 1,
    borderColor: "rgba(200, 169, 110, 0.20)",
    alignItems: "center",
    justifyContent: "center",
  },
  resultChipTitle: {
    ...typography.bodySmall,
    color: colors.text,
    fontWeight: "800",
  },
  resultChipMeta: {
    ...typography.captionSmall,
    color: colors.textSecondary,
    marginTop: 2,
    textTransform: "none",
  },
  scrollBottomFab: {
    position: "absolute",
    right: spacing.lg,
    bottom: 156,
    width: 44,
    height: 44,
    borderRadius: 22,
    backgroundColor: "rgba(20, 20, 24, 0.95)",
    borderWidth: 1.2,
    borderColor: "rgba(200, 169, 110, 0.35)",
    alignItems: "center",
    justifyContent: "center",
    shadowColor: colors.primary,
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 5,
  },
  assistantActionBar: {
    flexDirection: "row",
    alignItems: "center",
    gap: spacing.md,
    marginTop: spacing.sm,
    borderTopWidth: 0.5,
    borderTopColor: "rgba(255, 255, 255, 0.08)",
    paddingTop: spacing.sm,
  },
  actionButton: {
    flexDirection: "row",
    alignItems: "center",
    gap: 4,
  },
  actionButtonText: {
    ...typography.captionSmall,
    color: colors.textSecondary,
    textTransform: "none",
  },
  typingCard: {
    alignSelf: "flex-start",
    flexDirection: "row",
    alignItems: "center",
    gap: spacing.md,
    marginTop: spacing.md,
    marginBottom: spacing.xl,
    paddingLeft: spacing.md,
  },
  typingText: {
    ...typography.captionSmall,
    color: colors.textSecondary,
    textTransform: "none",
  },
  disabled: {
    opacity: 0.5,
  },
  inputContainer: {
    paddingHorizontal: spacing.lg,
    paddingBottom: 86,
    paddingTop: spacing.sm,
  },
  composer: {
    minHeight: 56,
    borderWidth: 1.2,
    borderColor: "rgba(200, 169, 110, 0.18)",
    borderRadius: borderRadius.full,
    backgroundColor: "rgba(20, 20, 24, 0.85)",
    paddingLeft: spacing.md,
    paddingRight: spacing.sm,
    flexDirection: "row",
    alignItems: "center",
    gap: spacing.sm,
  },
  composerFocused: {
    borderColor: colors.primary,
    backgroundColor: "rgba(25, 22, 18, 0.98)",
    shadowColor: colors.primary,
    shadowOffset: { width: 0, height: 0 },
    shadowOpacity: 0.35,
    shadowRadius: 12,
    elevation: 8,
  },
  composerHasText: {
    borderColor: "rgba(200, 169, 110, 0.35)",
  },
  inputIcon: {
    width: 32,
    height: 32,
    borderRadius: 16,
    alignItems: "center",
    justifyContent: "center",
    backgroundColor: colors.primaryLight,
  },
  input: {
    flex: 1,
    ...typography.body,
    color: colors.text,
    minHeight: 44,
    paddingVertical: 8,
  },
  sendBtn: {
    width: 38,
    height: 38,
    borderRadius: 19,
    backgroundColor: "rgba(255, 255, 255, 0.05)",
    justifyContent: "center",
    alignItems: "center",
  },
  sendBtnActive: {
    backgroundColor: colors.primary,
    shadowColor: colors.primary,
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.35,
    shadowRadius: 6,
    elevation: 3,
  },
  sendBtnDisabled: {
    backgroundColor: "rgba(255, 255, 255, 0.02)",
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
    fontWeight: "700",
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
  markdownContainer: {
    width: "100%",
  },
  bounceDot: {
    width: 6,
    height: 6,
    borderRadius: 3,
    backgroundColor: colors.primary,
  },
  codeBlockContainer: {
    backgroundColor: "#000000",
    borderRadius: borderRadius.md,
    borderWidth: 1,
    borderColor: "rgba(200, 169, 110, 0.2)",
    marginVertical: spacing.md,
    overflow: "hidden",
  },
  codeBlockHeader: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    backgroundColor: "rgba(20, 20, 24, 0.95)",
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
    borderBottomWidth: 1,
    borderBottomColor: "rgba(255, 255, 255, 0.05)",
  },
  codeBlockLang: {
    ...typography.captionSmall,
    color: colors.textSecondary,
    fontWeight: "700",
  },
  codeBlockCopyBtn: {
    flexDirection: "row",
    alignItems: "center",
    gap: 4,
  },
  codeBlockCopyText: {
    ...typography.captionSmall,
    color: colors.primary,
    textTransform: "none",
  },
  codeBlockText: {
    fontFamily: Platform.OS === "ios" ? "Courier New" : "monospace",
    fontSize: 13,
    color: "#E2C08D", // Sleek gold/beige text
    lineHeight: 18,
  },
});
