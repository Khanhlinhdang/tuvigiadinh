import Link from "next/link";

type LegalSection = {
  title: string;
  content: string[];
};

type LegalPageProps = {
  title: string;
  description: string;
  lastUpdated: string;
  sections: LegalSection[];
};

export function LegalPage({
  title,
  description,
  lastUpdated,
  sections,
}: LegalPageProps) {
  return (
    <div className="px-4 py-12">
      <article
        className="mx-auto max-w-4xl rounded-3xl p-6 md:p-10"
        style={{
          background: "white",
          border: "1px solid var(--border)",
          boxShadow: "0 8px 30px rgba(139, 92, 246, 0.08)",
        }}
      >
        <Link href="/" className="text-sm font-medium" style={{ color: "var(--primary)" }}>
          ← Về trang chủ
        </Link>
        <header className="mt-6 mb-8">
          <p className="text-sm font-semibold uppercase tracking-wider" style={{ color: "var(--muted)" }}>
            Tử vi gia đình
          </p>
          <h1 className="mt-2 text-3xl md:text-4xl font-bold gradient-text">{title}</h1>
          <p className="mt-4 text-lg" style={{ color: "var(--muted)" }}>
            {description}
          </p>
          <p className="mt-3 text-sm" style={{ color: "var(--muted)" }}>
            Cập nhật lần cuối: {lastUpdated}
          </p>
        </header>

        <div className="space-y-8">
          {sections.map((section) => (
            <section key={section.title}>
              <h2 className="text-xl font-bold mb-3">{section.title}</h2>
              <div className="space-y-3 leading-7" style={{ color: "var(--foreground)" }}>
                {section.content.map((paragraph) => (
                  <p key={paragraph}>{paragraph}</p>
                ))}
              </div>
            </section>
          ))}
        </div>
      </article>
    </div>
  );
}
