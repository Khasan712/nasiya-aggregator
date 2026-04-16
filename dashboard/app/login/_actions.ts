'use server';

import { cookies } from 'next/headers';
import { redirect } from 'next/navigation';

const BACKEND = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';

export async function loginAction(formData: FormData) {
  const email = String(formData.get('email') ?? '');
  const password = String(formData.get('password') ?? '');
  const next = String(formData.get('next') ?? '/admin/providers');

  const res = await fetch(`${BACKEND}/api/v1/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password }),
    cache: 'no-store',
  });

  if (!res.ok) {
    const text = await res.text();
    return { error: text.includes('Invalid credentials') ? 'Email yoki parol noto\'g\'ri' : `Xatolik: ${res.status}` };
  }

  const data = (await res.json()) as { access_token: string; refresh_token: string };
  cookies().set('nasiya_token', data.access_token, {
    httpOnly: true,
    sameSite: 'lax',
    path: '/',
    maxAge: 60 * 60,
  });
  cookies().set('nasiya_refresh', data.refresh_token, {
    httpOnly: true,
    sameSite: 'lax',
    path: '/',
    maxAge: 60 * 60 * 24 * 30,
  });
  redirect(next.startsWith('/admin') ? next : '/admin/providers');
}

export async function logoutAction() {
  cookies().delete('nasiya_token');
  cookies().delete('nasiya_refresh');
  redirect('/login');
}
