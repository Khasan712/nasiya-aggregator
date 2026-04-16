'use client';

import { useMemo, useState, useTransition } from 'react';
import { useRouter } from 'next/navigation';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { toast } from 'sonner';
import { productSchema, type ProductInput } from '@/lib/schemas';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { SourceCitationsEditor } from './source-citations-editor';

interface ProviderOption {
  id: number;
  name_uz: string;
}

interface Props {
  providers: ProviderOption[];
  defaultValues?: Partial<ProductInput> & { allowed_terms?: number[] | string | null };
  onSubmit: (data: ProductInput) => Promise<void>;
  submitLabel: string;
}

export function ProductForm({ providers, defaultValues, onSubmit, submitLabel }: Props) {
  const router = useRouter();
  const [pending, startTransition] = useTransition();
  const [error, setError] = useState<string | null>(null);

  const initial = useMemo(() => {
    const dv: any = { ...defaultValues };
    if (Array.isArray(dv.allowed_terms)) dv.allowed_terms = dv.allowed_terms.join(', ');
    return {
      provider_id: providers[0]?.id ?? 0,
      status: 'active',
      is_interest_free: false,
      ...dv,
    };
  }, [defaultValues, providers]);

  const {
    register,
    handleSubmit,
    setValue,
    watch,
    formState: { errors },
  } = useForm<ProductInput>({
    resolver: zodResolver(productSchema) as any,
    defaultValues: initial as any,
  });

  const sourceCitedUrls = watch('source_cited_urls') ?? {};

  const submit = (data: ProductInput) => {
    setError(null);
    startTransition(async () => {
      try {
        await onSubmit(data);
        toast.success('Saqlandi');
      } catch (e) {
        const msg = (e as Error).message;
        if (msg.includes('NEXT_REDIRECT')) return;
        setError(msg);
        toast.error('Xatolik: ' + msg);
      }
    });
  };

  const f = (key: keyof ProductInput) => (errors as any)[key]?.message;

  return (
    <form onSubmit={handleSubmit(submit)} className="space-y-6">
      <fieldset className="space-y-4 rounded-lg border p-4">
        <legend className="text-sm font-semibold">Asosiy</legend>
        <div className="grid gap-4 md:grid-cols-2">
          <div className="space-y-1.5">
            <Label>Provayder *</Label>
            <Select
              value={String(watch('provider_id') ?? '')}
              onValueChange={(v) => setValue('provider_id', Number(v) as any)}
            >
              <SelectTrigger><SelectValue placeholder="Tanlang" /></SelectTrigger>
              <SelectContent>
                {providers.map((p) => (
                  <SelectItem key={p.id} value={String(p.id)}>{p.name_uz}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <div className="space-y-1.5">
            <Label>Status *</Label>
            <Select
              value={watch('status')}
              onValueChange={(v) => setValue('status', v as ProductInput['status'])}
            >
              <SelectTrigger><SelectValue /></SelectTrigger>
              <SelectContent>
                <SelectItem value="active">Aktiv</SelectItem>
                <SelectItem value="needs_verification">Tekshirish kerak</SelectItem>
                <SelectItem value="inactive">Noaktiv</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div className="space-y-1.5 md:col-span-2">
            <Label htmlFor="name_uz">Nom (UZ) *</Label>
            <Input id="name_uz" {...register('name_uz')} />
            {f('name_uz') && <p className="text-xs text-red-600">{String(f('name_uz'))}</p>}
          </div>
          <div className="space-y-1.5">
            <Label htmlFor="name_ru">Nom (RU)</Label>
            <Input id="name_ru" {...register('name_ru')} />
          </div>
          <div className="space-y-1.5">
            <Label htmlFor="name_en">Nom (EN)</Label>
            <Input id="name_en" {...register('name_en')} />
          </div>
        </div>
      </fieldset>

      <fieldset className="space-y-4 rounded-lg border p-4">
        <legend className="text-sm font-semibold">Limit va muddat</legend>
        <div className="grid gap-4 md:grid-cols-2">
          <div className="space-y-1.5">
            <Label htmlFor="min_limit_uzs">Min limit (UZS)</Label>
            <Input id="min_limit_uzs" type="number" min={0} {...register('min_limit_uzs')} />
          </div>
          <div className="space-y-1.5">
            <Label htmlFor="max_limit_uzs">Max limit (UZS)</Label>
            <Input id="max_limit_uzs" type="number" min={0} {...register('max_limit_uzs')} />
          </div>
          <div className="space-y-1.5">
            <Label htmlFor="min_term_months">Min muddat (oy)</Label>
            <Input id="min_term_months" type="number" min={0} {...register('min_term_months')} />
          </div>
          <div className="space-y-1.5">
            <Label htmlFor="max_term_months">Max muddat (oy)</Label>
            <Input id="max_term_months" type="number" min={0} {...register('max_term_months')} />
          </div>
          <div className="space-y-1.5 md:col-span-2">
            <Label htmlFor="allowed_terms">Ruxsat etilgan muddatlar (vergul bilan)</Label>
            <Input id="allowed_terms" placeholder="3, 6, 12" {...register('allowed_terms') as any} />
          </div>
        </div>
      </fieldset>

      <fieldset className="space-y-4 rounded-lg border p-4">
        <legend className="text-sm font-semibold">Foiz / Markup</legend>
        <label className="flex items-center gap-2 text-sm">
          <input
            type="checkbox"
            className="h-4 w-4 rounded border-input"
            {...register('is_interest_free')}
          />
          Rasmiy ravishda <b>foizsiz</b> deb e'lon qilingan
        </label>
        <div className="space-y-1.5">
          <Label htmlFor="markup_note_uz">Markup haqida izoh (UZ)</Label>
          <Textarea id="markup_note_uz" rows={2} {...register('markup_note_uz')} />
        </div>
      </fieldset>

      <fieldset className="space-y-4 rounded-lg border p-4">
        <legend className="text-sm font-semibold">Yashash huquqi va shartlar</legend>
        <div className="grid gap-4 md:grid-cols-3">
          <div className="space-y-1.5">
            <Label htmlFor="min_age">Min yosh</Label>
            <Input id="min_age" type="number" min={0} max={120} {...register('min_age')} />
          </div>
          <div className="space-y-1.5">
            <Label htmlFor="max_age">Max yosh</Label>
            <Input id="max_age" type="number" min={0} max={120} {...register('max_age')} />
          </div>
          <div className="space-y-1.5">
            <Label htmlFor="citizenship_required">Fuqarolik</Label>
            <Input id="citizenship_required" placeholder="UZ" {...register('citizenship_required')} />
          </div>
          <div className="space-y-1.5 md:col-span-2">
            <Label htmlFor="min_income_uzs">Min daromad (UZS)</Label>
            <Input id="min_income_uzs" type="number" min={0} {...register('min_income_uzs')} />
          </div>
          <div className="space-y-1.5">
            <Label>Ishlatish</Label>
            <Select
              value={(watch('use_case') as string) ?? ''}
              onValueChange={(v) => setValue('use_case', (v || null) as any)}
            >
              <SelectTrigger><SelectValue placeholder="—" /></SelectTrigger>
              <SelectContent>
                <SelectItem value="universal">Universal</SelectItem>
                <SelectItem value="online">Online</SelectItem>
                <SelectItem value="offline">Offline</SelectItem>
                <SelectItem value="cash">Naqd</SelectItem>
                <SelectItem value="auto">Avto</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>
      </fieldset>

      <fieldset className="space-y-4 rounded-lg border p-4">
        <legend className="text-sm font-semibold">Rasmiy aloqalar</legend>
        <div className="grid gap-4 md:grid-cols-2">
          <div className="space-y-1.5">
            <Label htmlFor="official_url">Rasmiy sayt URL</Label>
            <Input id="official_url" type="url" {...register('official_url')} />
          </div>
          <div className="space-y-1.5">
            <Label htmlFor="partners_list_url">Hamkorlar ro'yxati URL</Label>
            <Input id="partners_list_url" type="url" {...register('partners_list_url')} />
          </div>
          <div className="space-y-1.5">
            <Label htmlFor="ios_app_url">App Store URL</Label>
            <Input id="ios_app_url" type="url" {...register('ios_app_url')} />
          </div>
          <div className="space-y-1.5">
            <Label htmlFor="android_app_url">Google Play URL</Label>
            <Input id="android_app_url" type="url" {...register('android_app_url')} />
          </div>
          <div className="space-y-1.5">
            <Label htmlFor="telegram_bot">Telegram bot (@username)</Label>
            <Input id="telegram_bot" {...register('telegram_bot')} />
          </div>
          <div className="space-y-1.5">
            <Label htmlFor="telegram_channel">Telegram kanal</Label>
            <Input id="telegram_channel" {...register('telegram_channel')} />
          </div>
          <div className="space-y-1.5">
            <Label htmlFor="support_phone">Telefon</Label>
            <Input id="support_phone" {...register('support_phone')} />
          </div>
          <div className="space-y-1.5">
            <Label htmlFor="support_email">Email</Label>
            <Input id="support_email" type="email" {...register('support_email')} />
          </div>
          <div className="space-y-1.5">
            <Label htmlFor="partners_count">Hamkor do'konlar soni</Label>
            <Input id="partners_count" type="number" min={0} {...register('partners_count')} />
          </div>
        </div>
      </fieldset>

      <fieldset className="space-y-4 rounded-lg border p-4">
        <legend className="text-sm font-semibold">📌 Source citations (per-field rasmiy manba)</legend>
        <SourceCitationsEditor
          value={sourceCitedUrls as Record<string, string>}
          onChange={(v) => setValue('source_cited_urls', v as any)}
        />
      </fieldset>

      {error && (
        <div className="rounded-md border border-red-300 bg-red-50 p-3 text-sm text-red-700">{error}</div>
      )}

      <div className="flex justify-end gap-2">
        <Button type="button" variant="outline" onClick={() => router.back()} disabled={pending}>
          Bekor qilish
        </Button>
        <Button type="submit" disabled={pending}>
          {pending ? 'Saqlanmoqda…' : submitLabel}
        </Button>
      </div>
    </form>
  );
}
