import type { Metadata } from "next";
import "./globals.css";
import { NavBar } from "@/components/NavBar";

export const metadata: Metadata = {
  title: "Tử Vi Gia Đình - Family Intelligence System",
  description: "Hệ thống phân tích quan hệ và vận khí gia đình theo tri thức Đông phương",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="vi">
      <body>
        <NavBar />
        <main className="min-h-screen">
          {children}
        </main>
        <footer className="py-8 text-center text-sm" style={{ color: 'var(--muted)', borderTop: '1px solid var(--border)' }}>
          <p>🌟 Tử Vi Gia Đình - Hệ thống phân tích quan hệ gia đình theo tri thức Đông phương</p>
          <p className="mt-1 opacity-60">Dành cho mục đích tham khảo và phát triển bản thân</p>
        </footer>
      </body>
    </html>
  );
}
