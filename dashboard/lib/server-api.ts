/**
 * Server-side backend client. Uses the trusted X-Service-Token from .env.
 * Only import from server components, route handlers, or server actions.
 */

import 'server-only';
import { cookies } from 'next/headers';

const BACKEND = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';
const SERVICE_TOKEN = process.env.DASHBOARD_SERVICE_TOKEN || '';

type FetchInit = RequestInit & { json?: unknown };

function authHeaders(): Record<string, string> {
  const out: Record<string, string> = {};
  let userToken: string | undefined;
  try {
    userToken = cookies().get('nasiya_token')?.value;
  } catch {
    // cookies() not available outside request scope
  }
  if (userToken) out['Authorization'] = `Bearer ${userToken}`;
  if (SERVICE_TOKEN) out['X-Service-Token'] = SERVICE_TOKEN;
  return out;
}

async function call<T>(method: string, path: string, init: FetchInit = {}): Promise<T> {
  const { json, headers, ...rest } = init;
  const res = await fetch(`${BACKEND}/api/v1${path}`, {
    method,
    headers: {
      'Content-Type': 'application/json',
      ...authHeaders(),
      ...headers,
    },
    body: json !== undefined ? JSON.stringify(json) : undefined,
    cache: 'no-store',
    ...rest,
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`Backend ${method} ${path} → ${res.status}: ${text}`);
  }
  if (res.status === 204) return undefined as T;
  return (await res.json()) as T;
}

export interface CurrentUser {
  id: number;
  email: string | null;
  role: string;
  first_name: string | null;
}

export async function getCurrentUser(): Promise<CurrentUser | null> {
  try {
    return await call<CurrentUser>('GET', '/auth/me');
  } catch {
    return null;
  }
}

export const serverApi = {
  providers: {
    list: () => call<unknown[]>('GET', '/providers'),
    get: (id: number) => call<unknown>('GET', `/providers/${id}`),
    create: (body: unknown) => call<unknown>('POST', '/providers', { json: body }),
    update: (id: number, body: unknown) => call<unknown>('PATCH', `/providers/${id}`, { json: body }),
    verify: (id: number) => call<unknown>('POST', `/providers/${id}/verify`),
    remove: (id: number) => call<void>('DELETE', `/providers/${id}`),
  },
  products: {
    list: () => call<unknown[]>('GET', '/products'),
    get: (id: number) => call<unknown>('GET', `/products/${id}`),
    create: (body: unknown) => call<unknown>('POST', '/products', { json: body }),
    update: (id: number, body: unknown) => call<unknown>('PATCH', `/products/${id}`, { json: body }),
    verify: (id: number) => call<unknown>('POST', `/products/${id}/verify`),
    remove: (id: number) => call<void>('DELETE', `/products/${id}`),
  },
  stats: {
    overview: () => call<StatsOverview>('GET', '/stats/overview'),
  },
};

// ─── Stats types (mirrors backend) ─────────────────────────────────────────

export interface StatsCounter {
  today: number;
  last_7d: number;
  last_30d: number;
  total: number;
}

export interface StatsTopProduct {
  product_id: number;
  name_uz: string;
  provider_name_uz: string;
  views: number;
}

export interface StatsAmountBucket {
  bucket_label: string;
  count: number;
}

export interface StatsDailyPoint {
  day: string;
  events: number;
  unique_users: number;
}

export interface StatsEventTypeRow {
  event_type: string;
  count: number;
}

export interface StatsTopProvider {
  provider_id: number;
  name_uz: string;
  views: number;
}

export interface StatsHourlyPoint {
  hour: number;
  events: number;
}

export interface StatsFunnelStep {
  name: string;
  count: number;
}

export interface StatsAmountSummary {
  searches: number;
  avg_uzs: number;
  median_uzs: number;
  max_uzs: number;
}

export interface StatsOverview {
  users: StatsCounter;
  bot_users: StatsCounter;
  events: StatsCounter;
  top_products: StatsTopProduct[];
  top_providers: StatsTopProvider[];
  amount_buckets: StatsAmountBucket[];
  amount_summary: StatsAmountSummary;
  daily_activity: StatsDailyPoint[];
  hourly_activity: StatsHourlyPoint[];
  event_types: StatsEventTypeRow[];
  languages: StatsEventTypeRow[];
  funnel: StatsFunnelStep[];
}

// ─── Users endpoint ────────────────────────────────────────────────────────

export interface UserListItem {
  id: number;
  email: string | null;
  telegram_id: number | null;
  telegram_username: string | null;
  first_name: string | null;
  last_name: string | null;
  language: 'uz' | 'ru' | 'en';
  role: 'admin' | 'editor' | 'viewer' | 'user';
  is_active: boolean;
  last_seen_at: string | null;
  created_at: string;
  event_count: number;
}

export interface UsersResponse {
  total: number;
  items: UserListItem[];
}

function buildQueryString(params: Record<string, unknown>): string {
  const qs = new URLSearchParams();
  for (const [k, v] of Object.entries(params)) {
    if (v === undefined || v === null) continue;
    if (typeof v === 'string' && v === '') continue;
    qs.set(k, String(v));
  }
  return qs.toString() ? `?${qs}` : '';
}

export async function listUsers(params: {
  role?: string;
  language?: string;
  has_telegram?: boolean;
  search?: string;
  limit?: number;
  offset?: number;
}): Promise<UsersResponse> {
  return call<UsersResponse>('GET', `/users${buildQueryString(params)}`);
}

// ─── Feedback ──────────────────────────────────────────────────────────────

export interface FeedbackRow {
  id: number;
  user_id: number | null;
  text: string;
  language: string | null;
  is_resolved: boolean;
  created_at: string;
  user_first_name: string | null;
  user_telegram_username: string | null;
  user_telegram_id: number | null;
}

export interface FeedbackList {
  total: number;
  items: FeedbackRow[];
}

export async function listFeedback(params: {
  only_open?: boolean;
  limit?: number;
  offset?: number;
}): Promise<FeedbackList> {
  return call<FeedbackList>('GET', `/feedback${buildQueryString(params)}`);
}
