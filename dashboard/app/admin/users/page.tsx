import { listUsers, type UserListItem } from '@/lib/server-api';
import { Badge } from '@/components/ui/badge';
import { timeAgoUz } from '@/lib/utils';
import { UserFilters } from './_components/filters';

export const dynamic = 'force-dynamic';

interface Props {
  searchParams: {
    role?: string;
    language?: string;
    has_telegram?: string;
    search?: string;
    offset?: string;
  };
}

const ROLE_LABEL: Record<string, string> = {
  admin: 'Admin',
  editor: 'Editor',
  viewer: 'Viewer',
  user: 'Foydalanuvchi',
};
const ROLE_VARIANT: Record<string, 'default' | 'success' | 'warning' | 'outline' | 'destructive'> =
  {
    admin: 'destructive',
    editor: 'warning',
    viewer: 'default',
    user: 'outline',
  };
const LANG_LABEL: Record<string, string> = {
  uz: "🇺🇿 O'zbek",
  ru: '🇷🇺 Русский',
  en: '🇬🇧 English',
};

function displayName(u: UserListItem): string {
  if (u.first_name) return [u.first_name, u.last_name].filter(Boolean).join(' ');
  if (u.telegram_username) return '@' + u.telegram_username;
  if (u.email) return u.email;
  return `#${u.id}`;
}

export default async function UsersPage({ searchParams }: Props) {
  const offset = parseInt(searchParams.offset ?? '0', 10) || 0;
  const params = {
    role: searchParams.role,
    language: searchParams.language,
    has_telegram:
      searchParams.has_telegram === 'true'
        ? true
        : searchParams.has_telegram === 'false'
          ? false
          : undefined,
    search: searchParams.search,
    limit: 50,
    offset,
  };

  let total = 0;
  let items: UserListItem[] = [];
  let error: string | null = null;
  try {
    const res = await listUsers(params);
    total = res.total;
    items = res.items;
  } catch (e) {
    error = (e as Error).message;
  }

  return (
    <div className="space-y-6">
      <header>
        <h1 className="text-2xl font-bold">Foydalanuvchilar ({total})</h1>
        <p className="text-sm text-muted-foreground">
          Bot orqali kirganlar va admin/editor foydalanuvchilari.
        </p>
      </header>

      <UserFilters initial={searchParams} />

      {error && (
        <div className="rounded-md border border-red-300 bg-red-50 p-4 text-sm text-red-700">
          Backendga ulanib bo'lmadi: <code>{error}</code>
        </div>
      )}

      <div className="overflow-hidden rounded-lg border">
        <table className="w-full text-sm">
          <thead className="bg-muted text-left">
            <tr>
              <th className="px-4 py-3 font-medium">ID</th>
              <th className="px-4 py-3 font-medium">Foydalanuvchi</th>
              <th className="px-4 py-3 font-medium">Kanal</th>
              <th className="px-4 py-3 font-medium">Til</th>
              <th className="px-4 py-3 font-medium">Rol</th>
              <th className="px-4 py-3 text-right font-medium">Eventlar</th>
              <th className="px-4 py-3 font-medium">Oxirgi</th>
              <th className="px-4 py-3 font-medium">Qo'shilgan</th>
            </tr>
          </thead>
          <tbody>
            {items.map((u) => (
              <tr key={u.id} className="border-t hover:bg-muted/30">
                <td className="px-4 py-3 font-mono text-xs text-muted-foreground">#{u.id}</td>
                <td className="px-4 py-3">
                  <div className="font-medium">{displayName(u)}</div>
                  {u.email && <div className="text-xs text-muted-foreground">{u.email}</div>}
                </td>
                <td className="px-4 py-3 text-xs">
                  {u.telegram_id ? (
                    <span>
                      <Badge variant="default">Telegram</Badge>
                      <div className="mt-1 font-mono text-muted-foreground">
                        {u.telegram_id}
                        {u.telegram_username && ` · @${u.telegram_username}`}
                      </div>
                    </span>
                  ) : (
                    <Badge variant="outline">Web</Badge>
                  )}
                </td>
                <td className="px-4 py-3 text-xs">{LANG_LABEL[u.language] ?? u.language}</td>
                <td className="px-4 py-3">
                  <Badge variant={ROLE_VARIANT[u.role] ?? 'outline'}>
                    {ROLE_LABEL[u.role] ?? u.role}
                  </Badge>
                </td>
                <td className="px-4 py-3 text-right tabular-nums">
                  {u.event_count > 0 ? (
                    <span className="font-semibold">{u.event_count}</span>
                  ) : (
                    <span className="text-muted-foreground">0</span>
                  )}
                </td>
                <td className="px-4 py-3 text-xs text-muted-foreground">
                  {timeAgoUz(u.last_seen_at)}
                </td>
                <td className="px-4 py-3 text-xs text-muted-foreground">
                  {new Date(u.created_at).toLocaleDateString('uz-UZ')}
                </td>
              </tr>
            ))}
            {items.length === 0 && !error && (
              <tr>
                <td colSpan={8} className="px-4 py-12 text-center text-muted-foreground">
                  Foydalanuvchilar topilmadi. Bot orqali <code>/start</code> bosing —
                  bu sahifaga qaytib kelganingizda o'zingizni ko'rasiz.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {total > items.length && (
        <div className="flex justify-between text-sm text-muted-foreground">
          <span>
            {offset + 1}–{offset + items.length} / {total}
          </span>
          <div className="space-x-2">
            {offset > 0 && (
              <a
                href={`?${new URLSearchParams({
                  ...(searchParams as Record<string, string>),
                  offset: String(Math.max(0, offset - 50)),
                })}`}
                className="text-primary hover:underline"
              >
                ← Oldingi
              </a>
            )}
            {offset + items.length < total && (
              <a
                href={`?${new URLSearchParams({
                  ...(searchParams as Record<string, string>),
                  offset: String(offset + 50),
                })}`}
                className="text-primary hover:underline"
              >
                Keyingi →
              </a>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
