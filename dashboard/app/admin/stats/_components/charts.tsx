'use client';

import {
  AreaChart,
  BarChart,
  Card as TremorCard,
  DonutChart,
  Title,
  Subtitle,
  Legend,
} from '@tremor/react';
import type {
  StatsAmountBucket,
  StatsDailyPoint,
  StatsEventTypeRow,
  StatsFunnelStep,
  StatsHourlyPoint,
  StatsTopProduct,
  StatsTopProvider,
} from '@/lib/server-api';

const EVENT_TYPE_LABEL: Record<string, string> = {
  start: 'Boshlash',
  view_list: "Ro'yxatni ko'rish",
  view_product: "Mahsulot ko'rish",
  view_provider: "Provayder ko'rish",
  click_official_link: 'Rasmiy link',
  search_by_amount: 'Summa qidirish',
  compare: 'Solishtirish',
  language_change: "Til o'zgartirish",
  feedback: 'Fikr-mulohaza',
};

const LANG_LABEL: Record<string, string> = {
  uz: "🇺🇿 O'zbek",
  ru: '🇷🇺 Русский',
  en: '🇬🇧 English',
};

const intFmt = (v: number) => v.toLocaleString('uz-UZ');
const uzsFmt = (v: number) =>
  v >= 1_000_000 ? `${(v / 1_000_000).toFixed(1)}M` : v.toLocaleString('uz-UZ');

/** Strip parenthetical clauses and clamp length so chart Y-axis labels fit on one line. */
function shortName(name: string, max = 26): string {
  const cleaned = name
    .replace(/\s*\([^)]*\)\s*/g, ' ') // drop "(Sanoat Qurilish Bank)"
    .replace(/\s+/g, ' ')
    .trim();
  if (cleaned.length <= max) return cleaned;
  return cleaned.slice(0, max - 1).trim() + '…';
}

// ──────────────────────────────────────────────────────────────────────────

export function DailyChart({ data }: { data: StatsDailyPoint[] }) {
  const formatted = data.map((d) => ({
    Kun: new Date(d.day).toLocaleDateString('uz-UZ', { month: 'short', day: 'numeric' }),
    Eventlar: d.events,
    "Aktiv foydalanuvchilar": d.unique_users,
  }));
  return (
    <TremorCard>
      <Title>Kunlik faollik (oxirgi 30 kun)</Title>
      <Subtitle>Eventlar va aktiv foydalanuvchilar</Subtitle>
      <AreaChart
        className="mt-4 h-72"
        data={formatted}
        index="Kun"
        categories={['Eventlar', 'Aktiv foydalanuvchilar']}
        colors={['blue', 'emerald']}
        showLegend
        showGridLines
        valueFormatter={intFmt}
      />
    </TremorCard>
  );
}

export function HourlyChart({ data }: { data: StatsHourlyPoint[] }) {
  const rows = data.map((d) => ({
    Soat: `${String(d.hour).padStart(2, '0')}:00`,
    Eventlar: d.events,
  }));
  return (
    <TremorCard>
      <Title>Kun ichidagi faollik</Title>
      <Subtitle>Soat bo'yicha eventlar (Asia/Tashkent vaqti)</Subtitle>
      <BarChart
        className="mt-4 h-64"
        data={rows}
        index="Soat"
        categories={['Eventlar']}
        colors={['cyan']}
        showLegend={false}
        valueFormatter={intFmt}
      />
    </TremorCard>
  );
}

export function TopProductsChart({ data }: { data: StatsTopProduct[] }) {
  const rows = data.map((d) => ({
    Mahsulot: shortName(d.name_uz, 28),
    "Ko'rishlar": d.views,
  }));
  return (
    <TremorCard>
      <Title>Top mahsulotlar</Title>
      <Subtitle>Eng ko'p ko'rilgan nasiya xizmatlari</Subtitle>
      <BarChart
        className="mt-4 h-80"
        data={rows}
        index="Mahsulot"
        categories={["Ko'rishlar"]}
        colors={['blue']}
        layout="vertical"
        yAxisWidth={170}
        showLegend={false}
        valueFormatter={intFmt}
      />
    </TremorCard>
  );
}

export function TopProvidersChart({ data }: { data: StatsTopProvider[] }) {
  const rows = data.map((d) => ({
    Provayder: shortName(d.name_uz, 24),
    "Ko'rishlar": d.views,
  }));
  return (
    <TremorCard>
      <Title>Top provayderlar</Title>
      <Subtitle>Eng faol brendlar (mahsulot ko'rishlari yig'indisi)</Subtitle>
      <BarChart
        className="mt-4 h-80"
        data={rows}
        index="Provayder"
        categories={["Ko'rishlar"]}
        colors={['amber']}
        layout="vertical"
        yAxisWidth={150}
        showLegend={false}
        valueFormatter={intFmt}
      />
    </TremorCard>
  );
}

