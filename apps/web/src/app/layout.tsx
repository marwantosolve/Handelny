import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';

const inter = Inter({
  subsets: ['latin'],
  variable: '--font-inter',
});

export const metadata: Metadata = {
  title: 'Handelny — AI Customer Support Agents',
  description:
    'Create AI customer support agents from your documents, with grounded, cited answers.',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body
        className={`${inter.variable} font-sans bg-slate-50 text-slate-900 antialiased`}
      >
        {children}
      </body>
    </html>
  );
}
