export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
  results?: SearchResult[];
}

export interface SearchResult {
  type: string;
  name?: string;
  title?: string;
  address?: string;
  phone?: string;
  maps_link?: string;
  rating?: number;
  category?: string;
  tags?: string[];
  content?: string;
  similarity?: number;
  date?: string;
  [key: string]: unknown;
}

export interface ChatResponse {
  query: string;
  ai_response: string;
  intent: {
    intent: "sql" | "rag" | "hybrid";
    category: string;
    filters: Record<string, unknown>;
  };
  results: SearchResult[];
  result_count: number;
}

export interface Pharmacy {
  id: number;
  name: string;
  address: string | null;
  phone: string | null;
  maps_link: string | null;
  duty_date: string;
}

export interface Place {
  id: number;
  name: string;
  category: string | null;
  description: string | null;
  address: string | null;
  phone: string | null;
  maps_link: string | null;
  rating: number | null;
  tags: string[] | null;
}

export interface NewsItem {
  id: number;
  title: string;
  summary: string | null;
  published_date: string | null;
  category: string | null;
  source_url: string | null;
}

export interface EventItem {
  id: number;
  title: string;
  description: string | null;
  event_date: string | null;
  event_time: string | null;
  location: string | null;
  category: string | null;
  is_free: boolean | null;
}
