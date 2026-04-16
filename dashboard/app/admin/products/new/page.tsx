import Link from 'next/link';
import { serverApi } from '@/lib/server-api';
import { ProductForm } from '../_components/product-form';
import { NewProductClient } from './new-client';

export default async function NewProductPage() {
  const providers = (await serverApi.providers.list()) as Array<{ id: number; name_uz: string }>;
  return (
    <div className="mx-auto max-w-4xl space-y-6">
      <header className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Yangi mahsulot</h1>
        <Link href="/admin/products" className="text-sm text-muted-foreground hover:underline">
          « Ro'yxatga qaytish
        </Link>
      </header>
      <NewProductClient providers={providers} />
    </div>
  );
}
