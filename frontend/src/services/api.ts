import axios from "axios";
import {
  ChatResponse,
  ConversationTurn,
  Pharmacy,
  Place,
  NewsItem,
  EventItem,
  WeatherData,
  UtilityOutage,
  IzbanSummary,
  ProjectItem,
} from "../types";

const API_BASE_URL =
  process.env.EXPO_PUBLIC_API_BASE_URL?.trim() ||
  (__DEV__ ? "http://localhost:8000/api/v1" : "https://api.aliagai.com/api/v1");

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: { "Content-Type": "application/json" },
});

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

export const placeService = {
  getAll: async (category?: string, limit = 20): Promise<Place[]> => {
    const { data } = await api.get<Place[]>("/places", {
      params: { category, limit },
    });
    return data;
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
    try {
      const { data } = await api.get<UtilityOutage[]>("/city/outages");
      return data;
    } catch {
      // Endpoint olmayabilir, bos donelim
      return [];
    }
  },
};

export const cityService = {
  getOutages: async (limit = 50): Promise<UtilityOutage[]> => {
    try {
      const { data } = await api.get<UtilityOutage[]>("/city/outages", { params: { limit } });
      return data;
    } catch {
      return [];
    }
  },
  getIzbanSummary: async (): Promise<IzbanSummary | null> => {
    try {
      const { data } = await api.get<IzbanSummary>("/city/izban/summary");
      return data;
    } catch {
      return null;
    }
  },
};

export const projectService = {
  getAll: async (limit = 10): Promise<ProjectItem[]> => {
    const { data } = await api.get<ProjectItem[]>("/content/projects", { params: { limit } });
    return data;
  },
};

export default api;

