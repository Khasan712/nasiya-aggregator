'use client';

import { useRouter } from 'next/navigation';
import { useState, useTransition } from 'react';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Button } from '@/components/ui/button';

interface Props {
  initial: {
    role?: string;
    language?: string;
    has_telegram?: string;
    search?: string;
  };
}

const ALL = '__all';

export function UserFilters({ initial }: Props) {
  const router = useRouter();
  const [pending, startTransition] = useTransition();
  const [role, setRole] = useState(initial.role ?? ALL);
  const [language, setLanguage] = useState(initial.language ?? ALL);
  const [hasTelegram, setHasTelegram] = useState(initial.has_telegram ?? ALL);
  const [search, setSearch] = useState(initial.search ?? '');

  function apply(e?: React.FormEvent) {
    e?.preventDefault();
    const qs = new URLSearchParams();
    if (role && role !== ALL) qs.set('role', role);
    if (language && language !== ALL) qs.set('language', language);
    if (hasTelegram && hasTelegram !== ALL) qs.set('has_telegram', hasTelegram);
    if (search) qs.set('search', search);
    const href = `/admin/users${qs.toString() ? `?${qs}` : ''}` as never;
    startTransition(() => {
      router.push(href);
      router.refresh();
    });
  }

  function reset() {
    setRole(ALL);
    setLanguage(ALL);
    setHasTelegram(ALL);
    setSearch('');
    startTransition(() => {
      router.push('/admin/users' as never);
      router.refresh();
    });
  }

  return (
    <form
      onSubmit={apply}
      className="grid gap-3 rounded-lg border bg-card p-4 md:grid-cols-5"
    >
      <div className="space-y-1">
        <Label htmlFor="search" className="text-xs">
          Qidiruv
        </Label>
        <Input
          id="search"
          placeholder="Ism, username, email…"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
      </div>

      <div className="space-y-1">
        <Label className="text-xs">Rol</Label>
        <Select value={role} onValueChange={setRole}>
          <SelectTrigger>
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value={ALL}>Hammasi</SelectItem>
            <SelectItem value="admin">Admin</SelectItem>
            <SelectItem value="editor">Editor</SelectItem>
            <SelectItem value="viewer">Viewer</SelectItem>
            <SelectItem value="user">Foydalanuvchi</SelectItem>
          </SelectContent>
        </Select>
      </div>

      <div className="space-y-1">
        <Label className="text-xs">Til</Label>
        <Select value={language} onValueChange={setLanguage}>
          <SelectTrigger>
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value={ALL}>Hammasi</SelectItem>
            <SelectItem value="uz">🇺🇿 O'zbek</SelectItem>
            <SelectItem value="ru">🇷🇺 Русский</SelectItem>
            <SelectItem value="en">🇬🇧 English</SelectItem>
          </SelectContent>
        </Select>
      </div>

      <div className="space-y-1">
        <Label className="text-xs">Kanal</Label>
        <Select value={hasTelegram} onValueChange={setHasTelegram}>
          <SelectTrigger>
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value={ALL}>Hammasi</SelectItem>
            <SelectItem value="true">Faqat Telegram</SelectItem>
            <SelectItem value="false">Faqat Web</SelectItem>
          </SelectContent>
        </Select>
      </div>

      <div className="flex items-end gap-2">
        <Button type="submit" disabled={pending} className="flex-1">
          {pending ? '…' : 'Qo\'llash'}
        </Button>
        <Button type="button" variant="outline" onClick={reset} disabled={pending}>
          Tozalash
        </Button>
      </div>
    </form>
  );
}
