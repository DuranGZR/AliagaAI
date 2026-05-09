import React from 'react';
import { View, TouchableOpacity, StyleSheet, Dimensions, Keyboard } from 'react-native';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { NavigationContainer } from '@react-navigation/native';
import { Ionicons } from '@expo/vector-icons';
import { BlurView } from 'expo-blur';
import { colors, shadows, borderRadius, spacing } from '../theme';

// Screens
import { HomeScreen } from '../screens/HomeScreen';
import { ChatScreen } from '../screens/ChatScreen';
import { ExploreScreen } from '../screens/ExploreScreen';
import { PlaceDetailScreen } from '../screens/PlaceDetailScreen';
import { SettingsProfileScreen } from '../screens/SettingsProfileScreen';
import { PlacesListScreen } from '../screens/PlacesListScreen';
import { PharmacyListScreen } from '../screens/PharmacyListScreen';
import { NewsDetailScreen } from '../screens/NewsDetailScreen';
import { EditProfileScreen } from '../screens/EditProfileScreen';

const Tab = createBottomTabNavigator();
const Stack = createNativeStackNavigator();

// Tab ikonları — tasarımdaki sıraya göre
const TAB_ICONS: Record<string, { active: string; inactive: string }> = {
  Home: { active: "calendar", inactive: "calendar-outline" },
  Chat: { active: "hardware-chip", inactive: "hardware-chip-outline" },
  Explore: { active: "compass", inactive: "compass-outline" },
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
              accessibilityLabel={options.tabBarAccessibilityLabel}
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

const MainTabs = () => {
  return (
    <Tab.Navigator
      tabBar={props => <FloatingTabBar {...props} />}
      screenOptions={{
        headerShown: false,
        tabBarShowLabel: false,
      }}
    >
      <Tab.Screen name="Home" component={HomeScreen} />
      <Tab.Screen name="Chat" component={ChatScreen} />
      <Tab.Screen name="Explore" component={ExploreScreen} />
    </Tab.Navigator>
  );
};

export const AppNavigator = () => {
  return (
    <NavigationContainer>
      <Stack.Navigator screenOptions={{ headerShown: false, contentStyle: { backgroundColor: colors.background }}}>
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
          name="NewsDetail"
          component={NewsDetailScreen}
          options={{ presentation: 'modal' }}
        />
        <Stack.Screen
          name="EditProfile"
          component={EditProfileScreen}
        />
      </Stack.Navigator>
    </NavigationContainer>
  );
};

const { width } = Dimensions.get('window');

const styles = StyleSheet.create({
  tabBarContainer: {
    position: 'absolute',
    bottom: spacing.xxl,
    width: width - (spacing.huge * 2),
    alignSelf: 'center',
    height: 60,
    borderRadius: borderRadius.full,
    overflow: 'hidden',
    ...shadows.medium,
  },
  tabBarInner: {
    flex: 1,
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
  activeIndicator: {
    width: 4,
    height: 4,
    borderRadius: 2,
    backgroundColor: colors.text,
    marginTop: spacing.xs,
  },
});
