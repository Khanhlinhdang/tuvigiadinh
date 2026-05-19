const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const AUTH_TOKEN_KEY = 'tvgd_token';
const AUTH_USER_KEY = 'tvgd_user';

export interface AuthUser {
  id: number;
  email: string;
  name?: string;
  picture?: string;
  created_at: string;
}

export interface AuthConfig {
  auth_enabled: boolean;
  google_client_id: string;
}

export const authStore = {
  getToken(): string | null {
    if (typeof window === 'undefined') return null;
    return window.localStorage.getItem(AUTH_TOKEN_KEY);
  },
  setToken(token: string) {
    if (typeof window === 'undefined') return;
    window.localStorage.setItem(AUTH_TOKEN_KEY, token);
  },
  getUser(): AuthUser | null {
    if (typeof window === 'undefined') return null;
    const raw = window.localStorage.getItem(AUTH_USER_KEY);
    if (!raw) return null;
    try { return JSON.parse(raw) as AuthUser; } catch { return null; }
  },
  setUser(user: AuthUser) {
    if (typeof window === 'undefined') return;
    window.localStorage.setItem(AUTH_USER_KEY, JSON.stringify(user));
  },
  clear() {
    if (typeof window === 'undefined') return;
    window.localStorage.removeItem(AUTH_TOKEN_KEY);
    window.localStorage.removeItem(AUTH_USER_KEY);
  },
};

export interface FamilyMember {
  id: number;
  family_id: number;
  name: string;
  role: string;
  gender: string;
  occupation?: string;
  birth_year: number;
  birth_month?: number;
  birth_day?: number;
  birth_calendar?: 'solar' | 'lunar';
  solar_year?: number;
  solar_month?: number;
  solar_day?: number;
  lunar_year?: number;
  lunar_month?: number;
  lunar_day?: number;
  is_leap_month?: boolean;
  thien_can?: string;
  dia_chi?: string;
  ngu_hanh?: string;
  nap_am?: string;
  energy_role?: string;
  created_at: string;
}

export interface Family {
  id: number;
  name: string;
  description?: string;
  created_at: string;
  members: FamilyMember[];
}

export interface Citation {
  key: string;
  title: string;
  author: string;
  year: string;
  note: string;
}

export interface SinhKhac {
  type: string;
  headline: string;
  detail: string;
}

export interface PairCompatibility {
  member1_id: number;
  member2_id: number;
  member1_name: string;
  member2_name: string;
  member1_role: string;
  member2_role: string;
  member1_can_chi: string;
  member2_can_chi: string;
  can_compatibility: { relation: string; type: string; score: number; description: string };
  chi_compatibility: { relations: string[]; score: number; primary_relation: string; description: string };
  hanh_compatibility: { relation: string; score: number; description: string };
  overall_score: number;
  compatibility_level: string;
  summary: string;
  recommendations: string[];
  radar_scores: {
    emotional: number;
    communication: number;
    financial: number;
    lifestyle: number;
    stability: number;
  };
  relationship_type?: string;
  relationship_key?: string;
  sinh_khac?: SinhKhac;
  relationship_advice?: string[];
  relationship_explanation?: string;
  citations?: Citation[];
}

export interface PairSummary {
  member1_name: string;
  member2_name: string;
  relationship_type?: string;
  overall_score: number;
  compatibility_level: string;
  headline: string;
}

export interface ExecutiveSummary {
  strengths: string[];
  risks: string[];
  actions: string[];
  energy_keeper?: { name: string; role: string } | null;
  best_pair?: PairSummary | null;
  attention_pair?: PairSummary | null;
  positioning_note: string;
}

export interface FamilyAnalysis {
  family_name: string;
  members_count: number;
  pairs_analysis: PairCompatibility[];
  family_overall_score: number;
  family_dynamics: string;
  energy_distribution: Record<string, number>;
  energy_roles: Array<{ name: string; role: string }>;
  executive_summary?: ExecutiveSummary;
  ai_interpretation?: string;
  analysis_mode?: 'online' | 'offline';
  sources?: Citation[];
  annual_forecast?: FamilyForecast | null;
}

export interface ForecastSection {
  key: string;
  title: string;
  icon: string;
  content: string;
}

export interface ForecastDetailed {
  highlights: string[];
  sections: ForecastSection[];
}

export interface MemberForecast {
  id?: number;
  name: string;
  role: string;
  gender?: string;
  ngu_hanh?: string;
  nap_am?: string;
  birth_can_chi: string;
  year_can_chi: string;
  is_thai_tue: boolean;
  is_xung: boolean;
  energy_level: string;
  forecast: string;
  score: number;
  detailed?: ForecastDetailed;
}

export interface FamilyForecast {
  year: number;
  member_forecasts: MemberForecast[];
  family_year_summary: string;
  thai_tue_count: number;
  positive_count: number;
}

