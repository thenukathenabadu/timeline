import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'Timeline',
  description: 'A scrollable, zoomable timeline of world events built from multiple news sources.',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
