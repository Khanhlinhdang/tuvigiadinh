"use client";

import { usePathname, useRouter } from "next/navigation";
import { useEffect } from "react";
import { useAuth } from "@/components/AuthProvider";

const PUBLIC_PATHS = [
  "/login",
  "/dieu-khoan-dich-vu",
  "/chinh-sach-bao-mat",
  "/chinh-sach-thanh-toan",
  "/mien-tru-trach-nhiem",
];

export function AuthGate({ children }: { children: React.ReactNode }) {
  const { user, loading, config } = useAuth();
  const pathname = usePathname();
  const router = useRouter();

  const isPublic = PUBLIC_PATHS.some(
    (p) => pathname === p || pathname.startsWith(`${p}/`)
  );
  const authEnabled = config?.auth_enabled !== false; // default: enabled until config loaded

  useEffect(() => {
    if (loading) return;
    if (!authEnabled) return;
    if (!user && !isPublic) {
      const next = encodeURIComponent(pathname || "/");
      router.replace(`/login?next=${next}`);
    }
  }, [loading, user, isPublic, pathname, router, authEnabled]);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="text-center">
          <div className="text-5xl mb-3 pulse-soft">☯️</div>
          <p style={{ color: "var(--muted)" }}>Đang tải...</p>
        </div>
      </div>
    );
  }

  if (authEnabled && !user && !isPublic) {
    return null; // redirecting
  }

  return <>{children}</>;
}
