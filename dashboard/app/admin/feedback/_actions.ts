'use server';

import { revalidatePath } from 'next/cache';
import { cookies } from 'next/headers';

const BACKEND = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';
const SERVICE_TOKEN = process.env.DASHBOARD_SERVICE_TOKEN || '';

export async function toggleResolveAction(feedbackId: number): Promise<void> {
  const headers: Record<string, string> = { 'Content-Type': 'application/json' };
  const userToken = cookies().get('nasiya_token')?.value;
  if (userToken) headers['Authorization'] = `Bearer ${userToken}`;
  if (SERVICE_TOKEN) headers['X-Service-Token'] = SERVICE_TOKEN;

  const res = await fetch(`${BACKEND}/api/v1/feedback/${feedbackId}/resolve`, {
    method: 'POST',
    headers,
  });
  if (!res.ok) throw new Error(`Backend ${res.status}: ${await res.text()}`);
  revalidatePath('/admin/feedback');
}
