import type { Metadata } from "next";
import { LegalPage } from "@/components/LegalPage";
import { LAST_UPDATED, paymentSections } from "@/lib/legalPages";

export const metadata: Metadata = {
  title: "Chính sách thanh toán - Tử vi gia đình",
  description: "Chính sách thanh toán cho các tính năng và gói dịch vụ của Tử vi gia đình.",
};

export default function PaymentPolicyPage() {
  return (
    <LegalPage
      title="Chính sách thanh toán"
      description="Thông tin về giá, xác nhận giao dịch, hoàn tiền và hỗ trợ thanh toán của Tử vi gia đình."
      lastUpdated={LAST_UPDATED}
      sections={paymentSections}
    />
  );
}
