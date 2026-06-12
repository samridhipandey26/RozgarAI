// Server Component — must NOT contain event handlers
import type { Metadata } from 'next';
import './globals.css';
import NavBar from '@/components/NavBar';

export const metadata: Metadata = {
  title: 'RozgarAI — काम खोजो। काम दो। आज।',
  description: 'Voice-first Hindi job platform for blue-collar workers in Uttar Pradesh.',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="hi">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link
          href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap"
          rel="stylesheet"
        />
      </head>
      <body style={{ fontFamily: "'Inter', system-ui, sans-serif", backgroundColor: '#0D0D0D', color: '#ffffff', margin: 0 }}>
        {/* NavBar is a Client Component — handles hover events */}
        <NavBar />
        <main style={{ minHeight: 'calc(100vh - 64px)' }}>
          {children}
        </main>
      </body>
    </html>
  );
}
