'use client';

import Link from 'next/link';
import { ProviderForm } from '../_components/provider-form';
import { createProviderAction } from '../_actions';

export default function NewProviderPage() {
  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <header className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Yangi provayder</h1>
        <Link href="/admin/providers" className="text-sm text-muted-foreground hover:underline">
          « Ro'yxatga qaytish
        </Link>
      </header>
      <ProviderForm onSubmit={createProviderAction} submitLabel="Yaratish" />
    </div>
  );
}
