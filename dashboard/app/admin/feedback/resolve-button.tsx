'use client';

import { useTransition } from 'react';
import { useRouter } from 'next/navigation';
import { toast } from 'sonner';
import { Button } from '@/components/ui/button';
import { toggleResolveAction } from './_actions';

export function ResolveButton({ id, isResolved }: { id: number; isResolved: boolean }) {
  const [pending, startTransition] = useTransition();
  const router = useRouter();
  return (
    <Button
      size="sm"
      variant={isResolved ? 'outline' : 'default'}
      disabled={pending}
      onClick={() =>
        startTransition(async () => {
          try {
            await toggleResolveAction(id);
            toast.success(isResolved ? 'Qayta ochildi' : 'Yopildi');
            router.refresh();
          } catch (e) {
            toast.error((e as Error).message);
          }
        })
      }
    >
      {pending ? '…' : isResolved ? 'Qayta ochish' : 'Yopish'}
    </Button>
  );
}
