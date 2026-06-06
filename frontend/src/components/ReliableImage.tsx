import React, { useMemo, useState } from "react";
import { Image, ImageResizeMode, ImageStyle, StyleProp, StyleSheet, Text, View } from "react-native";
import { Ionicons } from "@expo/vector-icons";

import { colors, typography } from "../theme";

type Props = {
  uri?: string | null;
  fallbackUri?: string | null;
  style: StyleProp<ImageStyle>;
  resizeMode?: ImageResizeMode;
  label?: string;
};

export function ReliableImage({ uri, fallbackUri, style, resizeMode = "cover", label = "Gorsel" }: Props) {
  const [failedUri, setFailedUri] = useState<string | null>(null);
  const selectedUri = useMemo(() => {
    if (uri && failedUri !== uri) return uri;
    if (fallbackUri && failedUri !== fallbackUri) return fallbackUri;
    return null;
  }, [failedUri, fallbackUri, uri]);

  if (!selectedUri) {
    return (
      <View style={[style, styles.fallback]}>
        <Ionicons name="image-outline" size={28} color={colors.textTertiary} />
        <Text style={styles.fallbackText}>{label}</Text>
      </View>
    );
  }

  return (
    <Image
      source={{ uri: selectedUri }}
      style={style}
      resizeMode={resizeMode}
      onError={() => setFailedUri(selectedUri)}
    />
  );
}

const styles = StyleSheet.create({
  fallback: {
    alignItems: "center",
    justifyContent: "center",
    backgroundColor: "rgba(26,26,30,0.96)",
  },
  fallbackText: {
    ...typography.captionSmall,
    color: colors.textTertiary,
    marginTop: 6,
  },
});

