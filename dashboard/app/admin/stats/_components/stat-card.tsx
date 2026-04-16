'use client';

import { Card } from '@/components/ui/card';
import type { StatsCounter } from '@/lib/server-api';

interface Props {
  title: string;
  counter: StatsCounter;
}

export function StatCard({ title, counter }: Props) {
  return (
    <Card className="p-5">
      <div className="text-sm text-muted-foreground">{title}</div>
      <div className="mt-1 text-3xl font-semibold">{counter.total.toLocaleString('uz-UZ')}</div>
      <div className="mt-3 grid grid-cols-3 gap-2 text-xs text-muted-foreground">
        <div>
          <div className="font-semibold text-foreground">{counter.today}</div>
          <div>Bugun</div>
        </div>
        <div>
          <div className="font-semibold text-foreground">{counter.last_7d}</div>
          <div>7 kun</div>
        </div>
        <div>
          <div className="font-semibold text-foreground">{counter.last_30d}</div>
          <div>30 kun</div>
        </div>
      </div>
    </Card>
  );
}
