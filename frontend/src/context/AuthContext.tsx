import React, { createContext, useContext, useState, useEffect } from "react";
import AsyncStorage from "@react-native-async-storage/async-storage";
import { authService, setAuthToken, setOnUnauthorized } from "../services/api";
import { User } from "../types";

interface AuthContextType {
  isLoading: boolean;
  isOnboarded: boolean;
  user: User | null;
  token: string | null;
  completeOnboarding: () => Promise<void>;
  resetOnboarding: () => Promise<void>; // Geliştirici / Test için sıfırlama
  login: (email: string, password: string) => Promise<void>;
  register: (name: string, email: string, password: string) => Promise<void>;
  loginWithGoogle: (
    idToken: string,
    email?: string,
    fullName?: string,
    avatarUrl?: string
  ) => Promise<void>;
  logout: () => Promise<void>;
  updateProfile: (params: {
    full_name?: string;
    email?: string;
    password?: string;
    avatar_url?: string;
  }) => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [isLoading, setIsLoading] = useState(true);
  const [isOnboarded, setIsOnboarded] = useState(false);
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);

  useEffect(() => {
    // 401 Unauthorized durumlarında oturumu otomatik kapat
    setOnUnauthorized(async () => {
      await handleForceLogout();
    });

    // Uygulama başlangıcında yerel verileri yükle
    const loadStorageData = async () => {
      try {
        const storedOnboarded = await AsyncStorage.getItem("@isOnboarded");
        const storedToken = await AsyncStorage.getItem("@token");
        const storedUser = await AsyncStorage.getItem("@user");

        if (storedOnboarded === "true") {
          setIsOnboarded(true);
        }

        if (storedToken) {
          setToken(storedToken);
          setAuthToken(storedToken);

          if (storedUser) {
            setUser(JSON.parse(storedUser));
          }

          // Arka planda profili sunucudan güncelleyelim
          try {
            const freshUser = await authService.getMe();
            setUser(freshUser);
            await AsyncStorage.setItem("@user", JSON.stringify(freshUser));
          } catch (err) {
            console.warn("Profil güncellenemedi veya oturum geçersiz:", err);
            // Eğer sunucu token'ı geçersiz derse çıkış yapalım
            await handleForceLogout();
          }
        }
      } catch (error) {
        console.error("Storage yükleme hatası:", error);
      } finally {
        setIsLoading(false);
      }
    };

    loadStorageData();
  }, []);

  const handleForceLogout = async () => {
    setUser(null);
    setToken(null);
    setAuthToken(null);
    await AsyncStorage.removeItem("@token");
    await AsyncStorage.removeItem("@user");
  };

  const completeOnboarding = async () => {
    try {
      setIsOnboarded(true);
      await AsyncStorage.setItem("@isOnboarded", "true");
    } catch (error) {
      console.error("Onboarding kaydetme hatası:", error);
    }
  };

  const resetOnboarding = async () => {
    try {
      setIsOnboarded(false);
      await AsyncStorage.removeItem("@isOnboarded");
      await handleForceLogout();
    } catch (error) {
      console.error("Onboarding sıfırlama hatası:", error);
    }
  };

  const login = async (email: string, password: string) => {
    try {
      setIsLoading(true);
      const tokenData = await authService.login(email.trim(), password);
      
      setToken(tokenData.access_token);
      setAuthToken(tokenData.access_token);
      await AsyncStorage.setItem("@token", tokenData.access_token);

      const userData = await authService.getMe();
      setUser(userData);
      await AsyncStorage.setItem("@user", JSON.stringify(userData));
    } catch (error) {
      await handleForceLogout();
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const register = async (name: string, email: string, password: string) => {
    try {
      setIsLoading(true);
      await authService.register(name.trim(), email.trim(), password);
      // Kayıt başarılıysa otomatik giriş yap
      await login(email, password);
    } catch (error) {
      setIsLoading(false);
      throw error;
    }
  };

  const loginWithGoogle = async (
    idToken: string,
    email?: string,
    fullName?: string,
    avatarUrl?: string
  ) => {
    try {
      setIsLoading(true);
      const tokenData = await authService.googleLogin(idToken, email, fullName, avatarUrl);
      
      setToken(tokenData.access_token);
      setAuthToken(tokenData.access_token);
      await AsyncStorage.setItem("@token", tokenData.access_token);

      const userData = await authService.getMe();
      setUser(userData);
      await AsyncStorage.setItem("@user", JSON.stringify(userData));
    } catch (error) {
      await handleForceLogout();
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const logout = async () => {
    try {
      setIsLoading(true);
      await handleForceLogout();
    } catch (error) {
      console.error("Çıkış yapma hatası:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const updateProfile = async (params: {
    full_name?: string;
    email?: string;
    password?: string;
    avatar_url?: string;
  }) => {
    try {
      setIsLoading(true);
      const updatedUser = await authService.updateMe(params);
      setUser(updatedUser);
      await AsyncStorage.setItem("@user", JSON.stringify(updatedUser));
    } catch (error) {
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <AuthContext.Provider
      value={{
        isLoading,
        isOnboarded,
        user,
        token,
        completeOnboarding,
        resetOnboarding,
        login,
        register,
        loginWithGoogle,
        logout,
        updateProfile,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth bir AuthProvider içinde kullanılmalıdır.");
  }
  return context;
};
