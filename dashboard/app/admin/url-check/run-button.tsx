'use client';

import { useTransition } from 'react';
import { useRouter } from 'next/navigation';
import { toast } from 'sonner';
import { Button } from '@/components/ui/button';
import { runUrlCheckAction } from './_actions';

export function RunCheckButton() {
  const [pending, startTransition] = useTransition();
  const router = useRouter();

  return (
    <Button
      disabled={pending}
      onClick={() =>
        startTransition(async () => {
          try {
            const r = await runUrlCheckAction();
            toast.success(`Tekshirildi: ${r.checked} ta URL, ${r.broken} ta sinmagan`);
            router.refresh();
          } catch (e) {
            toast.error((e as Error).message);
          }
        })
      }
    >
      {pending ? 'Tekshirilmoqda…' : '🔍 Hozir tekshirish'}
    </Button>
  );
}
