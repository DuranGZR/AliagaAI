import React from 'react';
import { View, TouchableOpacity, StyleSheet, Dimensions, Keyboard, ActivityIndicator } from 'react-native';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { NavigationContainer } from '@react-navigation/native';
import { Ionicons } from '@expo/vector-icons';
import { BlurView } from 'expo-blur';
import { colors, shadows, borderRadius, spacing } from '../theme';
import { useAuth } from '../context/AuthContext';

// Screens
import { HomeScreen } from '../screens/HomeScreen';
import { ChatScreen } from '../screens/ChatScreen';
import { ExploreScreen } from '../screens/ExploreScreen';
import { DirectoryScreen } from '../screens/DirectoryScreen';
import { MunicipalityScreen } from '../screens/MunicipalityScreen';
import { PlaceDetailScreen } from '../screens/PlaceDetailScreen';
import { SettingsProfileScreen } from '../screens/SettingsProfileScreen';
import { PlacesListScreen } from '../screens/PlacesListScreen';
import { PharmacyListScreen } from '../screens/PharmacyListScreen';
import { NewsDetailScreen } from '../screens/NewsDetailScreen';
import { EditProfileScreen } from '../screens/EditProfileScreen';
import { IzbanScheduleScreen } from '../screens/IzbanScheduleScreen';
import { MarketListScreen } from '../screens/MarketListScreen';
import { PrayerTimesScreen } from '../screens/PrayerTimesScreen';
import { OutageListScreen } from '../screens/OutageListScreen';
import { WeatherDetailScreen } from '../screens/WeatherDetailScreen';
import { MarketRatesScreen } from '../screens/MarketRatesScreen';
import { EarthquakeListScreen } from '../screens/EarthquakeListScreen';
import { GalleryListScreen } from '../screens/GalleryListScreen';
import { GalleryDetailScreen } from '../screens/GalleryDetailScreen';
import { OnboardingScreen } from '../screens/OnboardingScreen';
import { LoginScreen } from '../screens/LoginScreen';
import { RegisterScreen } from '../screens/RegisterScreen';

const Tab = createBottomTabNavigator();
const Stack = createNativeStackNavigator();

// Tab ikonları — tasarımdaki sıraya göre
const TAB_ICONS: Record<string, { active: string; inactive: string }> = {
  Home: { active: "calendar", inactive: "calendar-outline" },
  Directory: { active: "book", inactive: "book-outline" },
  Chat: { active: "hardware-chip", inactive: "hardware-chip-outline" },
  Explore: { active: "compass", inactive: "compass-outline" },
  Municipality: { active: "business", inactive: "business-outline" },
};

const TAB_LABELS: Record<string, string> = {
  Home: "Ana sayfa",
  Directory: "Rehber",
  Chat: "AliağaAI sohbet",
  Explore: "Keşfet",
  Municipality: "Belediye",
};

