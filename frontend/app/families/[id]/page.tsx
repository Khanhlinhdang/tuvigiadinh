"use client";

import { useState, useEffect, use } from "react";
import Link from "next/link";
import { api, Family, FamilyAnalysis, FamilyForecast, FamilyMember } from "@/lib/api";
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

type Tab = "members" | "analysis" | "forecast" | "chat";

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

  const [memberForm, setMemberForm] = useState({
    name: "",
    role: "con",
    gender: "nam",
    birth_year: 1990,
    birth_month: "",
    birth_day: "",
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
        birth_year: memberForm.birth_year,
        birth_month: memberForm.birth_month ? parseInt(memberForm.birth_month) : undefined,
        birth_day: memberForm.birth_day ? parseInt(memberForm.birth_day) : undefined,
      });
      setFamily((prev) =>
        prev ? { ...prev, members: [...prev.members, newMember] } : prev
      );
      setShowAddMember(false);
      setMemberForm({ name: "", role: "con", gender: "nam", birth_year: 1990, birth_month: "", birth_day: "" });
      setAnalysis(null);
    } catch (e: unknown) {
      setError("Không thể thêm thành viên.");
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
    try {
      const data = await api.getFamilyAnalysis(familyId);
      setAnalysis(data);
    } catch (e: unknown) {
      const errMsg = e instanceof Error ? e.message : "Lỗi không xác định";
      setError(`Không thể phân tích: ${errMsg}`);
    } finally {
      setAnalysisLoading(false);
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
      <div className="flex items-center gap-4 mb-6">
        <Link href="/families" className="text-purple-600 hover:underline text-sm">
          ← Danh sách gia đình
        </Link>
        <span style={{ color: "var(--muted)" }}>/</span>
        <h1 className="text-2xl font-bold gradient-text">{family.name}</h1>
      </div>

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
            <div className="text-center py-20">
              <div className="text-4xl mb-4 pulse-soft">🔮</div>
              <p style={{ color: "var(--muted)" }}>Đang phân tích tương hợp...</p>
            </div>
          )}

          {!analysisLoading && analysis && (
            <AnalysisView analysis={analysis} onRefresh={() => { setAnalysis(null); loadAnalysis(); }} />
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
    </div>
  );
}

// ============ Sub Components ============

function MemberCard({ member, onDelete }: { member: FamilyMember; onDelete: () => void }) {
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
            </div>
          </div>
        </div>
        <button
          onClick={onDelete}
          className="text-gray-300 hover:text-red-500 text-sm"
        >
          ✕
        </button>
      </div>

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
    birth_year: number;
    birth_month: string;
    birth_day: string;
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
            <label className="block text-sm font-medium mb-1">Năm sinh *</label>
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
          className="p-6 rounded-2xl"
          style={{ background: "white", border: "1px solid var(--border)" }}
        >
          <h3 className="font-bold text-lg mb-4 flex items-center gap-2">
            <span>🤖</span> Phân Tích AI
          </h3>
          <div
            className="text-sm leading-relaxed whitespace-pre-wrap"
            style={{ color: "var(--foreground)" }}
          >
            {analysis.ai_interpretation}
          </div>
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

function PairDetail({ pair }: { pair: ReturnType<typeof Object.values> extends Array<infer T> ? T : never }) {
  const pairData = pair as {
    member1_name: string;
    member2_name: string;
    member1_role: string;
    member2_role: string;
    member1_can_chi: string;
    member2_can_chi: string;
    overall_score: number;
    compatibility_level: string;
    summary: string;
    recommendations: string[];
    radar_scores: {
      emotional: number;
      communication: number;
      financial: number;
      lifestyle: number;
      stability: number;
    };
    can_compatibility: { relation: string; description: string };
    chi_compatibility: { relations: string[]; description: string };
    hanh_compatibility: { relation: string; description: string };
  };

  const scoreColor = (score: number) => {
    if (score >= 65) return "#22c55e";
    if (score >= 45) return "#f59e0b";
    if (score >= 25) return "#8b5cf6";
    return "#ef4444";
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
        </div>
        <div className="text-right">
          <div className="text-3xl font-bold" style={{ color: scoreColor(pairData.overall_score) }}>
            {pairData.overall_score}
          </div>
          <div className="text-sm font-medium">{pairData.compatibility_level}</div>
        </div>
      </div>

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

      {/* Recommendations */}
      {pairData.recommendations.length > 0 && (
        <div className="mt-5">
          <h4 className="font-semibold mb-3">💡 Khuyến Nghị</h4>
          <div className="space-y-2">
            {pairData.recommendations.map((rec: string, i: number) => (
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

  return (
    <div className="space-y-5 fade-in">
      {/* Family year summary */}
      <div
        className="p-5 rounded-2xl"
        style={{
          background: "linear-gradient(135deg, #1a1a2e, #16213e)",
          color: "white",
        }}
      >
        <div className="text-xl font-bold mb-2">🗓️ Năm {forecast.year} - Tổng Quan</div>
        <p className="text-gray-300">{forecast.family_year_summary}</p>
        <div className="flex gap-4 mt-3 text-sm">
          {forecast.thai_tue_count > 0 && (
            <span className="px-3 py-1 rounded-full" style={{ background: "#a855f730" }}>
              ⚠️ {forecast.thai_tue_count} Thái Tuế
            </span>
          )}
          <span className="px-3 py-1 rounded-full" style={{ background: "#22c55e30" }}>
            ✨ {forecast.positive_count}/{forecast.member_forecasts.length} thuận lợi
          </span>
        </div>
      </div>

      {/* Member forecasts */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {forecast.member_forecasts.map((mf, i) => (
          <div
            key={i}
            className="p-5 rounded-2xl card-hover"
            style={{
              background: "white",
              border: `2px solid ${levelColors[mf.energy_level] || "#8b5cf6"}30`,
            }}
          >
            <div className="flex items-center justify-between mb-3">
              <div>
                <div className="font-bold">{mf.name}</div>
                <div className="text-xs" style={{ color: "var(--muted)" }}>
                  {mf.role} · {mf.birth_can_chi} → {mf.year_can_chi}
                </div>
              </div>
              <span
                className="px-2 py-1 rounded-lg text-xs font-semibold"
                style={{
                  background: `${levelColors[mf.energy_level] || "#8b5cf6"}20`,
                  color: levelColors[mf.energy_level] || "#8b5cf6",
                }}
              >
                {mf.energy_level}
              </span>
            </div>

            {mf.is_thai_tue && (
              <div
                className="mb-2 px-3 py-1.5 rounded-lg text-xs font-semibold"
                style={{ background: "#f3e8ff", color: "#7c3aed" }}
              >
                ⚠️ Năm Thái Tuế - Năm bản mệnh
              </div>
            )}

            <p className="text-sm" style={{ color: "var(--muted)" }}>{mf.forecast}</p>
          </div>
        ))}
      </div>
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
              className="max-w-xs lg:max-w-md px-4 py-3 rounded-2xl text-sm"
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
              <div className="whitespace-pre-wrap">{msg.content}</div>
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
