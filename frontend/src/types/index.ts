export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
  query?: string;
  confidence?: number;
  response_policy?: ChatResponse["response_policy"];
  search_method?: ChatResponse["search_method"];
  persona_profile?: string;
  results?: SearchResult[];
  suggestions?: string[];
}

export interface ConversationTurn {
  role: "user" | "assistant";
  content: string;
}

export interface SearchResult {
  type: string;
  name?: string;
  title?: string;
  url?: string;
  address?: string;
  phone?: string;
  maps_link?: string;
  latitude?: number;
  longitude?: number;
  rating?: number;
  category?: string;
  tags?: string[];
  content?: string;
  similarity?: number;
  date?: string;
  [key: string]: unknown;
}

export interface ChatResponse {
  answer: string;
  intent: string;
  sources: SearchResult[];
  search_method: "none" | "sql" | "rag" | "hybrid" | "llm_only";
  response_policy?:
    | "greeting"
    | "sql_only"
    | "grounded_rag"
    | "grounded_rag_strict"
    | "grounded_plus_model"
    | "model_only_fallback"
    | "no_answer";
  confidence?: number;
  persona_profile?: string;
  follow_up_suggestions?: string[];
}

export interface Pharmacy {
  id: number;
  name: string;
  address: string | null;
  phone: string | null;
  maps_link: string | null;
  duty_date: string;
  district?: string | null;
  latitude?: number | null;
  longitude?: number | null;
}

export interface Place {
  id: number;
  name: string;
  category: string | null;
  subcategory?: string | null;
  description: string | null;
  address: string | null;
  phone: string | null;
  maps_link?: string | null;
  website?: string | null;
  rating: number | null;
  tags: string[] | null;
  latitude?: number | null;
  longitude?: number | null;
  created_at?: string | null;
  image_url?: string | null;
}

export interface Institution {
  id: number;
  name: string;
  address: string | null;
  phone: string | null;
  category: string;
  subcategory?: string | null;
  description?: string | null;
  latitude?: number | null;
  longitude?: number | null;
  website?: string | null;
  working_hours?: Record<string, unknown> | null;
  image_url?: string | null;
  is_active?: boolean;
  created_at?: string | null;
}

export interface ServiceProvider {
  id: number;
  name: string;
  phone: string;
  category: string;
  address?: string | null;
  neighborhood?: string | null;
  description?: string | null;
  is_24h: boolean;
  rating: number;
  is_active?: boolean;
  created_at?: string | null;
}

export interface EmergencyContact {
  id: number;
  name: string;
  phone: string;
  category: string | null;
  description?: string | null;
  priority: number;
}

export interface TaxiStand {
  id: number;
  name: string;
  phone: string | null;
  address: string | null;
  latitude?: number | null;
  longitude?: number | null;
  is_24h: boolean;
}

export interface PostalCode {
  id: number;
  neighborhood: string;
  postal_code: string;
  district: string;
}

export interface NewsItem {
  id: number;
  title: string;
  content?: string | null;
  slug?: string | null;
  source_url: string | null;
  image_url?: string | null;
  category: string | null;
  published_at?: string | null;
  created_at?: string | null;
}

export interface AnnouncementItem {
  id: number;
  title: string;
  content?: string | null;
  type: "duyuru" | "ihale" | string;
  published_at?: string | null;
  source_url?: string | null;
  created_at?: string | null;
}

export interface EventItem {
  id: number;
  title: string;
  description: string | null;
  event_date: string | null;
  end_date?: string | null;
  event_time: string | null;
  location: string | null;
  category: string | null;
  source_url?: string | null;
  image_url?: string | null;
}

export interface WeatherData {
  id: number;
  city: string;
  date: string;
  temperature: number | null;
  description: string | null;
  icon: string | null;
  humidity: string | null;
  wind: string | null;
  min_temp: number | null;
  max_temp: number | null;
  fetched_at?: string | null;
}

export interface PrayerTimes {
  id: number;
  city: string;
  date: string;
  fajr: string | null;
  sunrise: string | null;
  dhuhr: string | null;
  asr: string | null;
  maghrib: string | null;
  isha: string | null;
  fetched_at?: string | null;
}

export interface FuelPrices {
  id: number;
  city: string;
  gasoline: number | null;
  diesel: number | null;
  lpg: number | null;
  fetched_at?: string | null;
}

export interface CurrencyRate {
  id: number;
  code: string;
  name: string | null;
  buying: number | null;
  selling: number | null;
  change_pct: number | null;
  fetched_at?: string | null;
}

export interface GoldPrice {
  id: number;
  name: string;
  buying: number | null;
  selling: number | null;
  change_pct: number | null;
  fetched_at?: string | null;
}

export interface Earthquake {
  id: number;
  magnitude: number;
  location: string | null;
  depth: number | null;
  latitude: number | null;
  longitude: number | null;
  event_date: string | null;
  source: string | null;
  fetched_at?: string | null;
}

export interface StreetMarket {
  id: number;
  name: string;
  day_of_week: string;
  neighborhood: string | null;
  address: string | null;
  description: string | null;
}

export interface IzbanSchedule {
  id: number;
  line: string | null;
  station: string | null;
  direction: string | null;
  departure_time: string | null;
  day_type: string | null;
}

export interface UtilityOutage {
  id: number;
  type: string;          // su | elektrik
  district: string | null;
  neighborhood: string | null;
  description: string | null;
  start_date: string | null;
  end_date: string | null;
  source: string | null;
  created_at?: string | null;
}

export interface MunicipalServiceItem {
  id: number;
  hizmet_tipi: string;
  birim: string;
  calisma_saatleri?: string | null;
  iletisim?: string | null;
  source_url: string;
  last_verified_at?: string | null;
  quality_score: number;
}

export interface ProjectItem {
  id: number;
  title: string;
  description: string | null;
  status: string;
  category: string | null;
  source_url: string | null;
  image_url: string | null;
  created_at?: string | null;
}

export interface IzbanSummary {
  total_records: number;
  next_departure?: string | null;
  status: "ok" | "limited" | "unknown";
  message: string;
  updated_at?: string | null;
}

export interface JobListingItem {
  id: number;
  title: string;
  company?: string | null;
  location?: string | null;
  description?: string | null;
  source_url?: string | null;
  published_at?: string | null;
  is_active: boolean;
  created_at?: string | null;
}

export interface GalleryImageItem {
  id: number;
  gallery_id: number;
  image_url: string;
  description?: string | null;
}

export interface GalleryItem {
  id: number;
  title: string;
  slug?: string | null;
  cover_image_url?: string | null;
  source_url?: string | null;
  publish_date?: string | null;
  created_at?: string | null;
  images: GalleryImageItem[];
}

export interface RouteStop {
  id: number;
  route_id: number;
  place_id: number | null;
  stop_name: string;
  latitude: number;
  longitude: number;
  sort_order: number;
}

export interface Route {
  id: number;
  title: string;
  eyebrow: string;
  description: string;
  duration: string;
  icon: string;
  image_url: string | null;
  tags: string[] | null;
  is_active: boolean;
  created_at: string;
  stops: RouteStop[];
}

export interface User {
  id: number;
  email: string;
  full_name: string;
  avatar_url: string | null;
  is_google_user: boolean;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

