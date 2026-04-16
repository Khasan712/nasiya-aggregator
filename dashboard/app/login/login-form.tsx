'use client';

import { useState, useTransition } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { loginAction } from './_actions';

export function LoginForm({ next }: { next: string }) {
  const [pending, startTransition] = useTransition();
  const [error, setError] = useState<string | null>(null);

  function onSubmit(formData: FormData) {
    setError(null);
    startTransition(async () => {
      const res = await loginAction(formData);
      if (res?.error) setError(res.error);
    });
  }

  return (
    <form action={onSubmit} className="space-y-4">
      <input type="hidden" name="next" value={next} />
      <div className="space-y-1.5">
        <Label htmlFor="email">Email</Label>
        <Input
          id="email"
          name="email"
          type="email"
          required
          autoComplete="email"
          defaultValue="admin@nasiya.uz"
        />
      </div>
      <div className="space-y-1.5">
        <Label htmlFor="password">Parol</Label>
        <Input id="password" name="password" type="password" required autoComplete="current-password" />
      </div>
      {error && (
        <div className="rounded-md border border-red-300 bg-red-50 p-2 text-xs text-red-700">{error}</div>
      )}
      <Button type="submit" className="w-full" disabled={pending}>
        {pending ? 'Kirilmoqda…' : 'Kirish'}
      </Button>
    </form>
  );
}
