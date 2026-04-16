'use server';

import { revalidatePath } from 'next/cache';
import { redirect } from 'next/navigation';
import { providerSchema, type ProviderInput } from '@/lib/schemas';
import { serverApi } from '@/lib/server-api';

function clean(input: ProviderInput) {
  return Object.fromEntries(
    Object.entries(input).map(([k, v]) => [k, v === '' ? null : v]),
  );
}

export async function createProviderAction(input: ProviderInput) {
  const parsed = providerSchema.parse(input);
  await serverApi.providers.create(clean(parsed));
  revalidatePath('/admin/providers');
  redirect('/admin/providers');
}

export async function updateProviderAction(id: number, input: ProviderInput) {
  const parsed = providerSchema.parse(input);
  await serverApi.providers.update(id, clean(parsed));
  revalidatePath('/admin/providers');
  revalidatePath(`/admin/providers/${id}/edit`);
  redirect('/admin/providers');
}

export async function deleteProviderAction(id: number) {
  await serverApi.providers.remove(id);
  revalidatePath('/admin/providers');
  redirect('/admin/providers');
}

export async function verifyProviderAction(id: number) {
  await serverApi.providers.verify(id);
  revalidatePath('/admin/providers');
}
