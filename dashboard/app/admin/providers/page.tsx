import { serverApi } from '@/lib/server-api';
import Link from 'next/link';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';

interface Provider {
  id: number;
  slug: string;
  name_uz: string;
  provider_type: 'bank' | 'mfo' | 'fintech' | 'islamic';
  status: 'active' | 'needs_verification' | 'deprecated' | 'coming_soon';
  license_body: string | null;
  license_number: string | null;
  source_verified_at: string | null;
}

const TYPE_LABEL = { bank: 'Bank', mfo: 'MKT', fintech: 'Fintech', islamic: 'Islomiy' } as const;
const STATUS_LABEL = {
  active: 'Aktiv',
  needs_verification: 'Tekshirish kerak',
  deprecated: 'Eskirgan',
  coming_soon: 'Tez kunda',
} as const;
const STATUS_VARIANT: Record<Provider['status'], 'success' | 'warning' | 'destructive' | 'outline'> = {
  active: 'success',
  needs_verification: 'warning',
  deprecated: 'destructive',
  coming_soon: 'outline',
};

export default async function ProvidersPage() {
  let providers: Provider[] = [];
  let error: string | null = null;
  try {
    providers = (await serverApi.providers.list()) as Provider[];
  } catch (e) {
    error = (e as Error).message;
  }

  return (
    <div className="space-y-6">
      <header className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Provayderlar ({providers.length})</h1>
        <Button asChild>
          <Link href="/admin/providers/new">+ Yangi provayder</Link>
        </Button>
      </header>

      {error && (
        <div className="rounded-md border border-red-300 bg-red-50 p-4 text-sm text-red-700">
          Backendga ulanib bo'lmadi: <code>{error}</code>
        </div>
      )}

      <div className="overflow-hidden rounded-lg border">
        <table className="w-full text-sm">
          <thead className="bg-muted">
            <tr className="text-left">
              <th className="px-4 py-3 font-medium">Nom</th>
              <th className="px-4 py-3 font-medium">Tur</th>
              <th className="px-4 py-3 font-medium">Lisenziya</th>
              <th className="px-4 py-3 font-medium">Status</th>
              <th className="whitespace-nowrap px-4 py-3 font-medium">Tasdiqlangan</th>
              <th className="px-4 py-3 font-medium"></th>
            </tr>
          </thead>
          <tbody>
            {providers.map((p) => (
              <tr key={p.id} className="border-t hover:bg-muted/30">
                <td className="px-4 py-3 align-top">
                  <div className="font-medium">{p.name_uz}</div>
                  <div className="font-mono text-xs text-muted-foreground">/{p.slug}</div>
                </td>
                <td className="px-4 py-3 align-top text-muted-foreground">
                  {TYPE_LABEL[p.provider_type]}
                </td>
                <td className="px-4 py-3 align-top text-muted-foreground">
                  {p.license_body ? `${p.license_body} ${p.license_number ?? ''}`.trim() : '—'}
                </td>
                <td className="px-4 py-3 align-top">
                  <Badge variant={STATUS_VARIANT[p.status]}>{STATUS_LABEL[p.status]}</Badge>
                </td>
                <td className="whitespace-nowrap px-4 py-3 align-top text-muted-foreground">
                  {p.source_verified_at
                    ? new Date(p.source_verified_at).toLocaleDateString('uz-UZ')
                    : '—'}
                </td>
                <td className="px-4 py-3 text-right align-top">
                  <Link
                    href={`/admin/providers/${p.id}/edit`}
                    className="text-sm text-primary underline-offset-2 hover:underline"
                  >
                    Tahrirlash
                  </Link>
                </td>
              </tr>
            ))}
            {providers.length === 0 && !error && (
              <tr>
                <td colSpan={6} className="px-4 py-8 text-center text-muted-foreground">
                  Hozircha provayderlar yo'q.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
