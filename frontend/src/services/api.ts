import axios from "axios";
import { ChatResponse, Pharmacy, Place, NewsItem, EventItem } from "../types";

const API_BASE_URL = __DEV__
  ? "http://10.0.2.2:8000/api"
  : "https://api.aliagai.com/api";

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: { "Content-Type": "application/json" },
});

export const chatService = {
  send: async (query: string): Promise<ChatResponse> => {
    const { data } = await api.post<ChatResponse>("/chat", { query });
    return data;
  },
};

export const pharmacyService = {
  getToday: async (): Promise<Pharmacy[]> => {
    const { data } = await api.get<Pharmacy[]>("/pharmacies", {
      params: { today_only: true },
    });
    return data;
  },
};

export const placeService = {
  getAll: async (category?: string, limit = 20): Promise<Place[]> => {
    const { data } = await api.get<Place[]>("/places", {
      params: { category, limit },
    });
    return data;
  },
  getCategories: async (): Promise<string[]> => {
    const { data } = await api.get<string[]>("/places/categories");
    return data;
  },
};

export const newsService = {
  getAll: async (limit = 10): Promise<NewsItem[]> => {
    const { data } = await api.get<NewsItem[]>("/news", { params: { limit } });
    return data;
  },
};

export const eventService = {
  getUpcoming: async (limit = 10): Promise<EventItem[]> => {
    const { data } = await api.get<EventItem[]>("/events", {
      params: { upcoming: true, limit },
    });
    return data;
  },
};

export default api;
