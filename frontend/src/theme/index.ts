export const colors = {
  // Brand Colors — Black & Gold Identity (Stitch Design)
  primary: "#C8A96E",       // Altın / Bej vurgu
  primaryLight: "rgba(200, 169, 110, 0.15)",
  primaryDark: "#9B7E4A",

  secondary: "#D4B980",     // Warm Gold (açık altın)
  secondaryLight: "rgba(212, 185, 128, 0.15)",
  secondaryDark: "#A89058",

  tertiary: "#8B9A7E",      // Muted Olive (doğa tonu)
  tertiaryLight: "rgba(139, 154, 126, 0.15)",

  // Neutral Colors — Pure Dark Theme
  background: "#0A0A0A",    // Saf siyah zemin
  surface: "rgba(30, 30, 30, 0.80)",          // Koyu kart yüzeyi
  surfaceLight: "rgba(40, 40, 40, 0.70)",     // Hafif açık yüzey
  surfaceHighlight: "rgba(255, 255, 255, 0.06)",
  glass: "rgba(25, 25, 25, 0.50)",
  glassDark: "rgba(18, 18, 18, 0.85)",
  glassNav: "rgba(28, 28, 28, 0.92)",         // Pill Nav Background
  glassBorder: "rgba(255, 215, 0, 0.15)",     // Koyu cam kenarlığı

  text: "#FFFFFF",
  textSecondary: "rgba(255, 255, 255, 0.60)",
  textTertiary: "rgba(255, 255, 255, 0.35)",
  textInverse: "#0A0A0A",

  border: "rgba(255, 255, 255, 0.10)",
  borderLight: "rgba(255, 255, 255, 0.06)",

  // Semantic
  success: "#4CAF50",
  warning: "#F5A623",
  error: "#EF4444",
  info: "#5B9BD5",

  // İZBAN / Altyapı kartları için
  izbanBlue: "#4A90D9",
  altyapiGold: "#C8A96E",

  // User chat bubble
  userBubble: "rgba(40, 35, 25, 0.95)",

  // Specialized Gradients
  gradients: {
    bg: ["#0A0A0A", "#0D0D0D", "#111111"],
    primary: ["#C8A96E", "#D4B980"],
    surface: ["rgba(30, 30, 30, 0.8)", "rgba(20, 20, 20, 0.6)"],
    accent: ["#D4B980", "#C8A96E"],
  },
} as const;

export const spacing = {
  xs: 4,
  sm: 8,
  md: 12,
  lg: 16,
  xl: 20,
  xxl: 24,
  xxxl: 32,
  huge: 48,
} as const;

export const borderRadius = {
  sm: 8,
  md: 12,
  lg: 16,
  xl: 24,
  xxl: 32,
  full: 999,
} as const;

export const typography = {
  // Header logo font (ALİAĞAİ başlığı)
  logo: { fontFamily: "Outfit_700Bold", fontSize: 20, letterSpacing: 3 },
  h1: { fontFamily: "Outfit_800ExtraBold", fontSize: 28, lineHeight: 36, letterSpacing: -0.5 },
  h2: { fontFamily: "Outfit_700Bold", fontSize: 22, lineHeight: 28, letterSpacing: -0.3 },
  h3: { fontFamily: "Outfit_600SemiBold", fontSize: 18, lineHeight: 24, letterSpacing: -0.2 },
  body: { fontFamily: "PlusJakartaSans_400Regular", fontSize: 16, lineHeight: 24, letterSpacing: 0.2 },
  bodyMedium: { fontFamily: "PlusJakartaSans_500Medium", fontSize: 16, lineHeight: 24, letterSpacing: 0.2 },
  bodySmall: { fontFamily: "PlusJakartaSans_400Regular", fontSize: 14, lineHeight: 20, letterSpacing: 0.1 },
  caption: { fontFamily: "PlusJakartaSans_600SemiBold", fontSize: 12, lineHeight: 16, letterSpacing: 0.5, textTransform: "uppercase" as const },
  captionSmall: { fontFamily: "PlusJakartaSans_600SemiBold", fontSize: 10, lineHeight: 14, letterSpacing: 0.3 },
  button: { fontFamily: "PlusJakartaSans_700Bold", fontSize: 16, lineHeight: 24, letterSpacing: 0.3 },
  date: { fontFamily: "Outfit_700Bold", fontSize: 22, lineHeight: 28, letterSpacing: -0.3 },
  subtitle: { fontFamily: "Outfit_600SemiBold", fontSize: 14, lineHeight: 20, letterSpacing: -0.1 },
} as const;

