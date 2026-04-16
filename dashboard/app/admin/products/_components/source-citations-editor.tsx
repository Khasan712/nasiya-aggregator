'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { X } from 'lucide-react';

/**
 * Editor for the source_cited_urls JSON object.
 * Each row = (field name, official URL where the value was confirmed).
 *
 * Per the project rule: every data field should cite the provider's official source.
 */
const COMMON_FIELDS = [
  'max_limit_uzs',
  'min_limit_uzs',
  'allowed_terms',
  'max_term_months',
  'min_term_months',
  'is_interest_free',
  'min_age',
  'max_age',
  'support_phone',
  'support_email',
  'official_url',
  'partners_count',
];

interface Props {
  value: Record<string, string> | null | undefined;
  onChange: (next: Record<string, string>) => void;
}

export function SourceCitationsEditor({ value, onChange }: Props) {
  const [pairs, setPairs] = useState<Array<[string, string]>>(
    () => Object.entries(value ?? {}),
  );

  function update(next: Array<[string, string]>) {
    setPairs(next);
    onChange(Object.fromEntries(next.filter(([k, v]) => k && v)));
  }

  return (
    <div className="space-y-3">
      <div className="rounded-md border bg-muted/30 p-3 text-xs text-muted-foreground">
        📌 Loyiha qoidasi: har bir muhim maydon uchun bu qiymat qaysi <b>rasmiy URL</b>'dan olinganini
        kiritish kerak. Uchinchi tomon (blog/news) qabul qilinmaydi.
      </div>

      {pairs.map(([key, url], i) => (
        <div key={i} className="flex gap-2">
          <select
            className="h-10 w-44 rounded-md border border-input bg-background px-2 text-sm"
            value={key}
            onChange={(e) => {
              const next = [...pairs];
              next[i] = [e.target.value, url];
              update(next);
            }}
          >
            <option value="">— maydon —</option>
            {COMMON_FIELDS.map((f) => (
              <option key={f} value={f}>{f}</option>
            ))}
            {key && !COMMON_FIELDS.includes(key) && <option value={key}>{key}</option>}
          </select>
          <Input
            type="url"
            placeholder="https://provider.uz/page-where-this-was-stated"
            value={url}
            onChange={(e) => {
              const next = [...pairs];
              next[i] = [key, e.target.value];
              update(next);
            }}
          />
          <Button
            type="button"
            variant="outline"
            size="icon"
            onClick={() => update(pairs.filter((_, j) => j !== i))}
          >
            <X className="h-4 w-4" />
          </Button>
        </div>
      ))}

      <Button
        type="button"
        variant="outline"
        size="sm"
        onClick={() => update([...pairs, ['', '']])}
      >
        + Source qo'shish
      </Button>
    </div>
  );
}
