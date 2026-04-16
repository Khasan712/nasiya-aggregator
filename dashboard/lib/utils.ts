import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function fmtUzs(amount: number | null | undefined): string {
  if (amount == null) return '—';
  return new Intl.NumberFormat('uz-UZ').format(amount) + " so'm";
}

/**
 * Human-readable "X vaqt oldin" in Uzbek. Avoids ambiguous single-letter
 * abbreviations (which previously collided: "s" meant both seconds and hours).
 */
export function timeAgoUz(iso: string | null | undefined): string {
  if (!iso) return '—';
  const d = new Date(iso);
  const ms = Date.now() - d.getTime();
  if (Number.isNaN(ms)) return '—';
  const sec = Math.max(1, Math.floor(ms / 1000));
  if (sec < 45) return 'hozirgina';
  const min = Math.floor(sec / 60);
  if (min < 60) return `${min} daqiqa oldin`;
  const hr = Math.floor(min / 60);
  if (hr < 24) return `${hr} soat oldin`;
  const days = Math.floor(hr / 24);
  if (days < 7) return `${days} kun oldin`;
  // Older than a week → show actual date
  return d.toLocaleDateString('uz-UZ', { day: 'numeric', month: 'short', year: 'numeric' });
}