export const shadows = {
  soft: {
    shadowColor: "#000000",
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 3,
  },
  medium: {
    shadowColor: "#000000",
    shadowOffset: { width: 0, height: 8 },
    shadowOpacity: 0.4,
    shadowRadius: 16,
    elevation: 6,
  },
  premium: {
    shadowColor: "#000000",
    shadowOffset: { width: 0, height: 12 },
    shadowOpacity: 0.5,
    shadowRadius: 24,
    elevation: 10,
  },
  glow: {
    shadowColor: "#C8A96E",
    shadowOffset: { width: 0, height: 0 },
    shadowOpacity: 0.25,
    shadowRadius: 12,
    elevation: 8,
  }
} as const;

// Google Maps karanlık tema — Black & Gold uyumlu
export const darkMapStyle = [
  { elementType: "geometry", stylers: [{ color: "#141414" }] },
  { elementType: "labels.text.fill", stylers: [{ color: "#C8A96E" }] },
  { elementType: "labels.text.stroke", stylers: [{ color: "#0A0A0A" }] },
  { elementType: "labels.icon", stylers: [{ saturation: -100 }, { lightness: -40 }] },
  { featureType: "administrative", elementType: "geometry.stroke", stylers: [{ color: "#C8A96E" }, { weight: 0.6 }] },
  { featureType: "administrative.land_parcel", elementType: "geometry.stroke", stylers: [{ color: "#C8A96E" }, { weight: 0.3 }] },
  { featureType: "poi", elementType: "geometry", stylers: [{ color: "#1a1a1a" }] },
  { featureType: "poi", elementType: "labels.text.fill", stylers: [{ color: "#8B9A7E" }] },
  { featureType: "road", elementType: "geometry", stylers: [{ color: "#1e1e1e" }] },
  { featureType: "road", elementType: "labels.text.fill", stylers: [{ color: "#C8A96E" }] },
  { featureType: "road.highway", elementType: "geometry.fill", stylers: [{ color: "#2a2a2a" }] },
  { featureType: "road.highway", elementType: "geometry.stroke", stylers: [{ color: "#C8A96E" }, { weight: 0.4 }] },
  { featureType: "road.arterial", elementType: "labels.text.fill", stylers: [{ color: "#D4B980" }] },
  { featureType: "water", elementType: "geometry", stylers: [{ color: "#0a1628" }] },
  { featureType: "water", elementType: "labels.text.fill", stylers: [{ color: "#5B9BD5" }] },
  { featureType: "transit", elementType: "geometry", stylers: [{ color: "#1a1a1a" }] },
  { featureType: "transit.station", elementType: "labels.text.fill", stylers: [{ color: "#C8A96E" }] },
];

// Kategoriye göre marker rengi
export const markerColors: Record<string, string> = {
  history: "#C8A96E",
  food: "#F5A623",
  coast: "#5B9BD5",
  park: "#4CAF50",
  culture: "#D4B980",
  default: "#C8A96E",
};

// Aliağa merkez koordinatı
export const ALIAGA_CENTER = {
  latitude: 38.7950,
  longitude: 26.9760,
  latitudeDelta: 0.12,
  longitudeDelta: 0.12,
};
