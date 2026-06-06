import axios from "axios";
import {
  ChatResponse,
  ConversationTurn,
  EmergencyContact,
  Pharmacy,
  Place,
  Institution,
  PostalCode,
  ServiceProvider,
  TaxiStand,
  NewsItem,
  EventItem,
  WeatherData,
  PrayerTimes,
  FuelPrices,
  CurrencyRate,
  GoldPrice,
  Earthquake,
  StreetMarket,
  IzbanSchedule,
  UtilityOutage,
  MunicipalServiceItem,
  IzbanSummary,
  ProjectItem,
  AnnouncementItem,
  JobListingItem,
  GalleryItem,
  Route,
  User,
  TokenResponse,
} from "../types";

const API_BASE_URL =
  process.env.EXPO_PUBLIC_API_BASE_URL?.trim() ||
  (__DEV__ ? "http://localhost:8000/api/v1" : "https://api.aliagai.com/api/v1");

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 60000,
  headers: { "Content-Type": "application/json" },
});

let authToken: string | null = null;
let onUnauthorizedCallback: (() => void) | null = null;

export const setAuthToken = (token: string | null) => {
  authToken = token;
};

export const setOnUnauthorized = (callback: () => void) => {
  onUnauthorizedCallback = callback;
};

api.interceptors.request.use((config) => {
  if (authToken) {
    config.headers.Authorization = `Bearer ${authToken}`;
  }
  const apiKey = process.env.EXPO_PUBLIC_API_KEY;
  if (apiKey) {
    config.headers["X-API-Key"] = apiKey;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response && error.response.status === 401) {
      if (onUnauthorizedCallback) {
        onUnauthorizedCallback();
      }
    }
    return Promise.reject(error);
  }
);

export const chatService = {
  send: async (query: string, conversationHistory: ConversationTurn[] = []): Promise<ChatResponse> => {
    const { data } = await api.post<ChatResponse>("/chat", {
      message: query,
      conversation_history: conversationHistory,
    });
    return data;
  },
};

export const pharmacyService = {
  getToday: async (): Promise<Pharmacy[]> => {
    const { data } = await api.get<Pharmacy[]>("/pharmacies/duty");
    return data;
  },
};

export const weatherService = {
  getToday: async (): Promise<WeatherData | null> => {
    const { data } = await api.get<WeatherData[]>("/data/weather");
    return data && data.length > 0 ? data[0] : null;
  },
};

export const dailyDataService = {
  getPrayerTimes: async (): Promise<PrayerTimes | null> => {
    const { data } = await api.get<PrayerTimes[]>("/data/prayers");
    return data && data.length > 0 ? data[0] : null;
  },
  getFuelPrices: async (): Promise<FuelPrices | null> => {
    const { data } = await api.get<FuelPrices[]>("/data/fuel");
    return data && data.length > 0 ? data[0] : null;
  },
  getCurrency: async (): Promise<CurrencyRate[]> => {
    const { data } = await api.get<CurrencyRate[]>("/data/currency");
    return data || [];
  },
  getGold: async (): Promise<GoldPrice[]> => {
    const { data } = await api.get<GoldPrice[]>("/data/gold");
    return data || [];
  },
  getEarthquakes: async (): Promise<Earthquake[]> => {
    const { data } = await api.get<Earthquake[]>("/data/earthquakes");
    return data || [];
  },
};

export const placeService = {
  getAll: async (category?: string, limit = 20): Promise<Place[]> => {
    const { data } = await api.get<Place[]>("/places", {
      params: { category, limit },
    });
    return data;
  },
  getInstitutions: async (category?: string, limit = 100): Promise<Institution[]> => {
    const { data } = await api.get<Institution[]>("/places/institutions", {
      params: { category, limit },
    });
    return data || [];
  },
  getServices: async (category?: string, limit = 100): Promise<ServiceProvider[]> => {
    const { data } = await api.get<ServiceProvider[]>("/places/services", {
      params: { category, limit },
    });
    return data || [];
  },
};

export const newsService = {
  getAll: async (limit = 10): Promise<NewsItem[]> => {
    const { data } = await api.get<NewsItem[]>("/content/news", { params: { limit } });
    return data;
  },
};

export const eventService = {
  getUpcoming: async (limit = 10): Promise<EventItem[]> => {
    const { data } = await api.get<EventItem[]>("/content/events", {
      params: { limit },
    });
    return data;
  },
};

