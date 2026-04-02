export const colors = {
  // Brand Colors - More Vibrant & Tech-forward
  primary: "#2563EB", // Electric Blue
  primaryLight: "rgba(37, 99, 235, 0.1)",
  primaryDark: "#1E3A8A",

  secondary: "#F59E0B", // Amber/Gold for "Premium" accents
  secondaryLight: "rgba(245, 158, 11, 0.1)",

  // Neutral Colors - Clean & Professional
  background: "#F8FAFC",
  surface: "rgba(255, 255, 255, 0.85)",
  glass: "rgba(255, 255, 255, 0.7)",
  glassDark: "rgba(15, 23, 42, 0.05)",

  text: "#0F172A",
  textSecondary: "#475569",
  textTertiary: "#94A3B8",
  textInverse: "#FFFFFF",

  border: "rgba(226, 232, 240, 0.8)",
  borderLight: "rgba(255, 255, 255, 0.5)",

  // Semantic
  success: "#10B981",
  warning: "#F59E0B",
  error: "#EF4444",
  info: "#3B82F6",

  // Specialized
  gradients: {
    bg: ["#F0F9FF", "#E0F2FE", "#F8FAFC"],
    primary: ["#2563EB", "#1D4ED8"],
    surface: ["rgba(255, 255, 255, 0.9)", "rgba(255, 255, 255, 0.7)"],
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
  xl: 24, // Smoother corners for premium look
  xxl: 32,
  full: 999,
} as const;

export const typography = {
  h1: { fontSize: 32, fontWeight: "800" as const, lineHeight: 40, letterSpacing: -0.5 },
  h2: { fontSize: 24, fontWeight: "700" as const, lineHeight: 30, letterSpacing: -0.3 },
  h3: { fontSize: 20, fontWeight: "600" as const, lineHeight: 28 },
  body: { fontSize: 16, fontWeight: "400" as const, lineHeight: 24 },
  bodyMedium: { fontSize: 16, fontWeight: "500" as const, lineHeight: 24 },
  bodySmall: { fontSize: 14, fontWeight: "400" as const, lineHeight: 20 },
  caption: { fontSize: 12, fontWeight: "500" as const, lineHeight: 16 },
  button: { fontSize: 16, fontWeight: "600" as const, lineHeight: 24 },
} as const;

export const shadows = {
  soft: {
    shadowColor: "#2563EB",
    shadowOffset: { width: 0, height: 10 },
    shadowOpacity: 0.03,
    shadowRadius: 20,
    elevation: 2,
  },
  medium: {
    shadowColor: "#0F172A",
    shadowOffset: { width: 0, height: 15 },
    shadowOpacity: 0.06,
    shadowRadius: 30,
    elevation: 5,
  },
  premium: {
    shadowColor: "#2563EB",
    shadowOffset: { width: 0, height: 20 },
    shadowOpacity: 0.08,
    shadowRadius: 40,
    elevation: 10,
  },
} as const;
