"use client";

import { useState, useEffect, use } from "react";
import Link from "next/link";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { api, Family, FamilyAnalysis, FamilyForecast, FamilyMember, MemberForecast, PairCompatibility, SavedAnalysisSummary, SavedAnalysisDetail } from "@/lib/api";
import { RadarChart, Radar, PolarGrid, PolarAngleAxis, ResponsiveContainer, Tooltip } from "recharts";

const HANH_COLORS: Record<string, string> = {
  Kim: "#a855f7",
  Mộc: "#22c55e",
  Hỏa: "#ef4444",
  Thổ: "#f59e0b",
  Thủy: "#3b82f6",
};

const ROLES = ["chồng", "vợ", "con", "cha", "mẹ", "anh", "chị", "em"];
const HOURS = ["Tý", "Sửu", "Dần", "Mão", "Thìn", "Tị", "Ngọ", "Mùi", "Thân", "Dậu", "Tuất", "Hợi"];

type Tab = "members" | "analysis" | "forecast" | "chat" | "saved";

export default function FamilyDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const familyId = parseInt(id);

  const [family, setFamily] = useState<Family | null>(null);
  const [analysis, setAnalysis] = useState<FamilyAnalysis | null>(null);
  const [forecast, setForecast] = useState<FamilyForecast | null>(null);
  const [loading, setLoading] = useState(true);
  const [analysisLoading, setAnalysisLoading] = useState(false);
  const [forecastLoading, setForecastLoading] = useState(false);
  const [activeTab, setActiveTab] = useState<Tab>("members");
  const [showAddMember, setShowAddMember] = useState(false);
  const [forecastYear, setForecastYear] = useState(new Date().getFullYear());
  const [chatMessages, setChatMessages] = useState<Array<{ role: "user" | "ai"; content: string }>>([]);
  const [chatInput, setChatInput] = useState("");
  const [chatLoading, setChatLoading] = useState(false);
  const [error, setError] = useState("");
  const [editingMember, setEditingMember] = useState<FamilyMember | null>(null);
  const [showEditFamily, setShowEditFamily] = useState(false);
  const [savedList, setSavedList] = useState<SavedAnalysisSummary[]>([]);
  const [savedDetail, setSavedDetail] = useState<SavedAnalysisDetail | null>(null);
  const [savingAnalysis, setSavingAnalysis] = useState(false);
  const [analysisProgress, setAnalysisProgress] = useState(0);

  const [memberForm, setMemberForm] = useState({
    name: "",
    role: "con",
    gender: "nam",
    occupation: "",
    birth_year: 1990,
    birth_month: "",
    birth_day: "",
    birth_calendar: "solar" as "solar" | "lunar",
    is_leap_month: false,
  });

  useEffect(() => {
    loadFamily();
  }, [familyId]);

  async function loadFamily() {
    try {
      const data = await api.getFamily(familyId);
      setFamily(data);
    } catch (e: unknown) {
      setError("Không tìm thấy gia đình.");
    } finally {
      setLoading(false);
    }
  }

  async function addMember(e: React.FormEvent) {
    e.preventDefault();
    try {
      const newMember = await api.addMember(familyId, {
        name: memberForm.name,
        role: memberForm.role,
        gender: memberForm.gender,
        occupation: memberForm.occupation || undefined,
        birth_year: memberForm.birth_year,
        birth_month: memberForm.birth_month ? parseInt(memberForm.birth_month) : undefined,
        birth_day: memberForm.birth_day ? parseInt(memberForm.birth_day) : undefined,
        birth_calendar: memberForm.birth_calendar,
        is_leap_month: memberForm.is_leap_month,
      });
      setFamily((prev) =>
        prev ? { ...prev, members: [...prev.members, newMember] } : prev
      );
      setShowAddMember(false);
      setMemberForm({ name: "", role: "con", gender: "nam", occupation: "", birth_year: 1990, birth_month: "", birth_day: "", birth_calendar: "solar", is_leap_month: false });
      setAnalysis(null);
    } catch (e: unknown) {
      setError("Không thể thêm thành viên.");
    }
  }

  async function saveMemberEdits(memberId: number, patch: Partial<{ name: string; role: string; gender: string; occupation: string; birth_year: number; birth_month: number; birth_day: number; birth_calendar: 'solar' | 'lunar'; is_leap_month: boolean }>) {
    try {
      const updated = await api.updateMember(familyId, memberId, patch);
      setFamily((prev) => prev ? { ...prev, members: prev.members.map((m) => m.id === memberId ? updated : m) } : prev);
      setAnalysis(null);
      setEditingMember(null);
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : "Lỗi cập nhật";
      setError(`Không thể cập nhật: ${msg}`);
    }
  }

  async function saveFamilyEdits(patch: { name?: string; description?: string }) {
    try {
      const updated = await api.updateFamily(familyId, patch);
      setFamily((prev) => prev ? { ...prev, name: updated.name, description: updated.description } : prev);
      setShowEditFamily(false);
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : "Lỗi cập nhật";
      setError(`Không thể cập nhật gia đình: ${msg}`);
    }
  }

  async function deleteMember(memberId: number) {
    if (!confirm("Xóa thành viên này?")) return;
    try {
      await api.deleteMember(familyId, memberId);
      setFamily((prev) =>
        prev ? { ...prev, members: prev.members.filter((m) => m.id !== memberId) } : prev
      );
      setAnalysis(null);
    } catch (e: unknown) {
      setError("Không thể xóa thành viên.");
    }
  }

  async function loadAnalysis() {
    if (analysis) return;
    setAnalysisLoading(true);
    setAnalysisProgress(5);
    // Simulated progress while waiting for backend - backend doesn't
    // stream progress, so we ease toward 90% then snap to 100% on done.
    const tick = setInterval(() => {
      setAnalysisProgress((p) => {
        if (p >= 90) return p;
        // Slower as we approach 90%
        const delta = p < 40 ? 6 : p < 70 ? 3 : 1;
        return Math.min(90, p + delta);
      });
    }, 350);
    try {
      const data = await api.getFamilyAnalysis(familyId);
      setAnalysisProgress(100);
      setAnalysis(data);
    } catch (e: unknown) {
      const errMsg = e instanceof Error ? e.message : "Lỗi không xác định";
      setError(`Không thể phân tích: ${errMsg}`);
    } finally {
      clearInterval(tick);
      // small delay so the user sees the bar reach 100%
      setTimeout(() => setAnalysisLoading(false), 250);
    }
  }

  async function loadSaved() {
    try {
      const list = await api.listSavedAnalyses(familyId);
      setSavedList(list);
    } catch {
      // ignore
    }
  }

  async function saveCurrentAnalysis() {
    setSavingAnalysis(true);
    try {
      const title = prompt("Đặt tên cho bản phân tích này:", `Phân tích ${new Date().toLocaleDateString("vi-VN")}`);
      if (title === null) {
        setSavingAnalysis(false);
        return;
      }
      const saved = await api.saveAnalysis(familyId, { title: title || undefined });
      await loadSaved();
      alert(`Đã lưu bản phân tích "${saved.title}" thành công.`);
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : "Lỗi";
      setError(`Không thể lưu phân tích: ${msg}`);
    } finally {
      setSavingAnalysis(false);
    }
  }

  async function openSaved(id: number) {
    try {
      const detail = await api.getSavedAnalysis(id);
      setSavedDetail(detail);
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : "Lỗi";
      setError(`Không thể mở bản đã lưu: ${msg}`);
    }
  }

  async function removeSaved(id: number) {
    if (!confirm("Xóa bản phân tích đã lưu?")) return;
    try {
      await api.deleteSavedAnalysis(id);
      setSavedList((prev) => prev.filter((s) => s.id !== id));
      if (savedDetail?.id === id) setSavedDetail(null);
    } catch {
      // ignore
    }
  }

  async function loadForecast() {
    setForecastLoading(true);
    try {
      const data = await api.getAnnualForecast(familyId, forecastYear);
      setForecast(data);
    } catch (e: unknown) {
      setError("Không thể lấy dự báo.");
    } finally {
      setForecastLoading(false);
    }
  }

  async function sendChat(e: React.FormEvent) {
    e.preventDefault();
    if (!chatInput.trim() || chatLoading) return;

    const question = chatInput.trim();
    setChatInput("");
    setChatMessages((prev) => [...prev, { role: "user", content: question }]);
    setChatLoading(true);

    try {
      const { response } = await api.sendChat(familyId, question);
      setChatMessages((prev) => [...prev, { role: "ai", content: response }]);
    } catch (e: unknown) {
      setChatMessages((prev) => [
        ...prev,
        { role: "ai", content: "Xin lỗi, không thể kết nối. Hãy thử lại sau." },
      ]);
    } finally {
      setChatLoading(false);
    }
  }

  function handleTabChange(tab: Tab) {
    setActiveTab(tab);
    if (tab === "analysis" && !analysis) {
      loadAnalysis();
    }
    if (tab === "forecast" && !forecast) {
      loadForecast();
    }
    if (tab === "saved") {
      loadSaved();
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-96">
        <div className="text-center">
          <div className="text-5xl mb-4 pulse-soft">☯️</div>
          <p style={{ color: "var(--muted)" }}>Đang tải...</p>
        </div>
      </div>
    );
  }

  if (!family) {
    return (
      <div className="text-center py-20">
        <p className="text-xl">Không tìm thấy gia đình</p>
        <Link href="/families" className="mt-4 inline-block text-purple-600 underline">
          Quay lại
        </Link>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto px-4 py-8">
      {/* Header */}
      <div className="flex items-center justify-between gap-4 mb-6">
        <div className="flex items-center gap-4">
          <Link href="/families" className="text-purple-600 hover:underline text-sm">
            ← Danh sách gia đình
          </Link>
          <span style={{ color: "var(--muted)" }}>/</span>
          <h1 className="text-2xl font-bold gradient-text">{family.name}</h1>
        </div>
        <button
          onClick={() => setShowEditFamily(true)}
          className="px-3 py-1.5 rounded-lg text-xs font-medium"
          style={{ background: "#f3e8ff", color: "#6d28d9", border: "1px solid #e9d5ff" }}
          title="Chỉnh sửa thông tin gia đình"
        >
          ✏️ Sửa thông tin
        </button>
      </div>
      {family.description && (
        <p className="mb-4 text-sm" style={{ color: "var(--muted)" }}>{family.description}</p>
      )}

      {error && (
        <div
          className="mb-4 p-4 rounded-xl text-sm"
          style={{ background: "#fee2e2", color: "#dc2626" }}
        >
          ⚠️ {error}
          <button onClick={() => setError("")} className="ml-2 underline">Đóng</button>
        </div>
      )}

      {/* Tabs */}
      <div
        className="flex gap-1 p-1 rounded-xl mb-6"
        style={{ background: "#f3f4f6" }}
      >
        {[
          { key: "members" as Tab, label: "👥 Thành Viên" },
          { key: "analysis" as Tab, label: "🔮 Phân Tích" },
          { key: "forecast" as Tab, label: "🗓️ Dự Báo" },
          { key: "saved" as Tab, label: "💾 Đã Lưu" },
          { key: "chat" as Tab, label: "🤖 AI Cố Vấn" },
        ].map((tab) => (
          <button
            key={tab.key}
            onClick={() => handleTabChange(tab.key)}
            className="flex-1 py-2 px-3 rounded-lg text-sm font-medium transition-all"
            style={{
              background: activeTab === tab.key
                ? "linear-gradient(135deg, #8b5cf6, #ec4899)"
                : "transparent",
              color: activeTab === tab.key ? "white" : "var(--foreground)",
            }}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Members Tab */}
      {activeTab === "members" && (
        <div>
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-lg font-bold">
              Thành viên ({family.members.length})
            </h2>
            <button
              onClick={() => setShowAddMember(true)}
              className="px-4 py-2 rounded-lg text-white text-sm font-semibold"
              style={{ background: "linear-gradient(135deg, #8b5cf6, #ec4899)" }}
            >
              + Thêm Thành Viên
            </button>
          </div>

          {family.members.length === 0 ? (
            <div
              className="text-center py-16 rounded-2xl"
              style={{ border: "2px dashed var(--border)" }}
            >
              <div className="text-4xl mb-3">👤</div>
              <p style={{ color: "var(--muted)" }}>Chưa có thành viên nào</p>
              <button
                onClick={() => setShowAddMember(true)}
                className="mt-4 px-6 py-2 rounded-lg text-white text-sm"
                style={{ background: "linear-gradient(135deg, #8b5cf6, #ec4899)" }}
              >
                Thêm Thành Viên Đầu Tiên
              </button>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {family.members.map((member) => (
                <MemberCard
                  key={member.id}
                  member={member}
                  onDelete={() => deleteMember(member.id)}
                  onEdit={() => setEditingMember(member)}
                />
              ))}
            </div>
          )}

          {/* Add Member Modal */}
          {showAddMember && (
            <AddMemberModal
              form={memberForm}
              onChange={setMemberForm}
              onSubmit={addMember}
              onClose={() => setShowAddMember(false)}
            />
          )}
        </div>
      )}

      {/* Analysis Tab */}
      {activeTab === "analysis" && (
        <div>
          {analysisLoading && (
            <div className="py-16">
              <div className="max-w-md mx-auto text-center">
                <div className="text-4xl mb-4 pulse-soft">🔮</div>
                <p className="mb-3 font-semibold">Đang phân tích tử vi gia đình...</p>
                <p className="text-xs mb-4" style={{ color: "var(--muted)" }}>
                  {analysisProgress < 30
                    ? "Đang đọc dữ liệu thành viên..."
                    : analysisProgress < 60
                    ? "Tính toán Can - Chi, Ngũ hành, tương sinh tương khắc..."
                    : analysisProgress < 90
                    ? "Đang gọi AI để tổng hợp diễn giải chiều sâu..."
                    : "Hoàn tất..."}
                </p>
                <ProgressBar value={analysisProgress} />
                <p className="text-xs mt-2" style={{ color: "var(--muted)" }}>{Math.round(analysisProgress)}%</p>
              </div>
            </div>
          )}

          {!analysisLoading && analysis && (
            <>
              <div className="flex justify-end gap-2 mb-3">
                <button
                  onClick={saveCurrentAnalysis}
                  disabled={savingAnalysis}
                  className="px-4 py-2 rounded-lg text-sm font-semibold disabled:opacity-50"
                  style={{ background: "#f3e8ff", color: "#6d28d9", border: "1px solid #e9d5ff" }}
                >
                  {savingAnalysis ? "Đang lưu..." : "💾 Lưu kết quả này"}
                </button>
              </div>
              <AnalysisView analysis={analysis} onRefresh={() => { setAnalysis(null); loadAnalysis(); }} />
            </>
          )}

          {!analysisLoading && !analysis && (
            <div className="text-center py-20">
              <div className="text-4xl mb-4">🔮</div>
              <p className="mb-4" style={{ color: "var(--muted)" }}>
                Nhấn để bắt đầu phân tích tương hợp gia đình
              </p>
              <button
                onClick={loadAnalysis}
                className="px-8 py-3 rounded-xl text-white font-semibold"
                style={{ background: "linear-gradient(135deg, #8b5cf6, #ec4899)" }}
              >
                Bắt Đầu Phân Tích
              </button>
            </div>
          )}
        </div>
      )}

      {/* Saved Analyses Tab */}
      {activeTab === "saved" && (
        <SavedAnalysesView
          list={savedList}
          detail={savedDetail}
          onOpen={openSaved}
          onClose={() => setSavedDetail(null)}
          onDelete={removeSaved}
        />
      )}

      {/* Forecast Tab */}
      {activeTab === "forecast" && (
        <div>
          <div className="flex items-center gap-4 mb-6">
            <label className="font-medium">Năm dự báo:</label>
            <input
              type="number"
              value={forecastYear}
              onChange={(e) => setForecastYear(parseInt(e.target.value))}
              min={2020}
              max={2050}
              className="px-3 py-2 rounded-lg border text-sm w-24"
              style={{ border: "1px solid var(--border)" }}
            />
            <button
              onClick={loadForecast}
              disabled={forecastLoading}
              className="px-6 py-2 rounded-lg text-white text-sm font-semibold"
              style={{ background: "linear-gradient(135deg, #8b5cf6, #ec4899)" }}
            >
              {forecastLoading ? "Đang tính..." : "Xem Dự Báo"}
            </button>
          </div>

          {forecast && <ForecastView forecast={forecast} />}
        </div>
      )}

      {/* Chat Tab */}
      {activeTab === "chat" && (
        <ChatView
          messages={chatMessages}
          input={chatInput}
          loading={chatLoading}
          onInputChange={setChatInput}
          onSend={sendChat}
          familyName={family.name}
        />
      )}

      {showEditFamily && (
        <EditFamilyModal
          initial={{ name: family.name, description: family.description || "" }}
          onSubmit={saveFamilyEdits}
          onClose={() => setShowEditFamily(false)}
        />
      )}

      {editingMember && (
        <EditMemberModal
          member={editingMember}
          onSubmit={(patch) => saveMemberEdits(editingMember.id, patch)}
          onClose={() => setEditingMember(null)}
        />
      )}
    </div>
  );
}

// ============ Sub Components ============

function ProgressBar({ value }: { value: number }) {
  const v = Math.max(0, Math.min(100, value));
  return (
    <div
      className="w-full h-3 rounded-full overflow-hidden"
      role="progressbar"
      aria-valuenow={v}
      aria-valuemin={0}
      aria-valuemax={100}
      style={{ background: "#f3f4f6" }}
    >
      <div
        className="h-full transition-all duration-300 ease-out"
        style={{
          width: `${v}%`,
          background: "linear-gradient(90deg, #8b5cf6, #ec4899)",
        }}
      />
    </div>
  );
}

function MemberCard({ member, onDelete, onEdit }: { member: FamilyMember; onDelete: () => void; onEdit: () => void }) {
  const color = HANH_COLORS[member.ngu_hanh || ""] || "#8b5cf6";

  return (
    <div
      className="p-5 rounded-2xl card-hover"
      style={{
        background: "white",
        border: "1px solid var(--border)",
        boxShadow: "0 2px 8px rgba(0,0,0,0.05)",
      }}
    >
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-2">
          <div
            className="w-10 h-10 rounded-full flex items-center justify-center text-lg"
            style={{ background: `${color}20`, color }}
          >
            {member.gender === "nam" ? "👨" : "👩"}
          </div>
          <div>
            <div className="font-bold">{member.name}</div>
            <div className="text-xs" style={{ color: "var(--muted)" }}>
              {member.role} · {member.birth_year}
              {member.birth_calendar === "lunar" ? " (âm)" : ""}
            </div>
            {(member.solar_year || member.lunar_year) && (
              <div className="text-[10px] mt-0.5" style={{ color: "var(--muted)" }}>
                {member.solar_year && member.solar_month && member.solar_day && (
                  <span>☀️ {String(member.solar_day).padStart(2, "0")}/{String(member.solar_month).padStart(2, "0")}/{member.solar_year}</span>
                )}
                {member.solar_year && member.lunar_year && " · "}
                {member.lunar_year && member.lunar_month && member.lunar_day && (
                  <span>🌙 {String(member.lunar_day).padStart(2, "0")}/{String(member.lunar_month).padStart(2, "0")}/{member.lunar_year}{member.is_leap_month ? " (nhuận)" : ""}</span>
                )}
              </div>
            )}
          </div>
        </div>
        <div className="flex items-center gap-1">
          <button
            onClick={onEdit}
            className="text-gray-300 hover:text-purple-500 text-sm"
            title="Chỉnh sửa"
          >
            ✏️
          </button>
          <button
            onClick={onDelete}
            className="text-gray-300 hover:text-red-500 text-sm"
            title="Xóa"
          >
            ✕
          </button>
        </div>
      </div>

      {member.occupation && (
        <div className="mb-2 text-xs px-2 py-1 rounded-md inline-block" style={{ background: "#f0fdf4", color: "#166534" }}>
          💼 {member.occupation}
        </div>
      )}

      {member.thien_can && (
        <div className="space-y-2">
          <div className="flex items-center gap-2">
            <span
              className="px-2 py-0.5 rounded-md text-xs font-semibold"
              style={{ background: `${color}15`, color }}
            >
              {member.thien_can} {member.dia_chi}
            </span>
            <span
              className="px-2 py-0.5 rounded-md text-xs"
              style={{ background: `${color}10`, color }}
            >
              Hành {member.ngu_hanh}
            </span>
          </div>
          {member.nap_am && (
            <div className="text-xs" style={{ color: "var(--muted)" }}>
              Nạp Âm: {member.nap_am}
            </div>
          )}
          {member.energy_role && (
            <div
              className="text-xs p-2 rounded-lg"
              style={{ background: "#f8f4ff", color: "#6d28d9" }}
            >
              💫 {member.energy_role}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

interface AddMemberModalProps {
  form: {
    name: string;
    role: string;
    gender: string;
    occupation: string;
    birth_year: number;
    birth_month: string;
    birth_day: string;
    birth_calendar: "solar" | "lunar";
    is_leap_month: boolean;
  };
  onChange: (form: AddMemberModalProps["form"]) => void;
  onSubmit: (e: React.FormEvent) => void;
  onClose: () => void;
}

function AddMemberModal({ form, onChange, onSubmit, onClose }: AddMemberModalProps) {
  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4"
      style={{ background: "rgba(0,0,0,0.5)" }}
    >
      <div
        className="w-full max-w-md rounded-2xl p-6 fade-in max-h-screen overflow-y-auto"
        style={{ background: "white" }}
      >
        <h2 className="text-xl font-bold mb-4">Thêm Thành Viên</h2>
        <form onSubmit={onSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-1">Tên *</label>
            <input
              type="text"
              value={form.name}
              onChange={(e) => onChange({ ...form, name: e.target.value })}
              placeholder="Tên thành viên"
              className="w-full px-4 py-3 rounded-xl text-sm"
              style={{ border: "1px solid var(--border)", outline: "none" }}
              required
            />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-sm font-medium mb-1">Vai trò *</label>
              <select
                value={form.role}
                onChange={(e) => onChange({ ...form, role: e.target.value })}
                className="w-full px-3 py-3 rounded-xl text-sm"
                style={{ border: "1px solid var(--border)", outline: "none" }}
              >
                {ROLES.map((r) => (
                  <option key={r} value={r}>{r}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Giới tính *</label>
              <select
                value={form.gender}
                onChange={(e) => onChange({ ...form, gender: e.target.value })}
                className="w-full px-3 py-3 rounded-xl text-sm"
                style={{ border: "1px solid var(--border)", outline: "none" }}
              >
                <option value="nam">Nam</option>
                <option value="nữ">Nữ</option>
              </select>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">Nghề nghiệp</label>
            <input
              type="text"
              value={form.occupation}
              onChange={(e) => onChange({ ...form, occupation: e.target.value })}
              placeholder="VD: kỹ sư phần mềm, giáo viên, học sinh..."
              className="w-full px-4 py-3 rounded-xl text-sm"
              style={{ border: "1px solid var(--border)", outline: "none" }}
            />
            <p className="text-xs mt-1" style={{ color: "var(--muted)" }}>
              Nghề nghiệp giúp phân tích sâu hơn về sự nghiệp và mệnh ngũ hành.
            </p>
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">Loại lịch ngày sinh *</label>
            <div className="flex gap-2">
              {(["solar", "lunar"] as const).map((cal) => (
                <button
                  key={cal}
                  type="button"
                  onClick={() => onChange({ ...form, birth_calendar: cal })}
                  className="flex-1 py-2 px-3 rounded-xl text-sm font-medium"
                  style={{
                    background: form.birth_calendar === cal
                      ? "linear-gradient(135deg, #8b5cf6, #ec4899)"
                      : "#f3f4f6",
                    color: form.birth_calendar === cal ? "white" : "var(--foreground)",
                    border: "1px solid var(--border)",
                  }}
                >
                  {cal === "solar" ? "☀️ Dương lịch" : "🌙 Âm lịch"}
                </button>
              ))}
            </div>
            <p className="text-xs mt-1" style={{ color: "var(--muted)" }}>
              Nhập ngày sinh theo {form.birth_calendar === "solar" ? "Dương lịch (lịch thường dùng)" : "Âm lịch (lịch ta)"}. Hệ thống tự động chuyển đổi và lưu cả hai.
            </p>
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">
              Năm sinh ({form.birth_calendar === "lunar" ? "âm" : "dương"}) *
            </label>
            <input
              type="number"
              value={form.birth_year}
              onChange={(e) => onChange({ ...form, birth_year: parseInt(e.target.value) })}
              min={1900}
              max={2050}
              className="w-full px-4 py-3 rounded-xl text-sm"
              style={{ border: "1px solid var(--border)", outline: "none" }}
              required
            />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-sm font-medium mb-1">Tháng sinh</label>
              <input
                type="number"
                value={form.birth_month}
                onChange={(e) => onChange({ ...form, birth_month: e.target.value })}
                placeholder="1-12"
                min={1}
                max={12}
                className="w-full px-4 py-3 rounded-xl text-sm"
                style={{ border: "1px solid var(--border)", outline: "none" }}
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Ngày sinh</label>
              <input
                type="number"
                value={form.birth_day}
                onChange={(e) => onChange({ ...form, birth_day: e.target.value })}
                placeholder="1-31"
                min={1}
                max={31}
                className="w-full px-4 py-3 rounded-xl text-sm"
                style={{ border: "1px solid var(--border)", outline: "none" }}
              />
            </div>
          </div>

          {form.birth_calendar === "lunar" && (
            <label className="flex items-center gap-2 text-sm cursor-pointer">
              <input
                type="checkbox"
                checked={form.is_leap_month}
                onChange={(e) => onChange({ ...form, is_leap_month: e.target.checked })}
              />
              <span>Tháng nhuận (chỉ tích khi sinh đúng vào tháng nhuận âm lịch)</span>
            </label>
          )}

          <div className="flex gap-3 pt-2">
            <button
              type="submit"
              className="flex-1 py-3 rounded-xl text-white font-semibold"
              style={{ background: "linear-gradient(135deg, #8b5cf6, #ec4899)" }}
            >
              Thêm Thành Viên
            </button>
            <button
              type="button"
              onClick={onClose}
              className="px-6 py-3 rounded-xl font-semibold"
              style={{ background: "#f3f4f6" }}
            >
              Hủy
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

function AnalysisView({ analysis, onRefresh }: { analysis: FamilyAnalysis; onRefresh: () => void }) {
  const [selectedPair, setSelectedPair] = useState(0);

  const scoreColor = (score: number) => {
    if (score >= 65) return "#22c55e";
    if (score >= 45) return "#f59e0b";
    if (score >= 25) return "#8b5cf6";
    return "#ef4444";
  };

  return (
    <div className="space-y-6 fade-in">
      {/* Overall Score */}
      <div
        className="p-6 rounded-2xl text-center"
        style={{
          background: "linear-gradient(135deg, #1a1a2e, #16213e)",
          color: "white",
        }}
      >
        <div className="text-5xl font-bold mb-2" style={{ color: scoreColor(analysis.family_overall_score) }}>
          {analysis.family_overall_score}
          <span className="text-2xl">/100</span>
        </div>
        <div className="text-lg font-semibold mb-2">Điểm Tương Hợp Gia Đình</div>
        <p className="text-gray-300 text-sm max-w-xl mx-auto">{analysis.family_dynamics}</p>
      </div>

      {/* Energy Distribution */}
      {Object.keys(analysis.energy_distribution).length > 0 && (
        <div
          className="p-5 rounded-2xl"
          style={{ background: "white", border: "1px solid var(--border)" }}
        >
          <h3 className="font-bold mb-4">Phân Bố Ngũ Hành</h3>
          <div className="flex flex-wrap gap-3">
            {Object.entries(analysis.energy_distribution).map(([hanh, count]) => (
              <div
                key={hanh}
                className="flex items-center gap-2 px-4 py-2 rounded-xl"
                style={{
                  background: `${HANH_COLORS[hanh] || "#8b5cf6"}15`,
                  border: `1px solid ${HANH_COLORS[hanh] || "#8b5cf6"}30`,
                }}
              >
                <span className="font-bold" style={{ color: HANH_COLORS[hanh] || "#8b5cf6" }}>
                  {hanh}
                </span>
                <span
                  className="text-xs px-1.5 py-0.5 rounded-full text-white"
                  style={{ background: HANH_COLORS[hanh] || "#8b5cf6" }}
                >
                  {count}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Energy Roles */}
      {analysis.energy_roles && analysis.energy_roles.length > 0 && (
        <div
          className="p-5 rounded-2xl"
          style={{ background: "#f8f4ff", border: "1px solid #e9d5ff" }}
        >
          <h3 className="font-bold mb-4">Vai Trò Năng Lượng</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {analysis.energy_roles.map((er, i) => (
              <div key={i} className="flex items-start gap-2">
                <span className="text-purple-500 mt-0.5">💫</span>
                <div>
                  <span className="font-semibold text-sm">{er.name}: </span>
                  <span className="text-sm" style={{ color: "var(--muted)" }}>{er.role}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Pairs Analysis */}
      {analysis.pairs_analysis.length > 0 && (
        <div>
          <h3 className="font-bold text-lg mb-4">Phân Tích Từng Cặp Quan Hệ</h3>

          {/* Pair selector */}
          <div className="flex flex-wrap gap-2 mb-4">
            {analysis.pairs_analysis.map((pair, i) => (
              <button
                key={i}
                onClick={() => setSelectedPair(i)}
                className="px-3 py-1.5 rounded-lg text-sm font-medium transition-all"
                style={{
                  background: selectedPair === i
                    ? "linear-gradient(135deg, #8b5cf6, #ec4899)"
                    : "#f3f4f6",
                  color: selectedPair === i ? "white" : "var(--foreground)",
                }}
              >
                {pair.member1_name} ↔ {pair.member2_name}
              </button>
            ))}
          </div>

          {/* Selected pair detail */}
          {analysis.pairs_analysis[selectedPair] && (
            <PairDetail pair={analysis.pairs_analysis[selectedPair]} />
          )}
        </div>
      )}

      {/* AI Interpretation */}
      {analysis.ai_interpretation && (
        <div
          className="rounded-2xl overflow-hidden"
          style={{ background: "white", border: "1px solid var(--border)" }}
        >
          <div
            className="px-6 py-4 flex items-center gap-2 flex-wrap"
            style={{
              background: "linear-gradient(135deg, rgba(139,92,246,0.08), rgba(236,72,153,0.08))",
              borderBottom: "1px solid var(--border)",
            }}
          >
            <span className="text-2xl">
              {analysis.analysis_mode === "offline" ? "📖" : "🤖"}
            </span>
            <h3 className="font-bold text-lg">
              {analysis.analysis_mode === "offline" ? "Phân Tích Chi Tiết" : "Phân Tích AI"}
            </h3>
            {analysis.analysis_mode && (
              <span
                className="ml-auto text-xs px-2.5 py-1 rounded-full font-medium"
                style={{
                  background: analysis.analysis_mode === "online" ? "#dcfce7" : "#fef3c7",
                  color: analysis.analysis_mode === "online" ? "#166534" : "#92400e",
                }}
              >
                {analysis.analysis_mode === "online" ? "Online (ChatGPT)" : "Offline"}
              </span>
            )}
          </div>
          <div className="p-6">
            <MarkdownContent content={analysis.ai_interpretation} />
          </div>
        </div>
      )}

      {/* Bibliography - full source list */}
      {analysis.sources && analysis.sources.length > 0 && (
        <div
          className="p-6 rounded-2xl"
          style={{ background: "#fafaf9", border: "1px solid var(--border)" }}
        >
          <h3 className="font-bold text-lg mb-3 flex items-center gap-2">
            <span>📚</span> Nguồn Dữ Liệu & Tài Liệu Tham Khảo
          </h3>
          <p className="text-xs mb-3" style={{ color: "var(--muted)" }}>
            Phân tích dựa trên các tài liệu kinh điển và học thuật về Tử Vi - Ngũ Hành - Âm Dương:
          </p>
          <ul className="space-y-2 text-sm">
            {analysis.sources.map((s, i) => (
              <li key={i} className="flex gap-2">
                <span className="text-purple-500">•</span>
                <div>
                  <span className="font-semibold">{s.title}</span> — {s.author} ({s.year}).{" "}
                  <span style={{ color: "var(--muted)" }}>{s.note}</span>
                </div>
              </li>
            ))}
          </ul>
        </div>
      )}

      <div className="text-center">
        <button
          onClick={onRefresh}
          className="px-6 py-2 rounded-lg text-sm font-medium"
          style={{ background: "#f3f4f6" }}
        >
          🔄 Phân Tích Lại
        </button>
      </div>
    </div>
  );
}

function PairDetail({ pair }: { pair: PairCompatibility }) {
  const pairData = pair;

  const scoreColor = (score: number) => {
    if (score >= 65) return "#22c55e";
    if (score >= 45) return "#f59e0b";
    if (score >= 25) return "#8b5cf6";
    return "#ef4444";
  };

  const sinhKhacColor = (type?: string) => {
    if (!type) return "#6b7280";
    if (type.includes("sinh")) return "#22c55e";
    if (type.includes("khac")) return "#ef4444";
    if (type.includes("ty")) return "#8b5cf6";
    return "#6b7280";
  };

  const radarData = [
    { subject: "Cảm Xúc", value: pairData.radar_scores.emotional },
    { subject: "Giao Tiếp", value: pairData.radar_scores.communication },
    { subject: "Tài Chính", value: pairData.radar_scores.financial },
    { subject: "Lối Sống", value: pairData.radar_scores.lifestyle },
    { subject: "Bền Vững", value: pairData.radar_scores.stability },
  ];

  return (
    <div
      className="p-6 rounded-2xl fade-in"
      style={{ background: "white", border: "1px solid var(--border)" }}
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-5">
        <div>
          <div className="flex items-center gap-3">
            <span className="font-bold text-lg">{pairData.member1_name}</span>
            <span style={{ color: "var(--muted)" }}>↔</span>
            <span className="font-bold text-lg">{pairData.member2_name}</span>
          </div>
          <div className="text-sm mt-1" style={{ color: "var(--muted)" }}>
            {pairData.member1_role} ({pairData.member1_can_chi}) ↔ {pairData.member2_role} ({pairData.member2_can_chi})
          </div>
          {pairData.relationship_type && (
            <div
              className="inline-block mt-2 px-2 py-0.5 rounded-md text-xs font-semibold"
              style={{ background: "#ede9fe", color: "#6d28d9" }}
            >
              {pairData.relationship_type}
            </div>
          )}
        </div>
        <div className="text-right">
          <div className="text-3xl font-bold" style={{ color: scoreColor(pairData.overall_score) }}>
            {pairData.overall_score}
          </div>
          <div className="text-sm font-medium">{pairData.compatibility_level}</div>
        </div>
      </div>

      {/* Tương Sinh / Tương Khắc highlight */}
      {pairData.sinh_khac && (
        <div
          className="mb-5 p-4 rounded-xl"
          style={{
            background: `${sinhKhacColor(pairData.sinh_khac.type)}10`,
            border: `1px solid ${sinhKhacColor(pairData.sinh_khac.type)}40`,
          }}
        >
          <div
            className="text-xs uppercase font-semibold mb-1"
            style={{ color: sinhKhacColor(pairData.sinh_khac.type) }}
          >
            Tương Sinh / Tương Khắc bản mệnh
          </div>
          <div className="font-bold text-base mb-1">{pairData.sinh_khac.headline}</div>
          <div className="text-sm" style={{ color: "var(--foreground)" }}>
            {pairData.sinh_khac.detail}
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Radar Chart */}
        <div>
          <h4 className="font-semibold text-sm mb-3" style={{ color: "var(--muted)" }}>
            BIỂU ĐỒ TƯƠNG HỢP
          </h4>
          <ResponsiveContainer width="100%" height={220}>
            <RadarChart data={radarData}>
              <PolarGrid />
              <PolarAngleAxis dataKey="subject" tick={{ fontSize: 11 }} />
              <Radar
                name="Score"
                dataKey="value"
                stroke="#8b5cf6"
                fill="#8b5cf6"
                fillOpacity={0.3}
              />
              <Tooltip formatter={(val) => [`${val}/100`, "Điểm"]} />
            </RadarChart>
          </ResponsiveContainer>
        </div>

        {/* Analysis details */}
        <div className="space-y-3">
          <div
            className="p-3 rounded-xl text-sm"
            style={{ background: "#f8f4ff" }}
          >
            <div className="font-semibold text-xs uppercase mb-1" style={{ color: "#8b5cf6" }}>
              Thiên Can
            </div>
            <div>{pairData.can_compatibility.description || pairData.can_compatibility.relation}</div>
          </div>
          <div
            className="p-3 rounded-xl text-sm"
            style={{ background: "#f0fdf4" }}
          >
            <div className="font-semibold text-xs uppercase mb-1" style={{ color: "#16a34a" }}>
              Địa Chi
            </div>
            <div>{pairData.chi_compatibility.description}</div>
          </div>
          <div
            className="p-3 rounded-xl text-sm"
            style={{ background: "#fff7ed" }}
          >
            <div className="font-semibold text-xs uppercase mb-1" style={{ color: "#d97706" }}>
              Ngũ Hành
            </div>
            <div>{pairData.hanh_compatibility.description}</div>
          </div>
        </div>
      </div>

      {/* Relationship explanation (from knowledge base) */}
      {pairData.relationship_explanation && (
        <div
          className="mt-5 p-4 rounded-xl text-sm"
          style={{ background: "#fef3c7", border: "1px solid #fde68a" }}
        >
          <div className="text-xs uppercase font-semibold mb-1" style={{ color: "#b45309" }}>
            📖 Tri thức truyền thống
          </div>
          <div>{pairData.relationship_explanation}</div>
        </div>
      )}

      {/* Relationship-specific advice */}
      {pairData.relationship_advice && pairData.relationship_advice.length > 0 && (
        <div className="mt-5">
          <h4 className="font-semibold mb-3">🎯 Khuyến Nghị Theo Loại Quan Hệ</h4>
          <div className="space-y-2">
            {pairData.relationship_advice.map((rec, i) => (
              <div
                key={i}
                className="flex items-start gap-2 p-3 rounded-xl text-sm"
                style={{ background: "#ecfeff", border: "1px solid #a5f3fc" }}
              >
                <span className="mt-0.5" style={{ color: "#0891b2" }}>★</span>
                <span>{rec}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* General recommendations */}
      {pairData.recommendations.length > 0 && (
        <div className="mt-5">
          <h4 className="font-semibold mb-3">💡 Khuyến Nghị Chung</h4>
          <div className="space-y-2">
            {pairData.recommendations.map((rec, i) => (
              <div
                key={i}
                className="flex items-start gap-2 p-3 rounded-xl text-sm"
                style={{ background: "#f8f4ff", border: "1px solid #e9d5ff" }}
              >
                <span className="text-purple-500 mt-0.5">→</span>
                <span>{rec}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Citations for this pair */}
      {pairData.citations && pairData.citations.length > 0 && (
        <div className="mt-5">
          <h4 className="font-semibold text-sm mb-2" style={{ color: "var(--muted)" }}>
            📚 Trích dẫn cho phân tích này
          </h4>
          <ul className="text-xs space-y-1" style={{ color: "var(--muted)" }}>
            {pairData.citations.map((c, i) => (
              <li key={i}>
                <span className="font-semibold">{c.title}</span> — {c.author} ({c.year})
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

function ForecastView({ forecast }: { forecast: FamilyForecast }) {
  const levelColors: Record<string, string> = {
    "thuận lợi": "#22c55e",
    "ổn định": "#3b82f6",
    "cần chú ý": "#f59e0b",
    "thách thức": "#ef4444",
    "biến động": "#a855f7",
  };

  const [selected, setSelected] = useState<number>(0);
  const activeMember: MemberForecast | undefined = forecast.member_forecasts[selected];

  return (
    <div className="space-y-5 fade-in">
      {/* Family year summary */}
      <div
        className="p-6 rounded-2xl"
        style={{
          background: "linear-gradient(135deg, #1a1a2e, #16213e)",
          color: "white",
        }}
      >
        <div className="text-xl font-bold mb-2">🗓️ Năm {forecast.year} - Tổng Quan Gia Đình</div>
        <p className="text-gray-300 leading-relaxed">{forecast.family_year_summary}</p>
        <div className="flex gap-2 mt-4 text-sm flex-wrap">
          {forecast.thai_tue_count > 0 && (
            <span className="px-3 py-1 rounded-full" style={{ background: "#a855f730" }}>
              ⚠️ {forecast.thai_tue_count} thành viên Thái Tuế
            </span>
          )}
          <span className="px-3 py-1 rounded-full" style={{ background: "#22c55e30" }}>
            ✨ {forecast.positive_count}/{forecast.member_forecasts.length} thuận lợi
          </span>
        </div>
      </div>

      {/* Member quick picker */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
        {forecast.member_forecasts.map((mf, i) => {
          const isActive = selected === i;
          const color = levelColors[mf.energy_level] || "#8b5cf6";
          return (
            <button
              key={i}
              onClick={() => setSelected(i)}
              className="text-left p-4 rounded-2xl card-hover transition-all"
              style={{
                background: isActive ? `${color}10` : "white",
                border: `2px solid ${isActive ? color : "#e5e7eb"}`,
                boxShadow: isActive ? `0 4px 12px ${color}30` : "0 1px 3px rgba(0,0,0,0.04)",
              }}
            >
              <div className="flex items-center justify-between mb-2">
                <span className="font-bold text-sm">{mf.name}</span>
                <span
                  className="text-[10px] px-2 py-0.5 rounded-full font-semibold"
                  style={{ background: `${color}20`, color }}
                >
                  {mf.energy_level}
                </span>
              </div>
              <div className="text-[11px]" style={{ color: "var(--muted)" }}>
                {mf.role} · {mf.birth_can_chi}
              </div>
              {mf.is_thai_tue && (
                <div className="text-[10px] mt-1 font-medium" style={{ color: "#7c3aed" }}>
                  ⚠️ Thái Tuế
                </div>
              )}
            </button>
          );
        })}
      </div>

      {/* Detailed forecast for selected member */}
      {activeMember && <MemberForecastDetail mf={activeMember} year={forecast.year} />}
    </div>
  );
}

function MemberForecastDetail({ mf, year }: { mf: MemberForecast; year: number }) {
  const levelColors: Record<string, string> = {
    "thuận lợi": "#22c55e",
    "ổn định": "#3b82f6",
    "cần chú ý": "#f59e0b",
    "thách thức": "#ef4444",
    "biến động": "#a855f7",
  };
  const color = levelColors[mf.energy_level] || "#8b5cf6";
  const sections = mf.detailed?.sections || [];
  const highlights = mf.detailed?.highlights || [];

  return (
    <div
      className="rounded-2xl overflow-hidden fade-in"
      style={{ background: "white", border: "1px solid var(--border)" }}
    >
      {/* Header */}
      <div
        className="p-5"
        style={{
          background: `linear-gradient(135deg, ${color}15, ${color}05)`,
          borderBottom: "1px solid var(--border)",
        }}
      >
        <div className="flex items-start justify-between gap-3 flex-wrap">
          <div>
            <div className="text-lg font-bold">
              {mf.name}{" "}
              <span style={{ color: "var(--muted)" }} className="text-sm font-normal">
                · {mf.role}
              </span>
            </div>
            <div className="text-xs mt-1" style={{ color: "var(--muted)" }}>
              Bản mệnh: <strong>{mf.birth_can_chi}</strong>
              {mf.ngu_hanh && <> · hành <strong>{mf.ngu_hanh}</strong></>}
              {mf.nap_am && <> · nạp âm <strong>{mf.nap_am}</strong></>}
            </div>
            <div className="text-xs mt-0.5" style={{ color: "var(--muted)" }}>
              Năm {year}: <strong>{mf.year_can_chi}</strong>
            </div>
          </div>
          <span
            className="px-3 py-1 rounded-full text-xs font-semibold"
            style={{ background: `${color}20`, color }}
          >
            {mf.energy_level}
          </span>
        </div>

        {/* Highlights */}
        {highlights.length > 0 && (
          <div className="mt-4 space-y-1.5">
            {highlights.map((h, i) => (
              <div
                key={i}
                className="text-sm px-3 py-2 rounded-lg"
                style={{ background: "white", border: `1px solid ${color}30` }}
              >
                {h}
              </div>
            ))}
          </div>
        )}

        {/* Top summary */}
        <p className="text-sm mt-4 leading-relaxed" style={{ color: "var(--foreground)" }}>
          {mf.forecast}
        </p>
      </div>

      {/* Sections grid */}
      {sections.length > 0 && (
        <div className="p-5 grid grid-cols-1 md:grid-cols-2 gap-3">
          {sections.map((s) => (
            <div
              key={s.key}
              className="p-4 rounded-xl"
              style={{ background: "#fafaf9", border: "1px solid var(--border)" }}
            >
              <div className="flex items-center gap-2 mb-2">
                <span className="text-xl">{s.icon}</span>
                <h4 className="font-semibold text-sm">{s.title}</h4>
              </div>
              <div className="text-sm leading-relaxed" style={{ color: "var(--foreground)" }}>
                <MarkdownContent content={s.content} compact />
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function ChatView({
  messages,
  input,
  loading,
  onInputChange,
  onSend,
  familyName,
}: {
  messages: Array<{ role: "user" | "ai"; content: string }>;
  input: string;
  loading: boolean;
  onInputChange: (v: string) => void;
  onSend: (e: React.FormEvent) => void;
  familyName: string;
}) {
  const suggestions = [
    "Vì sao vợ chồng hay xảy ra mâu thuẫn?",
    "Con tôi hợp học ngành gì?",
    "Năm nay gia đình có nên đầu tư không?",
    "Ai trong gia đình phù hợp quản lý tài chính?",
  ];

  return (
    <div className="flex flex-col" style={{ height: "60vh" }}>
      <div
        className="flex-1 overflow-y-auto p-4 rounded-2xl mb-4 space-y-4"
        style={{ background: "#f8f4ff", border: "1px solid #e9d5ff" }}
      >
        {messages.length === 0 && (
          <div className="text-center py-8">
            <div className="text-4xl mb-3">🤖</div>
            <h3 className="font-bold mb-2">AI Cố Vấn Gia Đình {familyName}</h3>
            <p className="text-sm mb-4" style={{ color: "var(--muted)" }}>
              Hỏi tôi bất kỳ câu hỏi nào về gia đình bạn
            </p>
            <div className="flex flex-wrap gap-2 justify-center">
              {suggestions.map((s) => (
                <button
                  key={s}
                  onClick={() => onInputChange(s)}
                  className="px-3 py-2 rounded-xl text-sm"
                  style={{
                    background: "white",
                    border: "1px solid #e9d5ff",
                    color: "#6d28d9",
                  }}
                >
                  {s}
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((msg, i) => (
          <div
            key={i}
            className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
          >
            <div
              className={`px-4 py-3 rounded-2xl text-sm ${msg.role === "user" ? "max-w-xs lg:max-w-md" : "max-w-xl lg:max-w-2xl"}`}
              style={{
                background: msg.role === "user"
                  ? "linear-gradient(135deg, #8b5cf6, #ec4899)"
                  : "white",
                color: msg.role === "user" ? "white" : "var(--foreground)",
                border: msg.role === "ai" ? "1px solid var(--border)" : "none",
              }}
            >
              {msg.role === "ai" && (
                <div className="font-semibold text-xs mb-1" style={{ color: "#8b5cf6" }}>
                  🤖 AI Cố Vấn
                </div>
              )}
              {msg.role === "ai" ? (
                <MarkdownContent content={msg.content} compact />
              ) : (
                <div className="whitespace-pre-wrap">{msg.content}</div>
              )}
            </div>
          </div>
        ))}

        {loading && (
          <div className="flex justify-start">
            <div
              className="px-4 py-3 rounded-2xl text-sm"
              style={{ background: "white", border: "1px solid var(--border)" }}
            >
              <span className="pulse-soft">🤔 Đang phân tích...</span>
            </div>
          </div>
        )}
      </div>

      <form onSubmit={onSend} className="flex gap-3">
        <input
          type="text"
          value={input}
          onChange={(e) => onInputChange(e.target.value)}
          placeholder="Hỏi về gia đình của bạn..."
          className="flex-1 px-4 py-3 rounded-xl text-sm"
          style={{ border: "1px solid var(--border)", outline: "none" }}
          disabled={loading}
        />
        <button
          type="submit"
          disabled={loading || !input.trim()}
          className="px-6 py-3 rounded-xl text-white font-semibold disabled:opacity-50"
          style={{ background: "linear-gradient(135deg, #8b5cf6, #ec4899)" }}
        >
          Gửi
        </button>
      </form>
    </div>
  );
}

// ============ Markdown Renderer ============

function MarkdownContent({ content, compact = false }: { content: string; compact?: boolean }) {
  return (
    <div className={`tuvi-markdown ${compact ? "tuvi-markdown-compact" : ""}`}>
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={{
          h1: ({ children }) => (
            <h1
              className="text-2xl font-bold mt-6 mb-3 pb-2"
              style={{
                background: "linear-gradient(135deg, #8b5cf6, #ec4899)",
                WebkitBackgroundClip: "text",
                WebkitTextFillColor: "transparent",
                borderBottom: "2px solid #f3e8ff",
              }}
            >
              {children}
            </h1>
          ),
          h2: ({ children }) => (
            <h2
              className="text-xl font-bold mt-6 mb-3 flex items-center gap-2"
              style={{ color: "#6d28d9" }}
            >
              <span
                className="inline-block w-1 h-6 rounded-full"
                style={{ background: "linear-gradient(180deg, #8b5cf6, #ec4899)" }}
              />
              {children}
            </h2>
          ),
          h3: ({ children }) => (
            <h3 className="text-base font-semibold mt-4 mb-2" style={{ color: "#7c3aed" }}>
              {children}
            </h3>
          ),
          h4: ({ children }) => (
            <h4 className="text-sm font-semibold mt-3 mb-1.5" style={{ color: "var(--foreground)" }}>
              {children}
            </h4>
          ),
          p: ({ children }) => (
            <p className="text-sm leading-relaxed my-2" style={{ color: "var(--foreground)" }}>
              {children}
            </p>
          ),
          ul: ({ children }) => <ul className="my-2 space-y-1 pl-1">{children}</ul>,
          ol: ({ children }) => (
            <ol className="my-2 space-y-1 pl-5 list-decimal" style={{ color: "var(--foreground)" }}>
              {children}
            </ol>
          ),
          li: ({ children }) => (
            <li
              className="text-sm leading-relaxed pl-5 relative"
              style={{ color: "var(--foreground)" }}
            >
              <span
                className="absolute left-0 top-2 w-1.5 h-1.5 rounded-full"
                style={{ background: "linear-gradient(135deg, #8b5cf6, #ec4899)" }}
              />
              {children}
            </li>
          ),
          strong: ({ children }) => (
            <strong className="font-semibold" style={{ color: "#6d28d9" }}>
              {children}
            </strong>
          ),
          em: ({ children }) => (
            <em style={{ color: "var(--muted)" }}>{children}</em>
          ),
          blockquote: ({ children }) => (
            <blockquote
              className="my-3 pl-4 py-2 pr-3 rounded-r-lg text-sm"
              style={{
                borderLeft: "4px solid #a855f7",
                background: "#faf5ff",
                color: "var(--foreground)",
              }}
            >
              {children}
            </blockquote>
          ),
          hr: () => (
            <hr
              className="my-5 border-0 h-px"
              style={{
                background:
                  "linear-gradient(90deg, transparent, #d8b4fe 50%, transparent)",
              }}
            />
          ),
          table: ({ children }) => (
            <div className="my-3 overflow-x-auto rounded-xl" style={{ border: "1px solid var(--border)" }}>
              <table className="w-full text-sm border-collapse">{children}</table>
            </div>
          ),
          thead: ({ children }) => (
            <thead style={{ background: "#f8f4ff" }}>{children}</thead>
          ),
          th: ({ children }) => (
            <th
              className="px-3 py-2 text-left font-semibold text-xs uppercase tracking-wide"
              style={{ color: "#6d28d9", borderBottom: "1px solid var(--border)" }}
            >
              {children}
            </th>
          ),
          td: ({ children }) => (
            <td
              className="px-3 py-2 text-sm align-top"
              style={{ borderTop: "1px solid var(--border)" }}
            >
              {children}
            </td>
          ),
          code: ({ children }) => (
            <code
              className="px-1.5 py-0.5 rounded text-xs font-mono"
              style={{ background: "#f3e8ff", color: "#6d28d9" }}
            >
              {children}
            </code>
          ),
          a: ({ href, children }) => (
            <a
              href={href}
              target="_blank"
              rel="noopener noreferrer"
              className="underline"
              style={{ color: "#7c3aed" }}
            >
              {children}
            </a>
          ),
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  );
}

// ============ Edit Family Modal ============

function EditFamilyModal({
  initial,
  onSubmit,
  onClose,
}: {
  initial: { name: string; description: string };
  onSubmit: (patch: { name?: string; description?: string }) => void;
  onClose: () => void;
}) {
  const [name, setName] = useState(initial.name);
  const [description, setDescription] = useState(initial.description);

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4"
      style={{ background: "rgba(0,0,0,0.5)" }}
    >
      <div
        className="w-full max-w-md rounded-2xl p-6 fade-in"
        style={{ background: "white" }}
      >
        <h2 className="text-xl font-bold mb-4">Chỉnh sửa gia đình</h2>
        <form
          onSubmit={(e) => {
            e.preventDefault();
            const patch: { name?: string; description?: string } = {};
            if (name.trim() && name.trim() !== initial.name) patch.name = name.trim();
            if (description !== initial.description) patch.description = description;
            if (Object.keys(patch).length === 0) {
              onClose();
              return;
            }
            onSubmit(patch);
          }}
          className="space-y-4"
        >
          <div>
            <label className="block text-sm font-medium mb-1">Tên gia đình *</label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="w-full px-4 py-3 rounded-xl text-sm"
              style={{ border: "1px solid var(--border)", outline: "none" }}
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Mô tả</label>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              rows={3}
              className="w-full px-4 py-3 rounded-xl text-sm"
              style={{ border: "1px solid var(--border)", outline: "none" }}
            />
          </div>
          <div className="flex gap-3 pt-2">
            <button
              type="submit"
              className="flex-1 py-3 rounded-xl text-white font-semibold"
              style={{ background: "linear-gradient(135deg, #8b5cf6, #ec4899)" }}
            >
              Lưu thay đổi
            </button>
            <button
              type="button"
              onClick={onClose}
              className="px-6 py-3 rounded-xl font-semibold"
              style={{ background: "#f3f4f6" }}
            >
              Hủy
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

// ============ Edit Member Modal ============

function EditMemberModal({
  member,
  onSubmit,
  onClose,
}: {
  member: FamilyMember;
  onSubmit: (patch: Partial<{ name: string; role: string; gender: string; occupation: string; birth_year: number; birth_month: number; birth_day: number; birth_calendar: 'solar' | 'lunar'; is_leap_month: boolean }>) => void;
  onClose: () => void;
}) {
  const ROLES = ["chồng", "vợ", "con", "cha", "mẹ", "anh", "chị", "em"];
  const [name, setName] = useState(member.name);
  const [role, setRole] = useState(member.role);
  const [gender, setGender] = useState(member.gender);
  const [occupation, setOccupation] = useState(member.occupation || "");
  const [birthYear, setBirthYear] = useState(member.birth_year);
  const [birthMonth, setBirthMonth] = useState(member.birth_month ? String(member.birth_month) : "");
  const [birthDay, setBirthDay] = useState(member.birth_day ? String(member.birth_day) : "");
  const [birthCalendar, setBirthCalendar] = useState<"solar" | "lunar">(member.birth_calendar || "solar");
  const [isLeapMonth, setIsLeapMonth] = useState<boolean>(!!member.is_leap_month);

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4"
      style={{ background: "rgba(0,0,0,0.5)" }}
    >
      <div
        className="w-full max-w-md rounded-2xl p-6 fade-in max-h-screen overflow-y-auto"
        style={{ background: "white" }}
      >
        <h2 className="text-xl font-bold mb-4">Chỉnh sửa thành viên</h2>
        <form
          onSubmit={(e) => {
            e.preventDefault();
            const patch: Parameters<typeof onSubmit>[0] = {};
            if (name.trim() && name.trim() !== member.name) patch.name = name.trim();
            if (role !== member.role) patch.role = role;
            if (gender !== member.gender) patch.gender = gender;
            if (occupation !== (member.occupation || "")) patch.occupation = occupation;
            if (birthYear !== member.birth_year) patch.birth_year = birthYear;
            const newMonth = birthMonth ? parseInt(birthMonth) : undefined;
            if (newMonth !== member.birth_month) patch.birth_month = newMonth as number;
            const newDay = birthDay ? parseInt(birthDay) : undefined;
            if (newDay !== member.birth_day) patch.birth_day = newDay as number;
            if (birthCalendar !== (member.birth_calendar || "solar")) patch.birth_calendar = birthCalendar;
            if (isLeapMonth !== !!member.is_leap_month) patch.is_leap_month = isLeapMonth;
            if (Object.keys(patch).length === 0) {
              onClose();
              return;
            }
            onSubmit(patch);
          }}
          className="space-y-4"
        >
          <div>
            <label className="block text-sm font-medium mb-1">Tên *</label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="w-full px-4 py-3 rounded-xl text-sm"
              style={{ border: "1px solid var(--border)", outline: "none" }}
              required
            />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-sm font-medium mb-1">Vai trò</label>
              <select
                value={role}
                onChange={(e) => setRole(e.target.value)}
                className="w-full px-3 py-3 rounded-xl text-sm"
                style={{ border: "1px solid var(--border)", outline: "none" }}
              >
                {ROLES.map((r) => (
                  <option key={r} value={r}>{r}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Giới tính</label>
              <select
                value={gender}
                onChange={(e) => setGender(e.target.value)}
                className="w-full px-3 py-3 rounded-xl text-sm"
                style={{ border: "1px solid var(--border)", outline: "none" }}
              >
                <option value="nam">Nam</option>
                <option value="nữ">Nữ</option>
              </select>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">Nghề nghiệp</label>
            <input
              type="text"
              value={occupation}
              onChange={(e) => setOccupation(e.target.value)}
              placeholder="VD: bác sĩ, kỹ sư, học sinh..."
              className="w-full px-4 py-3 rounded-xl text-sm"
              style={{ border: "1px solid var(--border)", outline: "none" }}
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">Loại lịch *</label>
            <div className="flex gap-2">
              {(["solar", "lunar"] as const).map((cal) => (
                <button
                  key={cal}
                  type="button"
                  onClick={() => setBirthCalendar(cal)}
                  className="flex-1 py-2 px-3 rounded-xl text-sm font-medium"
                  style={{
                    background: birthCalendar === cal
                      ? "linear-gradient(135deg, #8b5cf6, #ec4899)"
                      : "#f3f4f6",
                    color: birthCalendar === cal ? "white" : "var(--foreground)",
                    border: "1px solid var(--border)",
                  }}
                >
                  {cal === "solar" ? "☀️ Dương lịch" : "🌙 Âm lịch"}
                </button>
              ))}
            </div>
          </div>

          <div className="grid grid-cols-3 gap-3">
            <div>
              <label className="block text-sm font-medium mb-1">Năm *</label>
              <input
                type="number"
                value={birthYear}
                onChange={(e) => setBirthYear(parseInt(e.target.value))}
                className="w-full px-3 py-3 rounded-xl text-sm"
                style={{ border: "1px solid var(--border)", outline: "none" }}
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Tháng</label>
              <input
                type="number"
                value={birthMonth}
                onChange={(e) => setBirthMonth(e.target.value)}
                placeholder="1-12"
                min={1}
                max={12}
                className="w-full px-3 py-3 rounded-xl text-sm"
                style={{ border: "1px solid var(--border)", outline: "none" }}
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Ngày</label>
              <input
                type="number"
                value={birthDay}
                onChange={(e) => setBirthDay(e.target.value)}
                placeholder="1-31"
                min={1}
                max={31}
                className="w-full px-3 py-3 rounded-xl text-sm"
                style={{ border: "1px solid var(--border)", outline: "none" }}
              />
            </div>
          </div>

          {birthCalendar === "lunar" && (
            <label className="flex items-center gap-2 text-sm cursor-pointer">
              <input
                type="checkbox"
                checked={isLeapMonth}
                onChange={(e) => setIsLeapMonth(e.target.checked)}
              />
              <span>Tháng nhuận</span>
            </label>
          )}

          <div className="flex gap-3 pt-2">
            <button
              type="submit"
              className="flex-1 py-3 rounded-xl text-white font-semibold"
              style={{ background: "linear-gradient(135deg, #8b5cf6, #ec4899)" }}
            >
              Lưu thay đổi
            </button>
            <button
              type="button"
              onClick={onClose}
              className="px-6 py-3 rounded-xl font-semibold"
              style={{ background: "#f3f4f6" }}
            >
              Hủy
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

// ============ Saved Analyses View ============

function SavedAnalysesView({
  list,
  detail,
  onOpen,
  onClose,
  onDelete,
}: {
  list: SavedAnalysisSummary[];
  detail: SavedAnalysisDetail | null;
  onOpen: (id: number) => void;
  onClose: () => void;
  onDelete: (id: number) => void;
}) {
  if (detail) {
    return (
      <div>
        <div className="flex items-center justify-between mb-3">
          <div>
            <h2 className="text-lg font-bold">{detail.title || `Phân tích #${detail.id}`}</h2>
            <p className="text-xs" style={{ color: "var(--muted)" }}>
              Lưu lúc {new Date(detail.created_at).toLocaleString("vi-VN")}
            </p>
          </div>
          <button
            onClick={onClose}
            className="px-3 py-1.5 rounded-lg text-sm"
            style={{ background: "#f3f4f6" }}
          >
            ← Quay lại danh sách
          </button>
        </div>
        <AnalysisView analysis={detail.payload} onRefresh={() => {}} />
      </div>
    );
  }

  if (list.length === 0) {
    return (
      <div
        className="text-center py-16 rounded-2xl"
        style={{ border: "2px dashed var(--border)" }}
      >
        <div className="text-4xl mb-3">💾</div>
        <p style={{ color: "var(--muted)" }}>
          Chưa có bản phân tích nào được lưu. Hãy chạy phân tích và bấm
          &quot;Lưu kết quả này&quot;.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {list.map((s) => (
        <div
          key={s.id}
          className="p-4 rounded-2xl flex items-center justify-between"
          style={{ background: "white", border: "1px solid var(--border)" }}
        >
          <div className="flex-1">
            <div className="font-semibold">{s.title || `Phân tích #${s.id}`}</div>
            <div className="text-xs" style={{ color: "var(--muted)" }}>
              {new Date(s.created_at).toLocaleString("vi-VN")}
              {typeof s.family_overall_score === "number" && (
                <> · Điểm: {s.family_overall_score}/100</>
              )}
              {s.analysis_mode && <> · {s.analysis_mode === "online" ? "AI" : "Offline"}</>}
            </div>
            {s.note && (
              <div className="text-xs mt-1" style={{ color: "var(--muted)" }}>{s.note}</div>
            )}
          </div>
          <div className="flex gap-2">
            <button
              onClick={() => onOpen(s.id)}
              className="px-3 py-1.5 rounded-lg text-sm text-white"
              style={{ background: "linear-gradient(135deg, #8b5cf6, #ec4899)" }}
            >
              Xem
            </button>
            <button
              onClick={() => onDelete(s.id)}
              className="px-3 py-1.5 rounded-lg text-sm"
              style={{ background: "#fee2e2", color: "#dc2626" }}
            >
              Xóa
            </button>
          </div>
        </div>
      ))}
    </div>
  );
}
