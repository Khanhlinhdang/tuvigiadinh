import type { Metadata } from "next";
import { LegalPage } from "@/components/LegalPage";
import { LAST_UPDATED, termsSections } from "@/lib/legalPages";

export const metadata: Metadata = {
  title: "Điều khoản dịch vụ - Tử vi gia đình",
  description: "Điều khoản sử dụng dịch vụ Tử vi gia đình.",
};

export default function TermsPage() {
  return (
    <LegalPage
      title="Điều khoản dịch vụ"
      description="Các quy định khi truy cập và sử dụng nền tảng Tử vi gia đình."
      lastUpdated={LAST_UPDATED}
      sections={termsSections}
    />
  );
}
