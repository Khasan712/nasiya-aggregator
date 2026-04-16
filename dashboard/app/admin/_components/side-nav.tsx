'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { cn } from '@/lib/utils';

const NAV: { href: string; label: string; icon: string }[] = [
  { href: '/admin/providers', label: 'Provayderlar', icon: '🏦' },
  { href: '/admin/products', label: 'Mahsulotlar', icon: '💳' },
  { href: '/admin/users', label: 'Foydalanuvchilar', icon: '👥' },
  { href: '/admin/feedback', label: 'Fikr-mulohaza', icon: '💬' },
  { href: '/admin/stats', label: 'Statistika', icon: '📊' },
  { href: '/admin/url-check', label: 'URL tekshiruv', icon: '🔍' },
];

function isActive(pathname: string, href: string): boolean {
  // Exact match, OR pathname starts with href + "/" (so /admin/providers/1/edit
  // also highlights "Provayderlar"). We special-case the dashboard root prefix
  // by requiring the next char to be a slash to avoid /admin/products matching
  // a hypothetical /admin/products-archive in the future.
  if (pathname === href) return true;
  return pathname.startsWith(href + '/');
}

export function SideNav() {
  const pathname = usePathname() || '';
  return (
    <nav className="mt-6 space-y-1 text-sm">
      {NAV.map((n) => {
        const active = isActive(pathname, n.href);
        return (
          <Link
            key={n.href}
            href={n.href as never}
            aria-current={active ? 'page' : undefined}
            className={cn(
              'flex items-center gap-2 rounded-md px-3 py-2 transition-colors',
              active
                ? 'bg-primary/10 font-medium text-primary'
                : 'text-muted-foreground hover:bg-muted hover:text-foreground',
            )}
          >
            <span className="text-base leading-none">{n.icon}</span>
            <span>{n.label}</span>
          </Link>
        );
      })}
    </nav>
  );
}
