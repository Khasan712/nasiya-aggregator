'use client';

import { useState, useTransition } from 'react';
import { useRouter } from 'next/navigation';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { toast } from 'sonner';
import { providerSchema, type ProviderInput } from '@/lib/schemas';
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

interface Props {
  defaultValues?: Partial<ProviderInput>;
  onSubmit: (data: ProviderInput) => Promise<void>;
  submitLabel: string;
}

export function ProviderForm({ defaultValues, onSubmit, submitLabel }: Props) {
  const router = useRouter();
  const [pending, startTransition] = useTransition();
  const [error, setError] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    setValue,
    watch,
    formState: { errors },
  } = useForm<ProviderInput>({
    resolver: zodResolver(providerSchema),
    defaultValues: {
      provider_type: 'fintech',
      status: 'active',
      ...defaultValues,
    },
  });

  const submit = (data: ProviderInput) => {
    setError(null);
    startTransition(async () => {
      try {
        await onSubmit(data);
        toast.success('Saqlandi');
      } catch (e) {
        const msg = (e as Error).message;
        // next.js redirect throws a special error — ignore it
        if (msg.includes('NEXT_REDIRECT')) return;
        setError(msg);
        toast.error('Xatolik: ' + msg);
      }
    });
  };

  const f = (key: keyof ProviderInput) => errors[key]?.message;

  return (
    <form onSubmit={handleSubmit(submit)} className="space-y-6">
      <section className="grid gap-4 md:grid-cols-2">
        <div className="space-y-1.5">
          <Label htmlFor="slug">Slug *</Label>
          <Input id="slug" placeholder="alif" {...register('slug')} />
          {f('slug') && <p className="text-xs text-red-600">{f('slug')}</p>}
        </div>
        <div className="space-y-1.5">
          <Label htmlFor="legal_name">Yuridik nom</Label>
          <Input id="legal_name" {...register('legal_name')} />
        </div>

        <div className="space-y-1.5">
          <Label htmlFor="name_uz">Nom (UZ) *</Label>
          <Input id="name_uz" {...register('name_uz')} />
          {f('name_uz') && <p className="text-xs text-red-600">{f('name_uz')}</p>}
        </div>
        <div className="space-y-1.5">
          <Label htmlFor="name_ru">Nom (RU)</Label>
          <Input id="name_ru" {...register('name_ru')} />
        </div>
        <div className="space-y-1.5">
          <Label htmlFor="name_en">Nom (EN)</Label>
          <Input id="name_en" {...register('name_en')} />
        </div>

        <div className="space-y-1.5">
          <Label>Tur *</Label>
          <Select
            value={watch('provider_type')}
            onValueChange={(v) => setValue('provider_type', v as ProviderInput['provider_type'])}
          >
            <SelectTrigger><SelectValue /></SelectTrigger>
            <SelectContent>
              <SelectItem value="bank">Bank</SelectItem>
              <SelectItem value="mfo">MKT</SelectItem>
              <SelectItem value="fintech">Fintech</SelectItem>
              <SelectItem value="islamic">Islomiy</SelectItem>
            </SelectContent>
          </Select>
        </div>
        <div className="space-y-1.5">
          <Label>Status *</Label>
          <Select
            value={watch('status')}
            onValueChange={(v) => setValue('status', v as ProviderInput['status'])}
          >
            <SelectTrigger><SelectValue /></SelectTrigger>
            <SelectContent>
              <SelectItem value="active">Aktiv</SelectItem>
              <SelectItem value="needs_verification">Tekshirish kerak</SelectItem>
              <SelectItem value="deprecated">Eskirgan</SelectItem>
              <SelectItem value="coming_soon">Tez kunda</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </section>

      <section className="grid gap-4 md:grid-cols-2">
        <div className="space-y-1.5">
          <Label htmlFor="logo_url">Logo URL</Label>
          <Input id="logo_url" type="url" {...register('logo_url')} />
        </div>
        <div className="space-y-1.5">
          <Label htmlFor="brand_color">Brend rangi (hex)</Label>
          <Input id="brand_color" placeholder="#0066ff" {...register('brand_color')} />
        </div>
      </section>

      <fieldset className="space-y-4 rounded-lg border p-4">
        <legend className="text-sm font-semibold">Lisenziya (rasmiy manba)</legend>
        <div className="grid gap-4 md:grid-cols-3">
          <div className="space-y-1.5">
            <Label htmlFor="license_body">Organ (CBU/MRTKR)</Label>
            <Input id="license_body" {...register('license_body')} />
          </div>
          <div className="space-y-1.5">
            <Label htmlFor="license_number">Raqam</Label>
            <Input id="license_number" {...register('license_number')} />
          </div>
          <div className="space-y-1.5">
            <Label htmlFor="license_date">Sana</Label>
            <Input id="license_date" type="date" {...register('license_date')} />
          </div>
        </div>
        <div className="space-y-1.5">
          <Label htmlFor="license_url">Lisenziya URL (cbu.uz registri)</Label>
          <Input id="license_url" type="url" {...register('license_url')} />
        </div>
      </fieldset>

      <fieldset className="space-y-4 rounded-lg border p-4">
        <legend className="text-sm font-semibold">Tavsif</legend>
        <div className="space-y-1.5">
          <Label htmlFor="description_uz">UZ</Label>
          <Textarea id="description_uz" rows={3} {...register('description_uz')} />
        </div>
        <div className="space-y-1.5">
          <Label htmlFor="description_ru">RU</Label>
          <Textarea id="description_ru" rows={3} {...register('description_ru')} />
        </div>
        <div className="space-y-1.5">
          <Label htmlFor="description_en">EN</Label>
          <Textarea id="description_en" rows={3} {...register('description_en')} />
        </div>
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
