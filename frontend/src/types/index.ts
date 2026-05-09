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

export interface NewsItem {
  id: number;
  title: string;
  content?: string | null;
  slug?: string | null;
  source_url: string | null;
  image_url?: string | null;
  category: string | null;
  published_at?: string | null;
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

export interface ProjectItem {
  id: number;
  title: string;
  description: string | null;
  status: string;
  category: string | null;
  source_url: string | null;
  image_url: string | null;
}

export interface IzbanSummary {
  total_records: number;
  next_departure?: string | null;
  status: "ok" | "limited" | "unknown";
  message: string;
  updated_at?: string | null;
}
