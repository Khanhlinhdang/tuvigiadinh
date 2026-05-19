import type { Metadata } from "next";
import Link from "next/link";
import "./globals.css";
import { NavBar } from "@/components/NavBar";
import { AuthProvider } from "@/components/AuthProvider";
import { AuthGate } from "@/components/AuthGate";

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
        <AuthProvider>
          <NavBar />
          <main className="min-h-screen">
            <AuthGate>{children}</AuthGate>
          </main>
          <footer className="py-8 px-4 text-center text-sm" style={{ color: 'var(--muted)', borderTop: '1px solid var(--border)' }}>
            <p>🌟 Tử vi gia đình - Hệ thống phân tích quan hệ gia đình theo tri thức Đông phương</p>
            <p className="mt-1 opacity-60">Dành cho mục đích tham khảo và phát triển bản thân</p>
            <nav className="mt-4 flex flex-wrap justify-center gap-x-4 gap-y-2">
              <Link href="/dieu-khoan-dich-vu" className="hover:underline">
                Điều khoản dịch vụ
              </Link>
              <Link href="/chinh-sach-bao-mat" className="hover:underline">
                Chính sách bảo mật
              </Link>
              <Link href="/chinh-sach-thanh-toan" className="hover:underline">
                Chính sách thanh toán
              </Link>
              <Link href="/mien-tru-trach-nhiem" className="hover:underline">
                Miễn trừ trách nhiệm
              </Link>
            </nav>
          </footer>
        </AuthProvider>
      </body>
    </html>
  );
}
