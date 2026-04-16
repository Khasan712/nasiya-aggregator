import type { Metadata } from 'next';
import { SonnerProvider } from '@/components/sonner-provider';
import './globals.css';

export const metadata: Metadata = {
  title: 'Nasiya Aggregator — Admin',
  description: "O'zbekistondagi nasiya xizmatlari ma'muriy paneli",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="uz">
      <body className="min-h-screen antialiased">
        {children}
        <SonnerProvider />
      </body>
    </html>
  );
}