// Custom Floating Tab Bar
const FloatingTabBar = ({ state, descriptors, navigation }: any) => {
  const [visible, setVisible] = React.useState(true);

  React.useEffect(() => {
    const showSubscription = Keyboard.addListener('keyboardDidShow', () => setVisible(false));
    const hideSubscription = Keyboard.addListener('keyboardDidHide', () => setVisible(true));
    return () => {
      showSubscription.remove();
      hideSubscription.remove();
    };
  }, []);

  if (!visible) return null;

  const chatRoute = state.routes.find((route: any) => route.name === "Chat");
  const regularRoutes = state.routes.filter((route: any) => route.name !== "Chat");
  const leftRoutes = regularRoutes.slice(0, 2);
  const rightRoutes = regularRoutes.slice(2);

  const emitPress = (route: any, isFocused: boolean) => {
    const event = navigation.emit({
      type: 'tabPress',
      target: route.key,
      canPreventDefault: true,
    });

    if (!isFocused && !event.defaultPrevented) {
      navigation.navigate({ name: route.name, merge: true });
    }
  };

  const renderTabItem = (route: any) => {
    const routeIndex = state.routes.findIndex((item: any) => item.key === route.key);
    const { options } = descriptors[route.key];
    const isFocused = state.index === routeIndex;
    const icons = TAB_ICONS[route.name] || TAB_ICONS.Home;
    const iconName = isFocused ? icons.active : icons.inactive;

    return (
      <TouchableOpacity
        key={route.key}
        accessibilityRole="button"
        accessibilityState={isFocused ? { selected: true } : {}}
        accessibilityLabel={options.tabBarAccessibilityLabel || TAB_LABELS[route.name] || route.name}
        testID={options.tabBarTestID}
        onPress={() => emitPress(route, isFocused)}
        onLongPress={() => navigation.emit({ type: 'tabLongPress', target: route.key })}
        style={styles.tabItem}
      >
        <Ionicons
          name={iconName as any}
          size={24}
          color={isFocused ? colors.text : colors.textTertiary}
        />
        {isFocused && <View style={styles.activeIndicator} />}
      </TouchableOpacity>
    );
  };

  const renderChatButton = () => {
    if (!chatRoute) return null;
    const routeIndex = state.routes.findIndex((item: any) => item.key === chatRoute.key);
    const isFocused = state.index === routeIndex;

    return (
      <TouchableOpacity
        accessibilityRole="button"
        accessibilityState={isFocused ? { selected: true } : {}}
        accessibilityLabel={TAB_LABELS.Chat}
        onPress={() => emitPress(chatRoute, isFocused)}
        style={[styles.centerTabButton, isFocused && styles.centerTabButtonActive]}
        activeOpacity={0.88}
      >
        <Ionicons
          name={(isFocused ? TAB_ICONS.Chat.active : TAB_ICONS.Chat.inactive) as any}
          size={31}
          color={isFocused ? colors.background : colors.primary}
        />
        <View style={[styles.centerTabDot, isFocused && styles.centerTabDotActive]} />
      </TouchableOpacity>
    );
  };

  return (
    <View style={styles.tabBarContainer}>
      <BlurView intensity={50} tint="dark" style={styles.tabBarInner}>
        {state.routes.map((route: any, index: number) => {
          const { options } = descriptors[route.key];
          const isFocused = state.index === index;

          const onPress = () => {
            const event = navigation.emit({
              type: 'tabPress',
              target: route.key,
              canPreventDefault: true,
            });

            if (!isFocused && !event.defaultPrevented) {
              navigation.navigate({ name: route.name, merge: true });
            }
          };

          const onLongPress = () => {
            navigation.emit({
              type: 'tabLongPress',
              target: route.key,
            });
          };

          const icons = TAB_ICONS[route.name] || TAB_ICONS.Home;
          const iconName = isFocused ? icons.active : icons.inactive;

          return (
            <TouchableOpacity
              key={index}
              accessibilityRole="button"
              accessibilityState={isFocused ? { selected: true } : {}}
              accessibilityLabel={options.tabBarAccessibilityLabel || TAB_LABELS[route.name] || route.name}
              testID={options.tabBarTestID}
              onPress={onPress}
              onLongPress={onLongPress}
              style={styles.tabItem}
            >
              <Ionicons
                name={iconName as any}
                size={24}
                color={isFocused ? colors.text : colors.textTertiary}
              />
              {/* Aktif tab altında nokta gösterge */}
              {isFocused && <View style={styles.activeIndicator} />}
            </TouchableOpacity>
          );
        })}
      </BlurView>
    </View>
  );
};

