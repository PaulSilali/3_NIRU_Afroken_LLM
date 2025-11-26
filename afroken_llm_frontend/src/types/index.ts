export type Language = 'en' | 'sw' | 'sheng';

export type ServiceType = 'nhif' | 'kra' | 'huduma';

export interface Citation {
  id: string;
  title: string;
  url: string;
  snippet?: string;
}

export interface Message {
  id: string;
  role: 'user' | 'bot' | 'system';
  text: string;
  citations?: Citation[];
  timestamp: string;
  actions?: MessageAction[];
}

export interface MessageAction {
  type: 'BOOK' | 'LINK' | 'FORM';
  label: string;
  payload?: any;
}

export interface UserProfile {
  id: string;
  name?: string;
  phone?: string;
  language: Language;
  county?: string;
}

export interface ChatRequest {
  userId?: string;
  lang: Language;
  message: string;
  context?: {
    service?: ServiceType;
    county?: string;
  };
}

export interface ChatResponse {
  id: string;
  stream?: boolean;
  answer: string;
  citations: Citation[];
  actions?: MessageAction[];
}

export interface Metric {
  label: string;
  value: number | string;
  change?: number;
  trend?: 'up' | 'down' | 'neutral';
}

export interface CountyMetric {
  countyName: string;
  queries: number;
  escalations: number;
  satisfaction: number;
  coordinates: [number, number];
}

export interface DashboardMetrics {
  totalQueries: number;
  satisfactionRate: number;
  avgResponseTime: number;
  escalations: number;
  topIntents: IntentMetric[];
  countySummary: CountyMetric[];
}

export interface IntentMetric {
  intent: string;
  count: number;
  percentage: number;
}

export interface FeedbackRequest {
  chatId: string;
  messageId: string;
  rating: 'helpful' | 'not_helpful';
  comments?: string;
}
