import React from "react";
import { createBottomTabNavigator } from "@react-navigation/bottom-tabs";
import { Ionicons } from "@expo/vector-icons";

import { HomeScreen } from "../screens/HomeScreen";
import { ExploreScreen } from "../screens/ExploreScreen";
import { PharmacyScreen } from "../screens/PharmacyScreen";
import { NewsScreen } from "../screens/NewsScreen";
import { colors, typography } from "../theme";

const Tab = createBottomTabNavigator();

const TAB_ICONS: Record<string, { focused: string; unfocused: string }> = {
  Home: { focused: "chatbubble-ellipses", unfocused: "chatbubble-ellipses-outline" },
  Explore: { focused: "compass", unfocused: "compass-outline" },
  Pharmacy: { focused: "medical", unfocused: "medical-outline" },
  News: { focused: "newspaper", unfocused: "newspaper-outline" },
};

export function AppNavigator() {
  return (
    <Tab.Navigator
      screenOptions={({ route }) => ({
        headerShown: false,
        tabBarIcon: ({ focused, color, size }) => {
          const icons = TAB_ICONS[route.name];
          const iconName = focused ? icons.focused : icons.unfocused;
          return (
            <Ionicons
              name={iconName as keyof typeof Ionicons.glyphMap}
              size={size}
              color={color}
            />
          );
        },
        tabBarActiveTintColor: colors.primary,
        tabBarInactiveTintColor: colors.textTertiary,
        tabBarLabelStyle: {
          fontSize: typography.caption.fontSize,
          fontWeight: "500" as const,
        },
        tabBarStyle: {
          backgroundColor: colors.surface,
          borderTopColor: colors.borderLight,
          borderTopWidth: 1,
          paddingBottom: 4,
          height: 56,
        },
      })}
    >
      <Tab.Screen
        name="Home"
        component={HomeScreen}
        options={{ tabBarLabel: "Asistan" }}
      />
      <Tab.Screen
        name="Explore"
        component={ExploreScreen}
        options={{ tabBarLabel: "Keşfet" }}
      />
      <Tab.Screen
        name="Pharmacy"
        component={PharmacyScreen}
        options={{ tabBarLabel: "Eczane" }}
      />
      <Tab.Screen
        name="News"
        component={NewsScreen}
        options={{ tabBarLabel: "Gündem" }}
      />
    </Tab.Navigator>
  );
}