const FloatingTabBarV2 = ({ state, descriptors, navigation }: any) => {
  const [visible, setVisible] = React.useState(true);

  React.useEffect(() => {
    const showSubscription = Keyboard.addListener('keyboardDidShow', () => setVisible(false));
    const hideSubscription = Keyboard.addListener('keyboardDidHide', () => setVisible(true));
    return () => {
      showSubscription.remove();
      hideSubscription.remove();
    };
  }, []);

  if (!visible) return null;

  const chatRoute = state.routes.find((route: any) => route.name === "Chat");
  const regularRoutes = state.routes.filter((route: any) => route.name !== "Chat");
  const leftRoutes = regularRoutes.slice(0, 2);
  const rightRoutes = regularRoutes.slice(2);

  const emitPress = (route: any, isFocused: boolean) => {
    const event = navigation.emit({
      type: 'tabPress',
      target: route.key,
      canPreventDefault: true,
    });

    if (!isFocused && !event.defaultPrevented) {
      navigation.navigate({ name: route.name, merge: true });
    }
  };

  const renderTabItem = (route: any) => {
    const routeIndex = state.routes.findIndex((item: any) => item.key === route.key);
    const { options } = descriptors[route.key];
    const isFocused = state.index === routeIndex;
    const icons = TAB_ICONS[route.name] || TAB_ICONS.Home;
    const iconName = isFocused ? icons.active : icons.inactive;

    return (
      <TouchableOpacity
        key={route.key}
        accessibilityRole="button"
        accessibilityState={isFocused ? { selected: true } : {}}
        accessibilityLabel={options.tabBarAccessibilityLabel || TAB_LABELS[route.name] || route.name}
        testID={options.tabBarTestID}
        onPress={() => emitPress(route, isFocused)}
        onLongPress={() => navigation.emit({ type: 'tabLongPress', target: route.key })}
        style={styles.tabItem}
      >
        <Ionicons
          name={iconName as any}
          size={24}
          color={isFocused ? colors.text : colors.textTertiary}
        />
        {isFocused && <View style={styles.activeIndicator} />}
      </TouchableOpacity>
    );
  };

  const renderChatButton = () => {
    if (!chatRoute) return null;
    const routeIndex = state.routes.findIndex((item: any) => item.key === chatRoute.key);
    const isFocused = state.index === routeIndex;

    return (
      <TouchableOpacity
        accessibilityRole="button"
        accessibilityState={isFocused ? { selected: true } : {}}
        accessibilityLabel={TAB_LABELS.Chat}
        onPress={() => emitPress(chatRoute, isFocused)}
        style={[styles.centerTabButton, isFocused && styles.centerTabButtonActive]}
        activeOpacity={0.88}
      >
        <Ionicons
          name={(isFocused ? TAB_ICONS.Chat.active : TAB_ICONS.Chat.inactive) as any}
          size={20}
          color={isFocused ? colors.primary : "rgba(200, 169, 110, 0.65)"}
        />
        <View style={[styles.centerTabDot, isFocused && styles.centerTabDotActive]} />
      </TouchableOpacity>
    );
  };

  return (
    <View style={styles.tabBarContainer}>
      <BlurView intensity={50} tint="dark" style={styles.tabBarInner}>
        {leftRoutes.map(renderTabItem)}
        <View style={styles.centerSpacer} />
        {rightRoutes.map(renderTabItem)}
        {rightRoutes.length < 2 ? <View style={styles.tabItemPlaceholder} /> : null}
      </BlurView>
      {renderChatButton()}
    </View>
  );
};

const MainTabs = () => {
  return (
    <Tab.Navigator
      tabBar={props => <FloatingTabBarV2 {...props} />}
      screenOptions={{
        headerShown: false,
        tabBarShowLabel: false,
      }}
    >
      <Tab.Screen name="Home" component={HomeScreen} options={{ tabBarAccessibilityLabel: TAB_LABELS.Home }} />
      <Tab.Screen name="Directory" component={DirectoryScreen} options={{ tabBarAccessibilityLabel: TAB_LABELS.Directory }} />
      <Tab.Screen name="Chat" component={ChatScreen} options={{ tabBarAccessibilityLabel: TAB_LABELS.Chat }} />
      <Tab.Screen name="Explore" component={ExploreScreen} options={{ tabBarAccessibilityLabel: TAB_LABELS.Explore }} />
      <Tab.Screen name="Municipality" component={MunicipalityScreen} options={{ tabBarAccessibilityLabel: TAB_LABELS.Municipality }} />
    </Tab.Navigator>
  );
};

