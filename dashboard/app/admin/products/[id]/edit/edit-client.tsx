'use client';

import { useState, useTransition } from 'react';
import { ProductForm } from '../../_components/product-form';
import { deleteProductAction, updateProductAction, verifyProductAction } from '../../_actions';
import { Button } from '@/components/ui/button';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import { toast } from 'sonner';

interface Props {
  id: number;
  initial: any;
  providers: Array<{ id: number; name_uz: string }>;
}

export function EditProductClient({ id, initial, providers }: Props) {
  const [, startVerify] = useTransition();
  const [pendingDelete, startDelete] = useTransition();
  const [openDelete, setOpenDelete] = useState(false);

  return (
    <>
      <div className="flex items-center justify-between rounded-md border bg-muted/30 px-4 py-2 text-sm">
        <span className="text-muted-foreground">
          Oxirgi tasdiqlangan:{' '}
          {initial.source_verified_at
            ? new Date(initial.source_verified_at).toLocaleString('uz-UZ')
            : '—'}
        </span>
        <div className="flex gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() =>
              startVerify(async () => {
                try {
                  await verifyProductAction(id);
                  toast.success('Tasdiqlandi');
                } catch (e) {
                  toast.error((e as Error).message);
                }
              })
            }
          >
            ✓ Tasdiqlangan deb belgilash
          </Button>
          <Dialog open={openDelete} onOpenChange={setOpenDelete}>
            <DialogTrigger asChild>
              <Button variant="destructive" size="sm">O'chirish</Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>O'chirishni tasdiqlang</DialogTitle>
                <DialogDescription>
                  «{initial.name_uz}» mahsuloti o'chiriladi. Qaytarib bo'lmaydi.
                </DialogDescription>
              </DialogHeader>
              <DialogFooter>
                <Button variant="outline" onClick={() => setOpenDelete(false)}>
                  Bekor qilish
                </Button>
                <Button
                  variant="destructive"
                  disabled={pendingDelete}
                  onClick={() =>
                    startDelete(async () => {
                      try {
                        await deleteProductAction(id);
                      } catch (e) {
                        const msg = (e as Error).message;
                        if (!msg.includes('NEXT_REDIRECT')) toast.error(msg);
                      }
                    })
                  }
                >
                  {pendingDelete ? "O'chirilmoqda…" : "Ha, o'chirish"}
                </Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>
        </div>
      </div>

      <ProductForm
        providers={providers}
        defaultValues={initial}
        onSubmit={(data) => updateProductAction(id, data)}
        submitLabel="Saqlash"
      />
    </>
  );
}
