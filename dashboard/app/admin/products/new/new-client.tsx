'use client';

import { ProductForm } from '../_components/product-form';
import { createProductAction } from '../_actions';

export function NewProductClient({ providers }: { providers: Array<{ id: number; name_uz: string }> }) {
  return <ProductForm providers={providers} onSubmit={createProductAction} submitLabel="Yaratish" />;
}