export const outageService = {
  getActive: async (): Promise<UtilityOutage[]> => {
    const { data } = await api.get<UtilityOutage[]>("/city/outages");
    return data || [];
  },
};

export const cityService = {
  getEmergencyContacts: async (limit = 100): Promise<EmergencyContact[]> => {
    const { data } = await api.get<EmergencyContact[]>("/city/emergency", { params: { limit } });
    return data || [];
  },
  getMarkets: async (limit = 50): Promise<StreetMarket[]> => {
    const { data } = await api.get<StreetMarket[]>("/city/markets", { params: { limit } });
    return data || [];
  },
  getOutages: async (limit = 50): Promise<UtilityOutage[]> => {
    const { data } = await api.get<UtilityOutage[]>("/city/outages", { params: { limit } });
    return data || [];
  },
  getTaxis: async (limit = 100): Promise<TaxiStand[]> => {
    const { data } = await api.get<TaxiStand[]>("/city/taxis", { params: { limit } });
    return data || [];
  },
  getPostalCodes: async (limit = 200): Promise<PostalCode[]> => {
    const { data } = await api.get<PostalCode[]>("/city/postalcodes", { params: { limit } });
    return data || [];
  },
  getIzbanSummary: async (): Promise<IzbanSummary | null> => {
    const { data } = await api.get<IzbanSummary>("/city/izban/summary");
    return data || null;
  },
  getIzbanSchedules: async (limit = 120): Promise<IzbanSchedule[]> => {
    const { data } = await api.get<IzbanSchedule[]>("/city/izban/schedules", { params: { limit } });
    return data || [];
  },
  getMunicipalServices: async (limit = 100): Promise<MunicipalServiceItem[]> => {
    const { data } = await api.get<MunicipalServiceItem[]>("/city/municipal-services", { params: { limit } });
    return data || [];
  },
};

export const projectService = {
  getAll: async (limit = 10): Promise<ProjectItem[]> => {
    const { data } = await api.get<ProjectItem[]>("/content/projects", { params: { limit } });
    return data;
  },
};

export const municipalityService = {
  getAnnouncements: async (limit = 40, type?: string): Promise<AnnouncementItem[]> => {
    const { data } = await api.get<AnnouncementItem[]>("/content/announcements", {
      params: { limit, type },
    });
    return data || [];
  },
  getJobs: async (limit = 20): Promise<JobListingItem[]> => {
    const { data } = await api.get<JobListingItem[]>("/content/jobs", { params: { limit } });
    return data || [];
  },
};

export const galleryService = {
  getAll: async (limit = 20): Promise<GalleryItem[]> => {
    const { data } = await api.get<GalleryItem[]>("/content/galleries", { params: { limit } });
    return data || [];
  },
  getById: async (id: number): Promise<GalleryItem> => {
    const { data } = await api.get<GalleryItem>(`/content/galleries/${id}`);
    return data;
  },
};

export const routeService = {
  getAll: async (limit = 50): Promise<Route[]> => {
    const { data } = await api.get<Route[]>("/routes", { params: { limit } });
    return data || [];
  },
  getById: async (id: number): Promise<Route> => {
    const { data } = await api.get<Route>(`/routes/${id}`);
    return data;
  },
};

export const authService = {
  login: async (email: string, password: string): Promise<TokenResponse> => {
    const { data } = await api.post<TokenResponse>("/auth/login", { email, password });
    return data;
  },
  register: async (name: string, email: string, password: string): Promise<User> => {
    const { data } = await api.post<User>("/auth/register", {
      full_name: name,
      email,
      password,
    });
    return data;
  },
  googleLogin: async (
    idToken: string,
    email?: string,
    fullName?: string,
    avatarUrl?: string
  ): Promise<TokenResponse> => {
    const { data } = await api.post<TokenResponse>("/auth/google-login", {
      id_token: idToken,
      email,
      full_name: fullName,
      avatar_url: avatarUrl,
    });
    return data;
  },
  getMe: async (): Promise<User> => {
    const { data } = await api.get<User>("/auth/me");
    return data;
  },
  updateMe: async (params: {
    full_name?: string;
    email?: string;
    password?: string;
    avatar_url?: string;
  }): Promise<User> => {
    const { data } = await api.put<User>("/auth/me", null, { params });
    return data;
  },
};

export default api;
