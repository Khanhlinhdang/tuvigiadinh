"use client";

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
} from "react";
import { api, authStore, AuthUser, AuthConfig } from "@/lib/api";

interface AuthContextValue {
  user: AuthUser | null;
  config: AuthConfig | null;
  loading: boolean;
  loginWithGoogleCredential: (credential: string) => Promise<void>;
  logout: () => void;
  refreshMe: () => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [config, setConfig] = useState<AuthConfig | null>(null);
  const [loading, setLoading] = useState(true);

  const refreshMe = useCallback(async () => {
    const token = authStore.getToken();
    if (!token) {
      setUser(null);
      return;
    }
    try {
      const me = await api.getMe();
      setUser(me);
      authStore.setUser(me);
    } catch {
      authStore.clear();
      setUser(null);
    }
  }, []);

  useEffect(() => {
    let mounted = true;
    (async () => {
      try {
        const cfg = await api.getAuthConfig();
        if (!mounted) return;
        setConfig(cfg);
        // Hydrate user from localStorage immediately
        const cached = authStore.getUser();
        if (cached) setUser(cached);
        if (cfg.auth_enabled) {
          await refreshMe();
        }
      } catch {
        // ignore - backend might be down
      } finally {
        if (mounted) setLoading(false);
      }
    })();
    return () => {
      mounted = false;
    };
  }, [refreshMe]);

  const loginWithGoogleCredential = useCallback(async (credential: string) => {
    const res = await api.loginGoogle(credential);
    authStore.setToken(res.access_token);
    authStore.setUser(res.user);
    setUser(res.user);
  }, []);

  const logout = useCallback(() => {
    authStore.clear();
    setUser(null);
  }, []);

  const value = useMemo(
    () => ({ user, config, loading, loginWithGoogleCredential, logout, refreshMe }),
    [user, config, loading, loginWithGoogleCredential, logout, refreshMe]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used inside AuthProvider");
  return ctx;
}
