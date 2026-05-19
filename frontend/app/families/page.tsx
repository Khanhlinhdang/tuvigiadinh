"use client";

import { useState, useEffect, useCallback } from "react";
import Link from "next/link";
import { api, Family } from "@/lib/api";

export default function FamiliesPage() {
  const [families, setFamilies] = useState<Family[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({ name: "", description: "" });
  const [creating, setCreating] = useState(false);

  const loadFamilies = useCallback(async () => {
    try {
      const data = await api.getFamilies();
      setFamilies(data);
    } catch (e: unknown) {
      setError("Không thể kết nối đến server. Hãy đảm bảo backend đang chạy.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    // Defer the async load so React's compiler does not treat the resulting
    // state updates as synchronous effect work.
    const timer = window.setTimeout(() => {
      loadFamilies();
    }, 0);
    return () => window.clearTimeout(timer);
  }, [loadFamilies]);

  async function createFamily(e: React.FormEvent) {
    e.preventDefault();
    if (!formData.name.trim()) return;
    setCreating(true);
    try {
      const newFamily = await api.createFamily(formData);
      setFamilies([...families, newFamily]);
      setFormData({ name: "", description: "" });
      setShowForm(false);
    } catch (e: unknown) {
      setError("Không thể tạo gia đình. Thử lại sau.");
    } finally {
      setCreating(false);
    }
  }

  async function deleteFamily(id: number) {
    if (!confirm("Bạn có chắc muốn xóa gia đình này?")) return;
    try {
      await api.deleteFamily(id);
      setFamilies(families.filter((f) => f.id !== id));
    } catch (e: unknown) {
      setError("Không thể xóa gia đình.");
    }
  }

  const hanh_colors: Record<string, string> = {
    Kim: "#a855f7",
    Mộc: "#22c55e",
    Hỏa: "#ef4444",
    Thổ: "#f59e0b",
    Thủy: "#3b82f6",
  };

  return (
    <div className="max-w-6xl mx-auto px-4 py-8">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold gradient-text">Hồ Sơ Gia Đình</h1>
          <p className="mt-1" style={{ color: "var(--muted)" }}>
            Quản lý và phân tích các gia đình của bạn
          </p>
        </div>
        <button
          onClick={() => setShowForm(true)}
          className="px-6 py-3 rounded-xl text-white font-semibold transition-transform hover:scale-105"
          style={{ background: "linear-gradient(135deg, #8b5cf6, #ec4899)" }}
        >
          + Tạo Gia Đình Mới
        </button>
      </div>

      {error && (
        <div
          className="mb-6 p-4 rounded-xl text-sm"
          style={{ background: "#fee2e2", color: "#dc2626", border: "1px solid #fca5a5" }}
        >
          ⚠️ {error}
          <button
            onClick={() => setError("")}
            className="ml-2 underline"
          >
            Đóng
          </button>
        </div>
      )}

      {/* Create Family Form */}
      {showForm && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center p-4"
          style={{ background: "rgba(0,0,0,0.5)" }}
        >
          <div
            className="w-full max-w-md rounded-2xl p-6 fade-in"
            style={{ background: "white" }}
          >
            <h2 className="text-xl font-bold mb-4">Tạo Gia Đình Mới</h2>
            <form onSubmit={createFamily} className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-1">
                  Tên gia đình *
                </label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  placeholder="Ví dụ: Gia đình Nguyễn"
                  className="w-full px-4 py-3 rounded-xl border text-sm outline-none focus:ring-2"
                  style={{
                    border: "1px solid var(--border)",
                    outline: "none",
                  }}
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">
                  Mô tả (tùy chọn)
                </label>
                <textarea
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  placeholder="Ghi chú về gia đình..."
                  rows={3}
                  className="w-full px-4 py-3 rounded-xl border text-sm"
                  style={{ border: "1px solid var(--border)", outline: "none" }}
                />
              </div>
              <div className="flex gap-3 pt-2">
                <button
                  type="submit"
                  disabled={creating}
                  className="flex-1 py-3 rounded-xl text-white font-semibold"
                  style={{ background: "linear-gradient(135deg, #8b5cf6, #ec4899)" }}
                >
                  {creating ? "Đang tạo..." : "Tạo Gia Đình"}
                </button>
                <button
                  type="button"
                  onClick={() => setShowForm(false)}
                  className="px-6 py-3 rounded-xl font-semibold"
                  style={{ background: "#f3f4f6" }}
                >
                  Hủy
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Loading */}
      {loading && (
        <div className="text-center py-20">
          <div className="text-4xl mb-4 pulse-soft">☯️</div>
          <p style={{ color: "var(--muted)" }}>Đang tải...</p>
        </div>
      )}

      {/* Empty state */}
      {!loading && families.length === 0 && (
        <div
          className="text-center py-20 rounded-2xl"
          style={{ background: "white", border: "2px dashed var(--border)" }}
        >
          <div className="text-5xl mb-4">👨‍👩‍👧‍👦</div>
          <h3 className="text-xl font-bold mb-2">Chưa có hồ sơ gia đình nào</h3>
          <p className="mb-6" style={{ color: "var(--muted)" }}>
            Tạo hồ sơ đầu tiên để bắt đầu phân tích
          </p>
          <button
            onClick={() => setShowForm(true)}
            className="px-8 py-3 rounded-xl text-white font-semibold"
            style={{ background: "linear-gradient(135deg, #8b5cf6, #ec4899)" }}
          >
            + Tạo Gia Đình Đầu Tiên
          </button>
        </div>
      )}

      {/* Families grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {families.map((family) => (
          <div
            key={family.id}
            className="rounded-2xl p-6 card-hover"
            style={{
              background: "white",
              border: "1px solid var(--border)",
              boxShadow: "0 2px 8px rgba(0,0,0,0.05)",
            }}
          >
            <div className="flex items-start justify-between mb-4">
              <div>
                <h3 className="font-bold text-lg">{family.name}</h3>
                {family.description && (
                  <p className="text-sm mt-1" style={{ color: "var(--muted)" }}>
                    {family.description}
                  </p>
                )}
              </div>
              <button
                onClick={() => deleteFamily(family.id)}
                className="text-gray-400 hover:text-red-500 text-lg p-1"
                title="Xóa gia đình"
              >
                🗑️
              </button>
            </div>

            {/* Members preview */}
            <div className="mb-4">
              <div className="flex flex-wrap gap-2">
                {family.members.slice(0, 4).map((member) => (
                  <div
                    key={member.id}
                    className="flex items-center gap-1 px-2 py-1 rounded-lg text-xs"
                    style={{
                      background: `${hanh_colors[member.ngu_hanh || ""] || "#8b5cf6"}15`,
                      color: hanh_colors[member.ngu_hanh || ""] || "#8b5cf6",
                      border: `1px solid ${hanh_colors[member.ngu_hanh || ""] || "#8b5cf6"}30`,
                    }}
                  >
                    <span>{member.gender === "nam" ? "👨" : "👩"}</span>
                    <span>{member.name}</span>
                    {member.thien_can && (
                      <span className="opacity-70">
                        {member.thien_can} {member.dia_chi}
                      </span>
                    )}
                  </div>
                ))}
                {family.members.length > 4 && (
                  <div
                    className="px-2 py-1 rounded-lg text-xs"
                    style={{ background: "#f3f4f6", color: "var(--muted)" }}
                  >
                    +{family.members.length - 4} khác
                  </div>
                )}
              </div>
              {family.members.length === 0 && (
                <p className="text-sm" style={{ color: "var(--muted)" }}>
                  Chưa có thành viên
                </p>
              )}
            </div>

            <div className="flex items-center justify-between">
              <span className="text-xs" style={{ color: "var(--muted)" }}>
                {family.members.length} thành viên
              </span>
              <Link
                href={`/families/${family.id}`}
                className="px-4 py-2 rounded-lg text-sm font-semibold text-white transition-transform hover:scale-105"
                style={{ background: "linear-gradient(135deg, #8b5cf6, #ec4899)" }}
              >
                Xem Chi Tiết →
              </Link>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