async function apiFetch(path: string, options?: RequestInit) {
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options?.headers as Record<string, string> | undefined),
  };
  const token = authStore.getToken();
  if (token) headers['Authorization'] = `Bearer ${token}`;

  const response = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers,
  });
  if (!response.ok) {
    if (response.status === 401) {
      authStore.clear();
    }
    const error = await response.json().catch(() => ({ detail: 'Lỗi không xác định' }));
    throw new Error(error.detail || `HTTP ${response.status}`);
  }
  if (response.status === 204) return null;
  return response.json();
}

export interface SavedAnalysisSummary {
  id: number;
  family_id: number;
  title?: string;
  note?: string;
  family_overall_score?: number;
  analysis_mode?: 'online' | 'offline';
  created_at: string;
}

export interface SavedAnalysisDetail extends SavedAnalysisSummary {
  payload: FamilyAnalysis;
}

export const api = {
  // Auth
  getAuthConfig: (): Promise<AuthConfig> => apiFetch('/api/auth/config'),
  loginGoogle: (credential: string): Promise<{ access_token: string; token_type: string; user: AuthUser }> =>
    apiFetch('/api/auth/google', {
      method: 'POST',
      body: JSON.stringify({ credential }),
    }),
  getMe: (): Promise<AuthUser> => apiFetch('/api/auth/me'),

  getFamilies: (): Promise<Family[]> => apiFetch('/api/families'),

  createFamily: (data: { name: string; description?: string }): Promise<Family> =>
    apiFetch('/api/families', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  updateFamily: (id: number, data: { name?: string; description?: string }): Promise<Family> =>
    apiFetch(`/api/families/${id}`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    }),

  getFamily: (id: number): Promise<Family> => apiFetch(`/api/families/${id}`),

  deleteFamily: (id: number): Promise<void> =>
    apiFetch(`/api/families/${id}`, { method: 'DELETE' }),

  addMember: (
    familyId: number,
    data: {
      name: string;
      role: string;
      gender: string;
      occupation?: string;
      birth_year: number;
      birth_month?: number;
      birth_day?: number;
      birth_calendar?: 'solar' | 'lunar';
      is_leap_month?: boolean;
    }
  ): Promise<FamilyMember> =>
    apiFetch(`/api/families/${familyId}/members`, {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  updateMember: (
    familyId: number,
    memberId: number,
    data: Partial<{
      name: string;
      role: string;
      gender: string;
      occupation: string;
      birth_year: number;
      birth_month: number;
      birth_day: number;
      birth_calendar: 'solar' | 'lunar';
      is_leap_month: boolean;
    }>
  ): Promise<FamilyMember> =>
    apiFetch(`/api/families/${familyId}/members/${memberId}`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    }),

  deleteMember: (familyId: number, memberId: number): Promise<void> =>
    apiFetch(`/api/families/${familyId}/members/${memberId}`, { method: 'DELETE' }),

  getFamilyAnalysis: (familyId: number, useAi = false): Promise<FamilyAnalysis> =>
    apiFetch(`/api/families/${familyId}/analysis${useAi ? '?ai=true' : ''}`),

  getAnnualForecast: (familyId: number, year: number): Promise<FamilyForecast> =>
    apiFetch(`/api/families/${familyId}/forecast`, {
      method: 'POST',
      body: JSON.stringify({ family_id: familyId, year }),
    }),

  sendChat: (familyId: number, question: string): Promise<{ response: string }> =>
    apiFetch(`/api/families/${familyId}/chat`, {
      method: 'POST',
      body: JSON.stringify({ family_id: familyId, question }),
    }),

  // Saved analyses
  listSavedAnalyses: (familyId: number): Promise<SavedAnalysisSummary[]> =>
    apiFetch(`/api/families/${familyId}/saved-analyses`),

  saveAnalysis: (familyId: number, data: { title?: string; note?: string }, useAi = false): Promise<SavedAnalysisDetail> =>
    apiFetch(`/api/families/${familyId}/saved-analyses${useAi ? '?ai=true' : ''}`, {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  getSavedAnalysis: (id: number): Promise<SavedAnalysisDetail> =>
    apiFetch(`/api/saved-analyses/${id}`),

  deleteSavedAnalysis: (id: number): Promise<void> =>
    apiFetch(`/api/saved-analyses/${id}`, { method: 'DELETE' }),

  getCanChi: (year: number) => apiFetch(`/api/astrology/can-chi/${year}`),

  convertDate: (data: { year: number; month: number; day: number; calendar: 'solar' | 'lunar'; is_leap_month?: boolean }) =>
    apiFetch('/api/astrology/convert-date', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  getSources: (): Promise<{ sources: Citation[] }> => apiFetch('/api/astrology/sources'),

  aiHealth: (): Promise<{ openai_configured: boolean; mode: 'online' | 'offline' }> =>
    apiFetch('/api/health/ai'),
};
