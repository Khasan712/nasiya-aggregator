/** Zod schemas mirroring backend Pydantic schemas. */
import { z } from 'zod';

export const providerTypeEnum = z.enum(['bank', 'mfo', 'fintech', 'islamic']);
export const providerStatusEnum = z.enum(['active', 'needs_verification', 'deprecated', 'coming_soon']);

export const providerSchema = z.object({
  slug: z.string().min(1).max(64).regex(/^[a-z0-9-]+$/, 'lowercase, digits, dashes only'),
  name_uz: z.string().min(1).max(255),
  name_ru: z.string().max(255).nullish(),
  name_en: z.string().max(255).nullish(),
  legal_name: z.string().max(255).nullish(),
  logo_url: z.string().url().nullish().or(z.literal('')),
  brand_color: z.string().max(16).nullish(),
  provider_type: providerTypeEnum,
  status: providerStatusEnum,
  license_body: z.string().max(64).nullish(),
  license_number: z.string().max(64).nullish(),
  license_date: z.string().nullish(),
  license_url: z.string().url().nullish().or(z.literal('')),
  description_uz: z.string().nullish(),
  description_ru: z.string().nullish(),
  description_en: z.string().nullish(),
});
export type ProviderInput = z.infer<typeof providerSchema>;

export const productUseCaseEnum = z.enum(['online', 'offline', 'universal', 'cash', 'auto']);
export const productStatusEnum = z.enum(['active', 'needs_verification', 'inactive']);

export const productSchema = z.object({
  provider_id: z.coerce.number().int().positive(),
  name_uz: z.string().min(1).max(255),
  name_ru: z.string().nullish(),
  name_en: z.string().nullish(),
  min_limit_uzs: z.coerce.number().int().nonnegative().nullish(),
  max_limit_uzs: z.coerce.number().int().nonnegative().nullish(),
  min_term_months: z.coerce.number().int().nonnegative().nullish(),
  max_term_months: z.coerce.number().int().nonnegative().nullish(),
  allowed_terms: z
    .string()
    .nullish()
    .transform((v) => (v ? v.split(',').map((s) => parseInt(s.trim(), 10)).filter((n) => !Number.isNaN(n)) : null)),
  is_interest_free: z.coerce.boolean(),
  markup_note_uz: z.string().nullish(),
  min_age: z.coerce.number().int().min(0).max(120).nullish(),
  max_age: z.coerce.number().int().min(0).max(120).nullish(),
  citizenship_required: z.string().nullish(),
  min_income_uzs: z.coerce.number().int().nonnegative().nullish(),
  eligibility_note_uz: z.string().nullish(),
  use_case: productUseCaseEnum.nullish(),
  description_uz: z.string().nullish(),
  description_ru: z.string().nullish(),
  description_en: z.string().nullish(),
  official_url: z.string().url().nullish().or(z.literal('')),
  ios_app_url: z.string().url().nullish().or(z.literal('')),
  android_app_url: z.string().url().nullish().or(z.literal('')),
  telegram_bot: z.string().nullish(),
  telegram_channel: z.string().nullish(),
  support_phone: z.string().nullish(),
  support_email: z.string().email().nullish().or(z.literal('')),
  partners_count: z.coerce.number().int().nonnegative().nullish(),
  partners_list_url: z.string().url().nullish().or(z.literal('')),
  source_cited_urls: z.record(z.string(), z.string()).nullish(),
  status: productStatusEnum,
});
export type ProductInput = z.infer<typeof productSchema>;
