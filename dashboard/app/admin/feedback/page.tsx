import Link from 'next/link';
import { listFeedback, type FeedbackRow } from '@/lib/server-api';
import { Badge } from '@/components/ui/badge';
import { timeAgoUz } from '@/lib/utils';
import { ResolveButton } from './resolve-button';

export const dynamic = 'force-dynamic';

interface Props {
  searchParams: { tab?: string };
}

const LANG_LABEL: Record<string, string> = {
  uz: "🇺🇿 O'zbek",
  ru: '🇷🇺 Русский',
  en: '🇬🇧 English',
};

function userLabel(r: FeedbackRow): string {
  if (r.user_telegram_username) return '@' + r.user_telegram_username;
  if (r.user_first_name) return r.user_first_name;
  if (r.user_telegram_id) return `tg://${r.user_telegram_id}`;
  return '—';
}

export default async function FeedbackPage({ searchParams }: Props) {
  const tab = searchParams.tab === 'all' ? 'all' : 'open';
  let items: FeedbackRow[] = [];
  let total = 0;
  let error: string | null = null;
  try {
    const res = await listFeedback({ only_open: tab === 'open', limit: 200 });
    items = res.items;
    total = res.total;
  } catch (e) {
    error = (e as Error).message;
  }

  return (
    <div className="space-y-6">
      <header>
        <h1 className="text-2xl font-bold">Fikr-mulohazalar ({total})</h1>
        <p className="text-sm text-muted-foreground">
          Bot orqali kelgan foydalanuvchi izohlari.
        </p>
      </header>

      <nav className="inline-flex rounded-lg border bg-card p-1 text-sm">
        <Link
          href="/admin/feedback"
          className={`rounded-md px-4 py-1.5 ${tab === 'open' ? 'bg-primary text-primary-foreground' : 'text-muted-foreground'}`}
        >
          Faqat ochiq
        </Link>
        <Link
          href="/admin/feedback?tab=all"
          className={`rounded-md px-4 py-1.5 ${tab === 'all' ? 'bg-primary text-primary-foreground' : 'text-muted-foreground'}`}
        >
          Barchasi
        </Link>
      </nav>

      {error && (
        <div className="rounded-md border border-red-300 bg-red-50 p-4 text-sm text-red-700">
          Backendga ulanib bo'lmadi: <code>{error}</code>
        </div>
      )}

      {!error && items.length === 0 ? (
        <div className="rounded-lg border bg-muted/30 p-12 text-center text-muted-foreground">
          Hozircha fikr-mulohazalar yo'q.
          <br />
          <span className="text-xs">
            Botda <code>💬 Fikr-mulohaza</code> tugmasini bosib yozing — bu yerda paydo bo'ladi.
          </span>
        </div>
      ) : (
        <div className="space-y-3">
          {items.map((r) => (
            <div
              key={r.id}
              className={`rounded-lg border bg-card p-4 ${r.is_resolved ? 'opacity-60' : ''}`}
            >
              <div className="flex items-start justify-between gap-4">
                <div className="min-w-0 flex-1">
                  <div className="flex flex-wrap items-center gap-2 text-sm">
                    <span className="font-semibold">{userLabel(r)}</span>
                    {r.user_telegram_id && r.user_telegram_username && (
                      <a
                        href={`https://t.me/${r.user_telegram_username}`}
                        target="_blank"
                        rel="noreferrer"
                        className="text-xs text-primary hover:underline"
                      >
                        Telegram'da ochish ↗
                      </a>
                    )}
                    {r.language && (
                      <span className="text-xs text-muted-foreground">
                        {LANG_LABEL[r.language] ?? r.language}
                      </span>
                    )}
                    <span className="text-xs text-muted-foreground">
                      • {timeAgoUz(r.created_at)}
                    </span>
                    {r.is_resolved && <Badge variant="success">Yopilgan</Badge>}
                  </div>
                  <p className="mt-2 whitespace-pre-wrap text-sm leading-relaxed">{r.text}</p>
                </div>
                <ResolveButton id={r.id} isResolved={r.is_resolved} />
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
