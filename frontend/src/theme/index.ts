export const colors = {
  // Brand Colors - Cultural Heritage Identity
  primary: "#E16D54", // Terracotta
  primaryLight: "rgba(225, 109, 84, 0.15)",
  primaryDark: "#ad4a34",

  secondary: "#ffb4a4", // Warm Accent
  secondaryLight: "rgba(255, 180, 164, 0.15)",
  secondaryDark: "#c88576",
  
  tertiary: "#5fdac6", // Cool Aegean
  tertiaryLight: "rgba(95, 218, 198, 0.15)",

  // Neutral Colors - Premium Glass Dark Theme
  background: "#041329", // The Void (Deep Navy)
  surface: "rgba(17, 32, 54, 0.65)", // Dark glass surface
  surfaceHighlight: "rgba(255, 255, 255, 0.08)", // Bright edge for glass
  glass: "rgba(17, 32, 54, 0.4)",
  glassDark: "rgba(4, 19, 41, 0.6)",
  glassNav: "rgba(44, 57, 81, 0.85)", // Pill Nav Background

  text: "#F8FAFC",
  textSecondary: "#ddc0ba",
  textTertiary: "rgba(248, 250, 252, 0.5)",
  textInverse: "#041329",

  border: "rgba(255, 255, 255, 0.12)",
  borderLight: "rgba(255, 255, 255, 0.05)",

  // Semantic
  success: "#10B981",
  warning: "#F59E0B",
  error: "#EF4444",
  info: "#3B82F6",

  // Specialized Gradients
  gradients: {
    bg: ["#041329", "#061833", "#081d3d"], // Oceanic descent
    primary: ["#E16D54", "#e88b76"],
    surface: ["rgba(25, 45, 70, 0.7)", "rgba(10, 25, 45, 0.4)"],
    accent: ["#ffb4a4", "#E16D54"], // Vibrant terracotta gradient
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
  h1: { fontFamily: "System", fontSize: 34, fontWeight: "800" as const, lineHeight: 42, letterSpacing: -0.8 },
  h2: { fontFamily: "System", fontSize: 26, fontWeight: "700" as const, lineHeight: 32, letterSpacing: -0.5 },
  h3: { fontFamily: "System", fontSize: 20, fontWeight: "600" as const, lineHeight: 28, letterSpacing: -0.2 },
  body: { fontFamily: "System", fontSize: 16, fontWeight: "400" as const, lineHeight: 24, letterSpacing: 0.2 },
  bodyMedium: { fontFamily: "System", fontSize: 16, fontWeight: "500" as const, lineHeight: 24, letterSpacing: 0.2 },
  bodySmall: { fontFamily: "System", fontSize: 14, fontWeight: "400" as const, lineHeight: 20, letterSpacing: 0.1 },
  caption: { fontFamily: "System", fontSize: 12, fontWeight: "600" as const, lineHeight: 16, letterSpacing: 0.5, textTransform: "uppercase" as const },
  button: { fontFamily: "System", fontSize: 16, fontWeight: "700" as const, lineHeight: 24, letterSpacing: 0.3 },
} as const;

export const shadows = {
  soft: {
    shadowColor: "#000000",
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.2,
    shadowRadius: 10,
    elevation: 3,
  },
  medium: {
    shadowColor: "#000000",
    shadowOffset: { width: 0, height: 10 },
    shadowOpacity: 0.3,
    shadowRadius: 20,
    elevation: 6,
  },
  premium: {
    shadowColor: "#000000",
    shadowOffset: { width: 0, height: 15 },
    shadowOpacity: 0.4,
    shadowRadius: 30,
    elevation: 10,
  },
  glow: {
    shadowColor: "#E16D54",
    shadowOffset: { width: 0, height: 0 },
    shadowOpacity: 0.35,
    shadowRadius: 18,
    elevation: 8,
  }
} as const;
