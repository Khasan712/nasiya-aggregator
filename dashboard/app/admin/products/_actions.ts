'use server';

import { revalidatePath } from 'next/cache';
import { redirect } from 'next/navigation';
import { productSchema, type ProductInput } from '@/lib/schemas';
import { serverApi } from '@/lib/server-api';

function clean(input: any) {
  return Object.fromEntries(Object.entries(input).map(([k, v]) => [k, v === '' ? null : v]));
}

export async function createProductAction(input: ProductInput) {
  const parsed = productSchema.parse(input);
  await serverApi.products.create(clean(parsed));
  revalidatePath('/admin/products');
  redirect('/admin/products');
}

export async function updateProductAction(id: number, input: ProductInput) {
  const parsed = productSchema.parse(input);
  await serverApi.products.update(id, clean(parsed));
  revalidatePath('/admin/products');
  revalidatePath(`/admin/products/${id}/edit`);
  redirect('/admin/products');
}

export async function deleteProductAction(id: number) {
  await serverApi.products.remove(id);
  revalidatePath('/admin/products');
  redirect('/admin/products');
}

export async function verifyProductAction(id: number) {
  await serverApi.products.verify(id);
  revalidatePath('/admin/products');
}
