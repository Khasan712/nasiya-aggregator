import { LoginForm } from './login-form';

interface Props {
  searchParams: { next?: string };
}

export default function LoginPage({ searchParams }: Props) {
  return (
    <main className="flex min-h-screen items-center justify-center bg-muted/30">
      <div className="w-full max-w-sm space-y-6 rounded-lg border bg-card p-6 shadow-sm">
        <div>
          <h1 className="text-xl font-semibold">Nasiya Admin</h1>
          <p className="mt-1 text-sm text-muted-foreground">Kirish uchun ma'lumotlaringizni kiriting</p>
        </div>
        <LoginForm next={searchParams.next ?? '/admin/providers'} />
        <p className="text-center text-xs text-muted-foreground">
          Default: <code>admin@nasiya.uz</code> / <code>admin12345</code>
        </p>
      </div>
    </main>
  );
}
