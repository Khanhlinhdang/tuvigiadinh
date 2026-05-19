import type { Metadata } from "next";
import { LegalPage } from "@/components/LegalPage";
import { LAST_UPDATED, disclaimerSections } from "@/lib/legalPages";

export const metadata: Metadata = {
  title: "Miễn trừ trách nhiệm - Tử vi gia đình",
  description: "Tuyên bố miễn trừ trách nhiệm cho nội dung phân tích của Tử vi gia đình.",
};

export default function DisclaimerPage() {
  return (
    <LegalPage
      title="Miễn trừ trách nhiệm"
      description="Giới hạn trách nhiệm và lưu ý khi sử dụng kết quả phân tích tử vi, tương hợp gia đình và nội dung AI."
      lastUpdated={LAST_UPDATED}
      sections={disclaimerSections}
    />
  );
}