export function AmountBucketsChart({ data }: { data: StatsAmountBucket[] }) {
  const rows = data.map((d) => ({ Summa: d.bucket_label, Qidiruvlar: d.count }));
  return (
    <TremorCard>
      <Title>Qidirilgan summalar (UZS)</Title>
      <Subtitle>Foydalanuvchilar qancha summa so'raydi?</Subtitle>
      <BarChart
        className="mt-4 h-64"
        data={rows}
        index="Summa"
        categories={['Qidiruvlar']}
        colors={['emerald']}
        showLegend={false}
        valueFormatter={intFmt}
      />
    </TremorCard>
  );
}

export function EventTypesChart({ data }: { data: StatsEventTypeRow[] }) {
  const rows = data.map((d) => ({
    Event: shortName(EVENT_TYPE_LABEL[d.event_type] ?? d.event_type, 24),
    Soni: d.count,
  }));
  return (
    <TremorCard>
      <Title>Event turlari</Title>
      <Subtitle>Bot ichidagi harakatlar taqsimoti</Subtitle>
      <BarChart
        className="mt-4 h-72"
        data={rows}
        index="Event"
        categories={['Soni']}
        colors={['fuchsia']}
        layout="vertical"
        yAxisWidth={150}
        showLegend={false}
        valueFormatter={intFmt}
      />
    </TremorCard>
  );
}

export function LanguagesChart({ data }: { data: StatsEventTypeRow[] }) {
  const rows = data.map((d) => ({
    name: LANG_LABEL[d.event_type] ?? d.event_type,
    count: d.count,
  }));
  const total = rows.reduce((s, r) => s + r.count, 0);
  const colors = ['blue', 'emerald', 'rose'] as const;
  return (
    <TremorCard>
      <Title>Tillar</Title>
      <Subtitle>Bot foydalanuvchilari tillari ({total})</Subtitle>
      <DonutChart
        className="mt-4 h-56"
        data={rows}
        category="count"
        index="name"
        colors={[...colors]}
        valueFormatter={intFmt}
      />
      <Legend
        className="mt-3"
        categories={rows.map((r) => r.name)}
        colors={[...colors]}
      />
    </TremorCard>
  );
}

export function FunnelChart({ data }: { data: StatsFunnelStep[] }) {
  const top = data[0]?.count || 0;
  const colors = ['bg-blue-500', 'bg-indigo-500', 'bg-violet-500', 'bg-fuchsia-500'];
  return (
    <TremorCard>
      <Title>Foydalanish bosqichlari</Title>
      <Subtitle>
        Botga kirgan foydalanuvchilarning qancha qismi har bir bosqichgacha yetib bordi.
        Foiz — birinchi bosqichdan ulush.
      </Subtitle>
      <div className="mt-6 space-y-3">
        {data.map((step, i) => {
          // Width is conversion % from step #1, so the bars naturally taper.
          const conversion = top > 0 ? Math.round((step.count / top) * 100) : 0;
          return (
            <div key={step.name}>
              <div className="flex items-baseline justify-between text-sm">
                <span className="font-medium">{step.name}</span>
                <span className="tabular-nums text-muted-foreground">
                  {step.count.toLocaleString('uz-UZ')} foydalanuvchi · {conversion}%
                </span>
              </div>
              <div className="mt-1 h-6 rounded-md bg-muted/50">
                <div
                  className={`h-6 rounded-md ${colors[i % colors.length]}`}
                  style={{ width: `${Math.max(conversion, 4)}%` }}
                />
              </div>
            </div>
          );
        })}
      </div>
    </TremorCard>
  );
}

export function AmountSummaryCard({
  summary,
}: {
  summary: { searches: number; avg_uzs: number; median_uzs: number; max_uzs: number };
}) {
  return (
    <TremorCard>
      <Title>Qidiruv summalar yakuni</Title>
      <Subtitle>Foydalanuvchilar so'ragan summalar statistikasi</Subtitle>
      <div className="mt-4 grid grid-cols-2 gap-4">
        <Metric label="Qidiruvlar soni" value={intFmt(summary.searches)} />
        <Metric label="O'rtacha" value={uzsFmt(summary.avg_uzs) + ' UZS'} />
        <Metric label="Mediana" value={uzsFmt(summary.median_uzs) + ' UZS'} />
        <Metric label="Maksimal" value={uzsFmt(summary.max_uzs) + ' UZS'} />
      </div>
    </TremorCard>
  );
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <div className="text-xs text-muted-foreground">{label}</div>
      <div className="mt-1 text-xl font-semibold tabular-nums">{value}</div>
    </div>
  );
}
