import Link from 'next/link';

export default function HomePage() {
  return (
    <main className="container mx-auto py-12">
      <div className="mx-auto max-w-3xl space-y-6">
        <header className="space-y-2">
          <h1 className="text-3xl font-bold tracking-tight">Nasiya Aggregator</h1>
          <p className="text-muted-foreground">
            O'zbekistondagi nasiya (BNPL) xizmatlari uchun rasmiy ma'lumot agregatori — admin
            paneli.
          </p>
        </header>

        <section className="rounded-lg border bg-card p-6">
          <h2 className="text-lg font-semibold">Boshlash</h2>
          <ol className="mt-3 list-decimal space-y-1 pl-5 text-sm text-muted-foreground">
            <li>
              Backend ishlayotganini tekshiring:{' '}
              <code className="rounded bg-muted px-1.5 py-0.5">make backend</code>
            </li>
            <li>
              <Link className="text-primary underline" href="/admin/providers">
                Provayderlar
              </Link>{' '}
              sahifasiga o'ting va seed ma'lumotlarni ko'ring
            </li>
            <li>
              Statistikani{' '}
              <Link className="text-primary underline" href="/admin/stats">
                /admin/stats
              </Link>{' '}
              da kuzating
            </li>
          </ol>
        </section>

        <section className="rounded-lg border bg-card p-6 text-sm">
          <h2 className="text-lg font-semibold">API status</h2>
          <p className="mt-2 text-muted-foreground">
            Backend: <code className="rounded bg-muted px-1.5 py-0.5">/api/backend/health</code>
          </p>
        </section>
      </div>
    </main>
  );
}
