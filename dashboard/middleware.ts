import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

const PUBLIC_PATHS = new Set(['/login', '/']);

export function middleware(req: NextRequest) {
  const { pathname } = req.nextUrl;

  // Allow public paths and Next.js internals
  if (
    PUBLIC_PATHS.has(pathname) ||
    pathname.startsWith('/_next') ||
    pathname.startsWith('/api')
  ) {
    return NextResponse.next();
  }

  // Protect /admin/*
  if (pathname.startsWith('/admin')) {
    const token = req.cookies.get('nasiya_token')?.value;
    if (!token) {
      const url = req.nextUrl.clone();
      url.pathname = '/login';
      url.searchParams.set('next', pathname);
      return NextResponse.redirect(url);
    }
  }

  return NextResponse.next();
}

export const config = {
  matcher: ['/((?!_next/static|_next/image|favicon.ico).*)'],
};
