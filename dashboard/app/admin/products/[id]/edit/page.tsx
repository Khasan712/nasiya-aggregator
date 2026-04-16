import Link from 'next/link';
import { notFound } from 'next/navigation';
import { serverApi } from '@/lib/server-api';
import { EditProductClient } from './edit-client';

interface Props {
  params: { id: string };
}

export default async function EditProductPage({ params }: Props) {
  const id = Number(params.id);
  if (!Number.isFinite(id)) notFound();
  let product: any;
  try {
    product = await serverApi.products.get(id);
  } catch {
    notFound();
  }
  const providers = (await serverApi.providers.list()) as Array<{ id: number; name_uz: string }>;

  return (
    <div className="mx-auto max-w-4xl space-y-6">
      <header className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Tahrirlash: {product.name_uz}</h1>
        <Link href="/admin/products" className="text-sm text-muted-foreground hover:underline">
          « Ro'yxatga qaytish
        </Link>
      </header>
      <EditProductClient id={id} initial={product} providers={providers} />
    </div>
  );
}
