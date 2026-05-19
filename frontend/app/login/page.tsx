"use client";

import { Suspense, useEffect } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { useAuth } from "@/components/AuthProvider";
import { GoogleLoginButton } from "@/components/GoogleLoginButton";

function LoginInner() {
  const { user, loading, config } = useAuth();
  const router = useRouter();
  const sp = useSearchParams();
  const next = sp.get("next") || "/families";

  useEffect(() => {
    if (!loading && user) {
      router.replace(next);
    }
  }, [loading, user, next, router]);

  useEffect(() => {
    if (config && !config.auth_enabled) {
      router.replace(next);
    }
  }, [config, next, router]);

  return (
    <div className="max-w-md mx-auto px-4 py-16">
      <div
        className="p-8 rounded-2xl text-center"
        style={{
          background: "white",
          border: "1px solid var(--border)",
          boxShadow: "0 4px 20px rgba(0,0,0,0.05)",
        }}
      >
        <div className="text-5xl mb-3">☯️</div>
        <h1 className="text-2xl font-bold mb-2 gradient-text">Tử Vi Gia Đình</h1>
        <p className="text-sm mb-6" style={{ color: "var(--muted)" }}>
          Đăng nhập để lưu hồ sơ gia đình và xem các bản phân tích đã lưu.
        </p>
        <div className="flex justify-center">
          <GoogleLoginButton onSuccess={() => router.replace(next)} />
        </div>
        <p className="text-xs mt-6" style={{ color: "var(--muted)" }}>
          Bằng việc đăng nhập, bạn đồng ý cho hệ thống lưu hồ sơ gia đình và
          các bản phân tích để bạn có thể xem lại sau này.
        </p>
      </div>
    </div>
  );
}

export default function LoginPage() {
  return (
    <Suspense fallback={<div className="text-center py-20">Đang tải...</div>}>
      <LoginInner />
    </Suspense>
  );
}
