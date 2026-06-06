import React, { createContext, useContext, useState, useEffect, useCallback } from "react";
import * as Location from "expo-location";

interface LocationContextType {
  location: { latitude: number; longitude: number } | null;
  permissionStatus: "granted" | "denied" | "undetermined";
  isLoading: boolean;
  requestPermission: () => Promise<boolean>;
  refreshLocation: () => Promise<void>;
}

const LocationContext = createContext<LocationContextType | undefined>(undefined);

export const LocationProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [location, setLocation] = useState<{ latitude: number; longitude: number } | null>(null);
  const [permissionStatus, setPermissionStatus] = useState<"granted" | "denied" | "undetermined">("undetermined");
  const [isLoading, setIsLoading] = useState(true);

  const requestPermission = useCallback(async () => {
    try {
      const { status } = await Location.requestForegroundPermissionsAsync();
      setPermissionStatus(status === "granted" ? "granted" : "denied");
      return status === "granted";
    } catch (error) {
      console.warn("Failed to request location permission:", error);
      setPermissionStatus("denied");
      return false;
    }
  }, []);

  const refreshLocation = useCallback(async () => {
    setIsLoading(true);
    try {
      const { status } = await Location.getForegroundPermissionsAsync();
      setPermissionStatus(status === "granted" ? "granted" : status === "undetermined" ? "undetermined" : "denied");
      
      if (status === "granted") {
        // Try to get fast cached position first
        const lastKnown = await Location.getLastKnownPositionAsync({});
        if (lastKnown) {
          setLocation({
            latitude: lastKnown.coords.latitude,
            longitude: lastKnown.coords.longitude,
          });
        }
        
        // Then get fresh accurate position
        const current = await Location.getCurrentPositionAsync({
          accuracy: Location.Accuracy.Balanced,
        });
        setLocation({
          latitude: current.coords.latitude,
          longitude: current.coords.longitude,
        });
      }
    } catch (error) {
      console.warn("Failed to get current location:", error);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    void refreshLocation();
  }, [refreshLocation]);

  return (
    <LocationContext.Provider
      value={{
        location,
        permissionStatus,
        isLoading,
        requestPermission,
        refreshLocation,
      }}
    >
      {children}
    </LocationContext.Provider>
  );
};

export const useLocation = () => {
  const context = useContext(LocationContext);
  if (context === undefined) {
    throw new Error("useLocation must be used within a LocationProvider");
  }
  return context;
};
