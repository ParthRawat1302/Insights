// Backend API Response Models - MUST MATCH BACKEND EXACTLY

export interface UserProfileResponse {
  id: string;
  email: string;
  name: string | null;
  is_active: boolean;
  created_at: string;
  stats: {
    datasets_uploaded: number;
    dashboards_created: number;
    insights_generated: number;
  };
}

export interface DatasetResponse {
  dataset_id: string;
  filename: string;
  status: 'PROCESSING' | 'READY' | 'FAILED';
}

export interface Widget {
  widget_id: string;
  type: 'kpi' | 'chart';
  metric?: string;
  value?: number;
  format?: string | null;
  chart_type?: 'line' | 'bar' | 'scatter';
  x?: string;
  y?: string;
  aggregation?: string | null;
  data?: Array<Record<string, any>>;
}

export interface DashboardResponse {
  dashboard_id: string;
  dataset_id: string;
  title: string;
  widgets: Widget[];
}

export interface Insight {
  type: 'trend' | 'anomaly' | 'data_quality';
  message: string;
}

export interface InsightResponse {
  dataset_id: string;
  insights: Insight[];
  summary: string | null;
}

export interface LoginRequest {
  username: string; // FastAPI uses 'username' for OAuth2
  password: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  name?: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
}
