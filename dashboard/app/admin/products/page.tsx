import Link from 'next/link';
import { serverApi } from '@/lib/server-api';
import { fmtUzs } from '@/lib/utils';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';

interface Product {
  id: number;
  provider_id: number;
  name_uz: string;
  min_limit_uzs: number | null;
  max_limit_uzs: number | null;
  max_term_months: number | null;
  allowed_terms: number[] | null;
  is_interest_free: boolean;
  markup_note_uz: string | null;
  status: 'active' | 'needs_verification' | 'inactive';
  source_verified_at?: string | null;
}

const STATUS_LABEL = { active: 'Aktiv', needs_verification: 'Tekshirish', inactive: 'Noaktiv' } as const;
const STATUS_VARIANT: Record<Product['status'], 'success' | 'warning' | 'destructive'> = {
  active: 'success',
  needs_verification: 'warning',
  inactive: 'destructive',
};

export default async function ProductsPage() {
  let products: Product[] = [];
  let error: string | null = null;
  try {
    products = (await serverApi.products.list()) as Product[];
  } catch (e) {
    error = (e as Error).message;
  }

  return (
    <div className="space-y-6">
      <header className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Mahsulotlar ({products.length})</h1>
        <Button asChild>
          <Link href="/admin/products/new">+ Yangi mahsulot</Link>
        </Button>
      </header>

      {error && (
        <div className="rounded-md border border-red-300 bg-red-50 p-4 text-sm text-red-700">
          Backendga ulanib bo'lmadi: <code>{error}</code>
        </div>
      )}

      <div className="overflow-hidden rounded-lg border">
        <table className="w-full text-sm">
          <thead className="bg-muted text-left">
            <tr>
              <th className="px-4 py-3 font-medium">Nom</th>
              <th className="whitespace-nowrap px-4 py-3 font-medium">Limit (UZS)</th>
              <th className="whitespace-nowrap px-4 py-3 font-medium">Muddat</th>
              <th className="px-4 py-3 font-medium">Foiz</th>
              <th className="px-4 py-3 font-medium">Status</th>
              <th className="px-4 py-3 font-medium"></th>
            </tr>
          </thead>
          <tbody>
            {products.map((p) => (
              <tr key={p.id} className="border-t hover:bg-muted/30">
                <td className="px-4 py-3 align-top font-medium">{p.name_uz}</td>
                <td className="whitespace-nowrap px-4 py-3 align-top tabular-nums text-muted-foreground">
                  {p.min_limit_uzs || p.max_limit_uzs
                    ? `${fmtUzs(p.min_limit_uzs)} – ${fmtUzs(p.max_limit_uzs)}`
                    : '—'}
                </td>
                <td className="whitespace-nowrap px-4 py-3 align-top text-muted-foreground">
                  {p.allowed_terms?.length
                    ? p.allowed_terms.map((t) => `${t} oy`).join(' / ')
                    : p.max_term_months
                      ? `${p.max_term_months} oy`
                      : '—'}
                </td>
                <td className="px-4 py-3 align-top text-muted-foreground">
                  {p.is_interest_free ? (
                    <span className="text-emerald-700">✓ Foizsiz</span>
                  ) : (
                    (p.markup_note_uz ?? '—')
                  )}
                </td>
                <td className="px-4 py-3 align-top">
                  <Badge variant={STATUS_VARIANT[p.status]}>{STATUS_LABEL[p.status]}</Badge>
                </td>
                <td className="px-4 py-3 text-right align-top">
                  <Link
                    href={`/admin/products/${p.id}/edit`}
                    className="text-sm text-primary underline-offset-2 hover:underline"
                  >
                    Tahrirlash
                  </Link>
                </td>
              </tr>
            ))}
            {products.length === 0 && !error && (
              <tr>
                <td colSpan={6} className="px-4 py-8 text-center text-muted-foreground">
                  Mahsulotlar yo'q.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
