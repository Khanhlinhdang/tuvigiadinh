import type { Metadata } from "next";
import { LegalPage } from "@/components/LegalPage";
import { LAST_UPDATED, privacySections } from "@/lib/legalPages";

export const metadata: Metadata = {
  title: "Chính sách bảo mật - Tử vi gia đình",
  description: "Chính sách thu thập, sử dụng và bảo vệ dữ liệu của Tử vi gia đình.",
};

export default function PrivacyPage() {
  return (
    <LegalPage
      title="Chính sách bảo mật"
      description="Cách Tử vi gia đình thu thập, sử dụng, lưu trữ và bảo vệ thông tin người dùng."
      lastUpdated={LAST_UPDATED}
      sections={privacySections}
    />
  );
}
