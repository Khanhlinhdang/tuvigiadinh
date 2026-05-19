"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

export function NavBar() {
  const pathname = usePathname();

  const links = [
    { href: "/", label: "Trang Chủ" },
    { href: "/families", label: "Hồ Sơ Gia Đình" },
  ];

  return (
    <nav
      className="sticky top-0 z-50"
      style={{
        background: "rgba(255,255,255,0.95)",
        backdropFilter: "blur(10px)",
        borderBottom: "1px solid var(--border)",
        boxShadow: "0 1px 8px rgba(0,0,0,0.06)",
      }}
    >
      <div className="max-w-6xl mx-auto px-4 py-3 flex items-center justify-between">
        <Link href="/" className="flex items-center gap-2">
          <span className="text-2xl">☯️</span>
          <div>
            <div className="font-bold text-lg leading-tight gradient-text">
              Tử Vi Gia Đình
            </div>
            <div className="text-xs" style={{ color: "var(--muted)" }}>
              Family Intelligence System
            </div>
          </div>
        </Link>

        <div className="flex items-center gap-1">
          {links.map((link) => (
            <Link
              key={link.href}
              href={link.href}
              className="px-4 py-2 rounded-lg text-sm font-medium transition-all"
              style={{
                background:
                  pathname === link.href
                    ? "linear-gradient(135deg, #8b5cf6, #ec4899)"
                    : "transparent",
                color: pathname === link.href ? "white" : "var(--foreground)",
              }}
            >
              {link.label}
            </Link>
          ))}
          <Link
            href="/families"
            className="ml-2 px-4 py-2 rounded-lg text-sm font-medium text-white"
            style={{
              background: "linear-gradient(135deg, #8b5cf6, #ec4899)",
            }}
          >
            + Tạo Gia Đình
          </Link>
        </div>
      </div>
    </nav>
  );
}
