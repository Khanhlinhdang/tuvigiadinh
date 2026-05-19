import Link from "next/link";

const FEATURES = [
  {
    icon: "🔮",
    title: "Hồ Sơ Can Chi",
    desc: "Tự động tính Thiên Can, Địa Chi, Ngũ Hành và Nạp Âm từ năm sinh.",
  },
  {
    icon: "💞",
    title: "Phân Tích Tương Hợp",
    desc: "Đánh giá tương hợp giữa các thành viên theo lục hợp, tam hợp, lục xung.",
  },
  {
    icon: "��",
    title: "AI Cố Vấn Gia Đình",
    desc: "Đặt câu hỏi và nhận lời khuyên cá nhân hóa từ AI hiểu tử vi Đông phương.",
  },
  {
    icon: "📊",
    title: "Radar Tương Hợp",
    desc: "Biểu đồ trực quan về cảm xúc, giao tiếp, tài chính, lối sống.",
  },
  {
    icon: "🗓️",
    title: "Dự Báo Năm",
    desc: "Phân tích vận khí từng thành viên trong năm, cảnh báo Thái Tuế.",
  },
  {
    icon: "💡",
    title: "Khuyến Nghị Thực Tế",
    desc: "Lời khuyên cụ thể về giao tiếp, tài chính, giáo dục con cái.",
  },
];

const ELEMENTS = [
  { symbol: "木", name: "Mộc", color: "#22c55e", desc: "Phát triển & Sáng tạo" },
  { symbol: "火", name: "Hỏa", color: "#ef4444", desc: "Nhiệt huyết & Cảm xúc" },
  { symbol: "土", name: "Thổ", color: "#f59e0b", desc: "Ổn định & Nền tảng" },
  { symbol: "金", name: "Kim", color: "#a855f7", desc: "Quyết đoán & Kỷ luật" },
  { symbol: "水", name: "Thủy", color: "#3b82f6", desc: "Trí tuệ & Linh hoạt" },
];

