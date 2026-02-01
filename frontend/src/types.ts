export type SessionStatus = "planned" | "arrived" | "completed" | "canceled";

export interface UserInfo {
  id: number;
  email: string;
  role: "owner" | "admin";
  location_id: number | null;
}

export interface Game {
  id: number;
  name: string;
  mode_icon?: string | null;
  is_active: boolean;
}

export interface Resource {
  id: number;
  location_id: number;
  name: string;
}

export interface Session {
  id: number;
  location_id: number;
  resource_id: number;
  resource_name: string;
  game_id: number;
  game_name: string;
  game_icon?: string | null;
  start_at: string;
  end_at: string;
  duration_min: number;
  status: SessionStatus;
  players?: number | null;
  contact_name?: string | null;
  contact_phone?: string | null;
  comment?: string | null;
  canceled_reason?: string | null;
  created_at: string;
  updated_at?: string | null;
}

export interface SessionCreate {
  resource_id: number;
  game_id: number;
  start_at: string;
  duration_min: number;
  players?: number | null;
  status?: SessionStatus;
  contact_name?: string | null;
  contact_phone?: string | null;
  comment?: string | null;
}

export interface SessionUpdate {
  resource_id?: number | null;
  game_id?: number | null;
  start_at?: string | null;
  duration_min?: number | null;
  players?: number | null;
  status?: SessionStatus | null;
  contact_name?: string | null;
  contact_phone?: string | null;
  comment?: string | null;
}
