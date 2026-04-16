import Link from 'next/link';
import { getCurrentUser } from '@/lib/server-api';
import { logoutAction } from '../login/_actions';
import { SideNav } from './_components/side-nav';

export default async function AdminLayout({ children }: { children: React.ReactNode }) {
  const user = await getCurrentUser();
  return (
    <div className="flex min-h-screen">
      <aside className="flex w-60 flex-col border-r bg-card p-4">
        <Link href="/" className="block text-lg font-semibold">
          Nasiya Admin
        </Link>
        <SideNav />
        <div className="mt-auto space-y-2 border-t pt-4 text-xs text-muted-foreground">
          {user ? (
            <>
              <div>
                <div className="font-medium text-foreground">{user.email ?? user.first_name}</div>
                <div className="capitalize">{user.role}</div>
              </div>
              <form action={logoutAction}>
                <button className="w-full rounded px-2 py-1.5 text-left hover:bg-muted hover:text-foreground">
                  Chiqish
                </button>
              </form>
            </>
          ) : (
            <Link href="/login" className="block">
              Kirish
            </Link>
          )}
        </div>
      </aside>
      <main className="flex-1 p-8">{children}</main>
    </div>
  );
}
