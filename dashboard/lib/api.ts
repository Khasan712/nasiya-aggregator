/**
 * Backend API client.
 *
 * Calls go through Next.js rewrite at /api/backend/* → backend at /api/v1/*
 * (configured in next.config.mjs).
 */

export type ProviderStatus =
  | 'active'
  | 'needs_verification'
  | 'deprecated'
  | 'coming_soon';

export interface Provider {
  id: number;
  slug: string;
  name_uz: string;
  name_ru: string | null;
  name_en: string | null;
  legal_name: string | null;
  provider_type: 'bank' | 'mfo' | 'fintech' | 'islamic';
  status: ProviderStatus;
  license_body: string | null;
  license_number: string | null;
  license_url: string | null;
  description_uz: string | null;
  source_verified_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface Product {
  id: number;
  provider_id: number;
  name_uz: string;
  min_limit_uzs: number | null;
  max_limit_uzs: number | null;
  min_term_months: number | null;
  max_term_months: number | null;
  allowed_terms: number[] | null;
  is_interest_free: boolean;
  markup_note_uz: string | null;
  min_age: number | null;
  max_age: number | null;
  use_case: string | null;
  official_url: string | null;
  ios_app_url: string | null;
  android_app_url: string | null;
  telegram_bot: string | null;
  support_phone: string | null;
  support_email: string | null;
  partners_count: number | null;
  status: 'active' | 'needs_verification' | 'inactive';
  source_verified_at: string | null;
}

const BASE = '/api/backend';

async function req<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    ...init,
    headers: {
      'Content-Type': 'application/json',
      ...(init?.headers ?? {}),
    },
    cache: 'no-store',
  });
  if (!res.ok) {
    throw new Error(`API ${res.status}: ${await res.text()}`);
  }
  return (await res.json()) as T;
}

export const api = {
  providers: {
    list: () => req<Provider[]>('/providers'),
    get: (id: number) => req<Provider>(`/providers/${id}`),
  },
  products: {
    list: (providerId?: number) =>
      req<Product[]>(`/products${providerId ? `?provider_id=${providerId}` : ''}`),
    get: (id: number) => req<Product>(`/products/${id}`),
  },
  health: () => req<{ status: string; db: string }>('/health'),
};
