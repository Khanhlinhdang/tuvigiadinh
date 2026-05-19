"use client";

import { useEffect, useRef, useState } from "react";
import { useAuth } from "@/components/AuthProvider";

declare global {
  interface Window {
    google?: {
      accounts: {
        id: {
          initialize: (config: {
            client_id: string;
            callback: (response: { credential: string }) => void;
            ux_mode?: "popup" | "redirect";
            auto_select?: boolean;
          }) => void;
          renderButton: (
            el: HTMLElement,
            options: { theme?: string; size?: string; width?: number; text?: string }
          ) => void;
          prompt: () => void;
        };
      };
    };
  }
}

interface Props {
  onSuccess?: () => void;
  // When client id missing, allow dev login by pasting token manually
  allowDevPaste?: boolean;
}

/**
 * Renders the official Google Sign-In button. Falls back to a manual
 * paste box when no Google client id is configured (development only).
 */
export function GoogleLoginButton({ onSuccess, allowDevPaste = true }: Props) {
  const { config, loginWithGoogleCredential } = useAuth();
  const btnRef = useRef<HTMLDivElement>(null);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [scriptReady, setScriptReady] = useState(false);

  const clientId = config?.google_client_id || "";

  // Load the GSI script once
  useEffect(() => {
    if (!clientId) return;
    if (typeof window === "undefined") return;
    if (window.google?.accounts?.id) {
      queueMicrotask(() => setScriptReady(true));
      return;
    }
    const existing = document.querySelector<HTMLScriptElement>(
      'script[src="https://accounts.google.com/gsi/client"]'
    );
    if (existing) {
      existing.addEventListener("load", () => setScriptReady(true));
      return;
    }
    const s = document.createElement("script");
    s.src = "https://accounts.google.com/gsi/client";
    s.async = true;
    s.defer = true;
    s.onload = () => setScriptReady(true);
    document.head.appendChild(s);
  }, [clientId]);

  // Initialize & render button when script is ready
  useEffect(() => {
    if (!clientId || !scriptReady) return;
    if (!window.google?.accounts?.id || !btnRef.current) return;

    window.google.accounts.id.initialize({
      client_id: clientId,
      callback: async (resp) => {
        if (!resp.credential) return;
        setBusy(true);
        setError("");
        try {
          await loginWithGoogleCredential(resp.credential);
          onSuccess?.();
        } catch (e: unknown) {
          const msg = e instanceof Error ? e.message : "Đăng nhập thất bại";
          setError(msg);
        } finally {
          setBusy(false);
        }
      },
      ux_mode: "popup",
    });

    btnRef.current.innerHTML = "";
    window.google.accounts.id.renderButton(btnRef.current, {
      theme: "outline",
      size: "large",
      width: 280,
      text: "signin_with",
    });
  }, [clientId, scriptReady, loginWithGoogleCredential, onSuccess]);

  if (!clientId) {
    if (!allowDevPaste) {
      return (
        <div className="text-sm" style={{ color: "var(--muted)" }}>
          Google Client ID chưa được cấu hình (GOOGLE_CLIENT_ID ở backend).
        </div>
      );
    }
    return (
      <DevPasteFallback
        onSubmit={async (cred) => {
          setBusy(true);
          setError("");
          try {
            await loginWithGoogleCredential(cred);
            onSuccess?.();
          } catch (e: unknown) {
            setError(e instanceof Error ? e.message : "Đăng nhập thất bại");
          } finally {
            setBusy(false);
          }
        }}
        busy={busy}
        error={error}
      />
    );
  }

  return (
    <div className="flex flex-col items-center gap-3">
      <div ref={btnRef} />
      {busy && <p className="text-xs" style={{ color: "var(--muted)" }}>Đang đăng nhập...</p>}
      {error && <p className="text-xs text-red-600">{error}</p>}
    </div>
  );
}

function DevPasteFallback({
  onSubmit,
  busy,
  error,
}: {
  onSubmit: (cred: string) => void;
  busy: boolean;
  error: string;
}) {
  const [cred, setCred] = useState("");
  return (
    <div className="w-full max-w-md">
      <div
        className="p-3 rounded-lg text-xs mb-3"
        style={{ background: "#fef3c7", color: "#92400e" }}
      >
        ⚠️ Chưa cấu hình <code>GOOGLE_CLIENT_ID</code> ở backend -
        chế độ phát triển: dán Google ID token thủ công để đăng nhập.
      </div>
      <textarea
        value={cred}
        onChange={(e) => setCred(e.target.value)}
        placeholder="Google ID token (JWT)"
        className="w-full p-3 rounded-lg text-xs font-mono"
        style={{ border: "1px solid var(--border)", outline: "none", minHeight: 80 }}
      />
      <button
        disabled={!cred.trim() || busy}
        onClick={() => onSubmit(cred.trim())}
        className="mt-2 px-4 py-2 rounded-lg text-white text-sm font-semibold disabled:opacity-50"
        style={{ background: "linear-gradient(135deg, #8b5cf6, #ec4899)" }}
      >
        {busy ? "Đang đăng nhập..." : "Đăng nhập"}
      </button>
      {error && <p className="mt-2 text-xs text-red-600">{error}</p>}
    </div>
  );
}
