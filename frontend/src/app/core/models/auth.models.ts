export interface UserProfile {
  id: string;
  email: string;
  full_name: string | null;
  is_active: boolean;
  created_at: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  expires_in_minutes: number;
}

export interface SystemHealth {
  status: string;
  environment: string;
  database_connected?: boolean;
  database_connection?: boolean;
}
