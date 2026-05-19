const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface FamilyMember {
  id: number;
  family_id: number;
  name: string;
  role: string;
  gender: string;
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

export interface FamilyAnalysis {
  family_name: string;
  members_count: number;
  pairs_analysis: PairCompatibility[];
  family_overall_score: number;
  family_dynamics: string;
  energy_distribution: Record<string, number>;
  energy_roles: Array<{ name: string; role: string }>;
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
  const response = await fetch(`${API_BASE}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  });
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Lỗi không xác định' }));
    throw new Error(error.detail || `HTTP ${response.status}`);
  }
  return response.json();
}

export const api = {
  getFamilies: (): Promise<Family[]> => apiFetch('/api/families'),

  createFamily: (data: { name: string; description?: string }): Promise<Family> =>
    apiFetch('/api/families', {
      method: 'POST',
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

  deleteMember: (familyId: number, memberId: number): Promise<void> =>
    apiFetch(`/api/families/${familyId}/members/${memberId}`, { method: 'DELETE' }),

  getFamilyAnalysis: (familyId: number): Promise<FamilyAnalysis> =>
    apiFetch(`/api/families/${familyId}/analysis`),

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