export default function HomePage() {
  return (
    <div>
      {/* Hero Section */}
      <section
        className="relative py-24 px-4 text-center overflow-hidden"
        style={{
          background: "linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%)",
        }}
      >
        <div
          className="absolute top-10 left-10 w-64 h-64 rounded-full opacity-10"
          style={{ background: "radial-gradient(circle, #8b5cf6, transparent)" }}
        />
        <div
          className="absolute bottom-10 right-10 w-96 h-96 rounded-full opacity-10"
          style={{ background: "radial-gradient(circle, #ec4899, transparent)" }}
        />

        <div className="relative z-10 max-w-4xl mx-auto">
          <div className="text-6xl mb-4">☯️</div>
          <h1 className="text-4xl md:text-6xl font-bold text-white mb-4">
            Tử Vi{" "}
            <span
              style={{
                background: "linear-gradient(135deg, #a78bfa, #f472b6)",
                WebkitBackgroundClip: "text",
                WebkitTextFillColor: "transparent",
                backgroundClip: "text",
              }}
            >
              Gia Đình
            </span>
          </h1>
          <p className="text-xl text-gray-300 mb-2">
            Hệ thống phân tích quan hệ và vận khí gia đình
          </p>
          <p className="text-base text-gray-400 mb-10 max-w-2xl mx-auto">
            Kết hợp tri thức Can Chi – Ngũ Hành Đông phương với AI hiện đại để
            hiểu sâu hơn về động lực gia đình, tương hợp giữa các thành viên và
            hướng dẫn phát triển quan hệ bền vững.
          </p>

          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link
              href="/families"
              className="px-8 py-4 rounded-xl text-lg font-semibold text-white transition-transform hover:scale-105"
              style={{
                background: "linear-gradient(135deg, #8b5cf6, #ec4899)",
                boxShadow: "0 4px 20px rgba(139, 92, 246, 0.4)",
              }}
            >
              🏠 Tạo Hồ Sơ Gia Đình
            </Link>
          </div>
        </div>
      </section>

      {/* Five Elements Section */}
      <section className="py-12 px-4" style={{ background: "#f8f4ff" }}>
        <div className="max-w-4xl mx-auto">
          <h2 className="text-center text-xl font-semibold mb-8" style={{ color: "var(--muted)" }}>
            Nền tảng Ngũ Hành
          </h2>
          <div className="flex flex-wrap justify-center gap-4">
            {ELEMENTS.map((el) => (
              <div
                key={el.name}
                className="flex flex-col items-center p-4 rounded-2xl w-28"
                style={{
                  background: "white",
                  border: `2px solid ${el.color}20`,
                  boxShadow: `0 4px 15px ${el.color}15`,
                }}
              >
                <div className="text-3xl font-bold mb-1" style={{ color: el.color }}>
                  {el.symbol}
                </div>
                <div className="font-semibold text-sm">{el.name}</div>
                <div className="text-xs text-center mt-1" style={{ color: "var(--muted)" }}>
                  {el.desc}
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-16 px-4">
        <div className="max-w-6xl mx-auto">
          <h2 className="text-3xl font-bold text-center mb-4">
            <span className="gradient-text">Tính Năng Hệ Thống</span>
          </h2>
          <p className="text-center mb-12" style={{ color: "var(--muted)" }}>
            Phân tích toàn diện từ cá nhân đến tổng thể gia đình
          </p>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {FEATURES.map((feature) => (
              <div
                key={feature.title}
                className="p-6 rounded-2xl card-hover"
                style={{
                  background: "white",
                  border: "1px solid var(--border)",
                  boxShadow: "0 2px 8px rgba(0,0,0,0.05)",
                }}
              >
                <div className="text-3xl mb-3">{feature.icon}</div>
                <h3 className="font-bold text-lg mb-2">{feature.title}</h3>
                <p style={{ color: "var(--muted)" }}>{feature.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* How it works */}
      <section
        className="py-16 px-4"
        style={{ background: "linear-gradient(135deg, #f8f4ff, #fff0f6)" }}
      >
        <div className="max-w-4xl mx-auto">
          <h2 className="text-3xl font-bold text-center mb-12">
            <span className="gradient-text">Cách Sử Dụng</span>
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {[
              {
                step: "1",
                icon: "👨‍👩‍👧‍👦",
                title: "Tạo Hồ Sơ Gia Đình",
                desc: "Nhập thông tin các thành viên: tên, vai trò, giới tính và năm sinh",
              },
              {
                step: "2",
                icon: "🔬",
                title: "Phân Tích Tự Động",
                desc: "Hệ thống tính toán Can Chi, Ngũ Hành và phân tích tương hợp cho mọi cặp quan hệ",
              },
              {
                step: "3",
                icon: "💡",
                title: "Nhận Khuyến Nghị",
                desc: "Đọc phân tích AI và áp dụng lời khuyên thực tế để cải thiện quan hệ gia đình",
              },
            ].map((step) => (
              <div key={step.step} className="text-center">
                <div
                  className="w-16 h-16 rounded-full flex items-center justify-center text-2xl mx-auto mb-4"
                  style={{
                    background: "linear-gradient(135deg, #8b5cf6, #ec4899)",
                    boxShadow: "0 4px 15px rgba(139, 92, 246, 0.3)",
                  }}
                >
                  {step.icon}
                </div>
                <div
                  className="text-xs font-bold uppercase tracking-wider mb-2"
                  style={{ color: "#8b5cf6" }}
                >
                  Bước {step.step}
                </div>
                <h3 className="font-bold text-lg mb-2">{step.title}</h3>
                <p style={{ color: "var(--muted)" }}>{step.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-16 px-4 text-center">
        <div className="max-w-2xl mx-auto">
          <h2 className="text-3xl font-bold mb-4">
            Bắt đầu phân tích gia đình của bạn
          </h2>
          <p className="mb-8" style={{ color: "var(--muted)" }}>
            Miễn phí hoàn toàn. Không cần đăng ký.
          </p>
          <Link
            href="/families"
            className="inline-block px-10 py-4 rounded-xl text-lg font-semibold text-white transition-transform hover:scale-105"
            style={{
              background: "linear-gradient(135deg, #8b5cf6, #ec4899)",
              boxShadow: "0 4px 20px rgba(139, 92, 246, 0.4)",
            }}
          >
            🚀 Bắt Đầu Ngay
          </Link>
        </div>
      </section>
    </div>
  );
}
