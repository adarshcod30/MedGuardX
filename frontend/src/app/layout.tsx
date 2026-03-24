import type { Metadata } from 'next';
import './globals.css';
import Sidebar from '@/components/Sidebar';

export const metadata: Metadata = {
  title: 'MedGuardX — Healthcare Data Protection',
  description: 'AI-powered healthcare data protection system with context-aware masking and compliance engine',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="bg-surface-50 min-h-screen">
        <Sidebar />
        <main className="ml-64 min-h-screen transition-all duration-300">
          <div className="max-w-7xl mx-auto p-8">
            {children}
          </div>
        </main>
      </body>
    </html>
  );
}
