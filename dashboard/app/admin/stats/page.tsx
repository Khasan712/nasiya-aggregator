import { serverApi, type StatsOverview } from '@/lib/server-api';
import { StatCard } from './_components/stat-card';
import {
  AmountBucketsChart,
  AmountSummaryCard,
  DailyChart,
  EventTypesChart,
  FunnelChart,
  HourlyChart,
  LanguagesChart,
  TopProductsChart,
  TopProvidersChart,
} from './_components/charts';

export const dynamic = 'force-dynamic';

export default async function StatsPage() {
  let stats: StatsOverview | null = null;
  let error: string | null = null;
  try {
    stats = await serverApi.stats.overview();
  } catch (e) {
    error = (e as Error).message;
  }

  if (error || !stats) {
    return (
      <div className="space-y-4">
        <h1 className="text-2xl font-bold">Statistika</h1>
        <div className="rounded-md border border-red-300 bg-red-50 p-4 text-sm text-red-700">
          Backendga ulanib bo'lmadi: <code>{error}</code>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <header>
        <h1 className="text-2xl font-bold">Statistika</h1>
        <p className="text-sm text-muted-foreground">
          Bot va dashboard ma'lumotlari real vaqtda yangilanadi.
        </p>
      </header>

      <div className="grid gap-4 md:grid-cols-3">
        <StatCard title="Foydalanuvchilar" counter={stats.users} />
        <StatCard title="Bot foydalanuvchilari" counter={stats.bot_users} />
        <StatCard title="Eventlar" counter={stats.events} />
      </div>

      <DailyChart data={stats.daily_activity} />

      <div className="grid gap-4 md:grid-cols-2">
        <HourlyChart data={stats.hourly_activity} />
        <FunnelChart data={stats.funnel} />
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        <TopProductsChart data={stats.top_products} />
        <TopProvidersChart data={stats.top_providers} />
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        <AmountBucketsChart data={stats.amount_buckets} />
        <AmountSummaryCard summary={stats.amount_summary} />
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        <EventTypesChart data={stats.event_types} />
        <LanguagesChart data={stats.languages} />
      </div>
    </div>
  );
}
