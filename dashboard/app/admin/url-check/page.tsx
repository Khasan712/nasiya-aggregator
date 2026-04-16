import { Badge } from '@/components/ui/badge';
import { RunCheckButton } from './run-button';

interface CheckRow {
  id: number;
  entity_type: string;
  entity_id: number;
  field_name: string;
  url: string;
  status_code: number | null;
  response_time_ms: number | null;
  is_ok: boolean;
  error_message: string | null;
  created_at: string;
}

const BACKEND = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';
const SERVICE_TOKEN = process.env.DASHBOARD_SERVICE_TOKEN || '';

async function fetchLog(onlyBroken: boolean): Promise<CheckRow[]> {
  const url = `${BACKEND}/api/v1/admin/url-check/log?limit=100${onlyBroken ? '&only_broken=true' : ''}`;
  const res = await fetch(url, {
    headers: SERVICE_TOKEN ? { 'X-Service-Token': SERVICE_TOKEN } : {},
    cache: 'no-store',
  });
  if (!res.ok) return [];
  return (await res.json()) as CheckRow[];
}

export const dynamic = 'force-dynamic';

export default async function UrlCheckPage() {
  const [recent, broken] = await Promise.all([fetchLog(false), fetchLog(true)]);
  return (
    <div className="space-y-6">
      <header className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">URL tekshiruv</h1>
          <p className="text-sm text-muted-foreground">
            Cron har kuni Tashkent vaqtida 03:17 da ishlaydi. Manual triggerni quyida bosing.
          </p>
        </div>
        <RunCheckButton />
      </header>

      <section className="space-y-2">
        <h2 className="text-lg font-semibold">
          Sinmagan URL'lar ({broken.length})
        </h2>
        {broken.length === 0 ? (
          <div className="rounded-md border border-emerald-300 bg-emerald-50 p-4 text-sm text-emerald-700">
            ✓ Hammasi joyida — barcha rasmiy URL'lar javob bermoqda
          </div>
        ) : (
          <div className="overflow-hidden rounded-lg border">
            <table className="w-full text-sm">
              <thead className="bg-muted text-left">
                <tr>
                  <th className="px-4 py-2 font-medium">Entity</th>
                  <th className="px-4 py-2 font-medium">Maydon</th>
                  <th className="px-4 py-2 font-medium">URL</th>
                  <th className="px-4 py-2 font-medium">Status</th>
                  <th className="px-4 py-2 font-medium">Vaqti</th>
                </tr>
              </thead>
              <tbody>
                {broken.map((r) => (
                  <tr key={r.id} className="border-t">
                    <td className="px-4 py-2">{r.entity_type}#{r.entity_id}</td>
                    <td className="px-4 py-2 text-muted-foreground">{r.field_name}</td>
                    <td className="max-w-md truncate px-4 py-2"><a className="text-primary underline-offset-2 hover:underline" href={r.url} target="_blank" rel="noreferrer">{r.url}</a></td>
                    <td className="px-4 py-2">
                      <Badge variant="destructive">{r.status_code ?? r.error_message?.split(':')[0] ?? '?'}</Badge>
                    </td>
                    <td className="px-4 py-2 text-muted-foreground">{new Date(r.created_at).toLocaleString('uz-UZ')}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>

      <section className="space-y-2">
        <h2 className="text-lg font-semibold">Oxirgi tekshiruvlar ({recent.length})</h2>
        <div className="overflow-hidden rounded-lg border">
          <table className="w-full text-sm">
            <thead className="bg-muted text-left">
              <tr>
                <th className="px-4 py-2 font-medium">Entity</th>
                <th className="px-4 py-2 font-medium">Maydon</th>
                <th className="px-4 py-2 font-medium">URL</th>
                <th className="px-4 py-2 font-medium">Status</th>
                <th className="px-4 py-2 font-medium">ms</th>
                <th className="px-4 py-2 font-medium">Vaqt</th>
              </tr>
            </thead>
            <tbody>
              {recent.map((r) => (
                <tr key={r.id} className="border-t">
                  <td className="px-4 py-2">{r.entity_type}#{r.entity_id}</td>
                  <td className="px-4 py-2 text-muted-foreground">{r.field_name}</td>
                  <td className="max-w-sm truncate px-4 py-2 text-xs text-muted-foreground">{r.url}</td>
                  <td className="px-4 py-2">
                    <Badge variant={r.is_ok ? 'success' : 'destructive'}>{r.status_code ?? '—'}</Badge>
                  </td>
                  <td className="px-4 py-2 text-muted-foreground">{r.response_time_ms ?? '—'}</td>
                  <td className="px-4 py-2 text-muted-foreground">{new Date(r.created_at).toLocaleTimeString('uz-UZ')}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}