export const AppNavigator = () => {
  const { isLoading, isOnboarded, token } = useAuth();

  if (isLoading) {
    return (
      <View style={styles.loadingContainer}>
        <Ionicons name="hardware-chip" size={48} color={colors.primary} />
        <ActivityIndicator size="large" color={colors.primary} style={{ marginTop: spacing.lg }} />
      </View>
    );
  }

  return (
    <NavigationContainer>
      <Stack.Navigator screenOptions={{ headerShown: false, contentStyle: { backgroundColor: colors.background }}}>
        {!isOnboarded ? (
          // Onboarding Akışı
          <Stack.Screen name="Onboarding" component={OnboardingScreen} />
        ) : !token ? (
          // Kimlik Doğrulama Akışı
          <>
            <Stack.Screen name="Login" component={LoginScreen} />
            <Stack.Screen name="Register" component={RegisterScreen} />
          </>
        ) : (
          // Ana Uygulama Akışı
          <>
            <Stack.Screen name="MainTabs" component={MainTabs} />
            <Stack.Screen
              name="PlaceDetail"
              component={PlaceDetailScreen}
              options={{ presentation: 'modal' }}
            />
            <Stack.Screen
              name="SettingsProfile"
              component={SettingsProfileScreen}
              options={{ presentation: 'modal' }}
            />
            <Stack.Screen
              name="PlacesList"
              component={PlacesListScreen}
            />
            <Stack.Screen
              name="PharmacyList"
              component={PharmacyListScreen}
            />
            <Stack.Screen
              name="IzbanSchedule"
              component={IzbanScheduleScreen}
            />
            <Stack.Screen
              name="MarketList"
              component={MarketListScreen}
            />
            <Stack.Screen
              name="PrayerTimes"
              component={PrayerTimesScreen}
            />
            <Stack.Screen
              name="OutageList"
              component={OutageListScreen}
            />
            <Stack.Screen
              name="WeatherDetail"
              component={WeatherDetailScreen}
            />
            <Stack.Screen
              name="MarketRates"
              component={MarketRatesScreen}
            />
            <Stack.Screen
              name="EarthquakeList"
              component={EarthquakeListScreen}
            />
            <Stack.Screen
              name="NewsDetail"
              component={NewsDetailScreen}
              options={{ presentation: 'modal' }}
            />
            <Stack.Screen
              name="EditProfile"
              component={EditProfileScreen}
            />
            <Stack.Screen
              name="GalleryList"
              component={GalleryListScreen}
            />
            <Stack.Screen
              name="GalleryDetail"
              component={GalleryDetailScreen}
            />
          </>
        )}
      </Stack.Navigator>
    </NavigationContainer>
  );
};

const { width } = Dimensions.get('window');
const tabBarWidth = Math.min(width - spacing.xl * 2, 390);

const styles = StyleSheet.create({
  tabBarContainer: {
    position: 'absolute',
    bottom: spacing.xxl,
    width: tabBarWidth,
    alignSelf: 'center',
    height: 76,
    borderRadius: borderRadius.full,
    overflow: 'visible',
    ...shadows.medium,
  },
  tabBarInner: {
    position: "absolute",
    left: 0,
    right: 0,
    bottom: 0,
    height: 60,
    overflow: "hidden",
    flexDirection: 'row',
    justifyContent: 'space-around',
    alignItems: 'center',
    backgroundColor: "rgba(20, 20, 20, 0.5)",
    borderWidth: 0.5,
    borderColor: colors.glassBorder,
    borderRadius: borderRadius.full,
  },
  tabItem: {
    flex: 1,
    height: '100%',
    justifyContent: 'center',
    alignItems: 'center',
  },
  tabItemPlaceholder: {
    flex: 1,
    height: '100%',
  },
  centerSpacer: {
    flex: 1,
    height: '100%',
  },
  activeIndicator: {
    width: 4,
    height: 4,
    borderRadius: 2,
    backgroundColor: colors.text,
    marginTop: spacing.xs,
  },
  centerTabButton: {
    position: "absolute",
    left: "50%",
    top: 11,
    width: 50,
    height: 50,
    marginLeft: -25,
    borderRadius: 25,
    backgroundColor: "rgba(18,18,18,0.98)",
    borderWidth: 1.5,
    borderColor: colors.primary,
    justifyContent: "center",
    alignItems: "center",
    ...shadows.glow,
  },
  centerTabButtonActive: {
    backgroundColor: "rgba(24, 24, 28, 0.98)",
    borderColor: colors.primary,
    borderWidth: 2,
    shadowColor: colors.primary,
    shadowOpacity: 0.35,
    shadowRadius: 10,
    elevation: 6,
  },
  centerTabDot: {
    width: 4,
    height: 4,
    borderRadius: 2,
    backgroundColor: colors.primary,
    marginTop: 1,
    opacity: 0.55,
  },
  centerTabDotActive: {
    backgroundColor: colors.primary,
    opacity: 1,
    shadowColor: colors.primary,
    shadowOffset: { width: 0, height: 0 },
    shadowOpacity: 0.8,
    shadowRadius: 2,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
    backgroundColor: colors.background,
  },
});
