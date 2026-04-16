import Link from 'next/link';
import { notFound } from 'next/navigation';
import { serverApi } from '@/lib/server-api';
import { ProviderForm } from '../../_components/provider-form';
import { EditProviderClient } from './edit-client';

interface Props {
  params: { id: string };
}

export default async function EditProviderPage({ params }: Props) {
  const id = Number(params.id);
  if (!Number.isFinite(id)) notFound();
  let provider: any;
  try {
    provider = await serverApi.providers.get(id);
  } catch {
    notFound();
  }

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <header className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Tahrirlash: {provider.name_uz}</h1>
        <Link href="/admin/providers" className="text-sm text-muted-foreground hover:underline">
          « Ro'yxatga qaytish
        </Link>
      </header>
      <EditProviderClient id={id} initial={provider} />
    </div>
  );
}
