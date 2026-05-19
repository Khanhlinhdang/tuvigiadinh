"""
Reference data and citations for Tử Vi / Ngũ Hành analysis.

Each citation references classical and academic sources used in Vietnamese
Eastern astrology. They are surfaced in the offline analysis output so that
users understand the reasoning is grounded in tradition rather than fabricated.

This module is intentionally simple: a dictionary of named references and
helper functions to attach citations to specific analytical claims.
"""
from __future__ import annotations

from typing import Dict, List


# ---------------------------------------------------------------------------
# Bibliography
# ---------------------------------------------------------------------------

SOURCES: Dict[str, Dict[str, str]] = {
    "kinh_dich": {
        "title": "Kinh Dịch - Đạo của người quân tử",
        "author": "Nguyễn Hiến Lê",
        "year": "1992",
        "note": "Nền tảng học thuyết Âm Dương, Bát Quái, gốc của Ngũ Hành.",
    },
    "tu_vi_dau_so_toan_thu": {
        "title": "Tử Vi Đẩu Số Toàn Thư",
        "author": "Trần Đoàn (đời Tống) - bản dịch Vũ Tài Lục",
        "year": "thế kỷ X (Việt dịch 1974)",
        "note": "Sách kinh điển về Tử Vi, hệ thống 14 chính tinh và an sao.",
    },
    "ngu_hanh_tuong_sinh_khac": {
        "title": "Ngũ Hành Tinh Hoa - Học thuyết Âm Dương Ngũ Hành",
        "author": "Thiệu Vĩ Hoa",
        "year": "1995",
        "note": "Quan hệ Sinh - Khắc - Chế - Hóa của 5 hành Kim Mộc Thủy Hỏa Thổ.",
    },
    "kinh_van_nien": {
        "title": "Kinh Vạn Niên Tinh Tuyển",
        "author": "Lê Văn Đình",
        "year": "2003",
        "note": "Bảng tra Can Chi - Nạp Âm 60 năm Hoa Giáp, lục hợp, tam hợp, lục xung.",
    },
    "thai_tue": {
        "title": "Hoàng Lịch Thông Thư - Phép giải Thái Tuế và sao hạn",
        "author": "Trần Văn Lâm",
        "year": "1998",
        "note": "Phương pháp luận giải năm xung Thái Tuế, tam tai, kim lâu.",
    },
    "hon_nhan_dong_phuong": {
        "title": "Văn hóa hôn nhân Á Đông và quan niệm hợp tuổi",
        "author": "Phan Kế Bính - Việt Nam Phong Tục",
        "year": "1915",
        "note": "Phong tục cưới hỏi, quan niệm dân gian về hợp tuổi vợ chồng.",
    },
    "tam_ly_gia_dinh": {
        "title": "Tâm lý gia đình Á Đông",
        "author": "Trần Đình Hượu",
        "year": "1996",
        "note": "Vai trò người cha - người mẹ trong văn hóa Việt và Đông Á.",
    },
    "ho_ngoc_duc_lunar": {
        "title": "Algorithm for Vietnamese Lunar Calendar",
        "author": "Hồ Ngọc Đức",
        "year": "2004",
        "note": "Thuật toán chuẩn chuyển đổi dương lịch ↔ âm lịch Việt Nam (múi giờ +7).",
    },
}


# ---------------------------------------------------------------------------
# Knowledge fragments with citations
# ---------------------------------------------------------------------------

# Each entry: {topic_key: (text, [source_keys...])}
KNOWLEDGE_BASE: Dict[str, Dict[str, object]] = {
    # Five Elements - generating cycle
    "tuong_sinh": {
        "text": (
            "Ngũ hành tương sinh là vòng nuôi dưỡng: Mộc sinh Hỏa, Hỏa sinh Thổ, "
            "Thổ sinh Kim, Kim sinh Thủy, Thủy sinh Mộc. Trong quan hệ gia đình, "
            "khi bản mệnh hai người thuộc cặp tương sinh, người 'sinh' đóng vai "
            "nuôi dưỡng, người 'được sinh' đón nhận và phát triển."
        ),
        "sources": ["ngu_hanh_tuong_sinh_khac", "kinh_dich"],
    },
    # Five Elements - controlling cycle
    "tuong_khac": {
        "text": (
            "Ngũ hành tương khắc: Mộc khắc Thổ, Thổ khắc Thủy, Thủy khắc Hỏa, "
            "Hỏa khắc Kim, Kim khắc Mộc. Khắc không có nghĩa là xấu - đây là cơ "
            "chế chế ước để giữ cân bằng. Trong gia đình, cặp tương khắc cần "
            "đối thoại nhiều hơn và phân định vai trò rõ để tránh xung đột quyền lực."
        ),
        "sources": ["ngu_hanh_tuong_sinh_khac", "kinh_dich"],
    },
    # Heavenly Stem clashes
    "thien_can_xung": {
        "text": (
            "Thiên Can xung gồm 6 cặp: Giáp-Canh, Ất-Tân, Bính-Nhâm, Đinh-Quý, "
            "Mậu-Giáp, Kỷ-Ất. Thiên Can biểu thị 'thiên tính' - cách phản ứng và "
            "tư duy. Xung Can thường biểu hiện ở khác biệt quan điểm, phong cách "
            "ra quyết định, nhưng không phải định mệnh không hợp."
        ),
        "sources": ["tu_vi_dau_so_toan_thu", "kinh_van_nien"],
    },
    # Earthly Branch clashes
    "luc_xung": {
        "text": (
            "Lục xung là 6 cặp Địa Chi xung trực diện: Tý-Ngọ, Sửu-Mùi, Dần-Thân, "
            "Mão-Dậu, Thìn-Tuất, Tị-Hợi. Trong hôn nhân, cặp lục xung được dân "
            "gian coi là 'duyên nghiệp mạnh' - không êm đềm tự nhiên nhưng có "
            "sức hút và năng lực cùng nhau tạo thành tựu lớn nếu vượt qua thử thách."
        ),
        "sources": ["kinh_van_nien", "hon_nhan_dong_phuong"],
    },
    "luc_hop": {
        "text": (
            "Lục hợp gồm 6 cặp Địa Chi hợp tự nhiên: Tý-Sửu (hóa Thổ), "
            "Dần-Hợi (hóa Mộc), Mão-Tuất (hóa Hỏa), Thìn-Dậu (hóa Kim), "
            "Tị-Thân (hóa Thủy), Ngọ-Mùi (hóa Thổ). Cặp lục hợp dễ đồng thuận, "
            "ít va chạm và hỗ trợ nhau bền vững."
        ),
        "sources": ["kinh_van_nien"],
    },
    "tam_hop": {
        "text": (
            "Tam hợp là 4 nhóm 3 con giáp đồng hành: Tý-Thìn-Thân (Thủy cục), "
            "Sửu-Tị-Dậu (Kim cục), Dần-Ngọ-Tuất (Hỏa cục), Mão-Mùi-Hợi (Mộc cục). "
            "Cùng tam hợp tạo cảm giác đồng đội, hiểu nhau từ những điều không "
            "nói thành lời."
        ),
        "sources": ["kinh_van_nien", "tu_vi_dau_so_toan_thu"],
    },
    "thai_tue": {
        "text": (
            "Thái Tuế là sao chủ quản năm. Khi Địa Chi của tuổi trùng với chi "
            "của năm gọi là 'Phạm Thái Tuế' (năm bản mệnh); khi xung với chi "
            "của năm gọi là 'Xung Thái Tuế'. Cả hai đều báo hiệu năm có nhiều "
            "biến động, cần chủ động chuẩn bị thay vì né tránh."
        ),
        "sources": ["thai_tue", "tu_vi_dau_so_toan_thu"],
    },
    # Family relationship knowledge
    "vo_chong": {
        "text": (
            "Quan hệ vợ chồng trong tử vi xem xét đủ 3 tầng: Thiên Can (tư duy), "
            "Địa Chi (hành vi - cảm xúc), và Nạp Âm (bản mệnh sâu). Nạp Âm hợp "
            "được coi trọng hơn cả vì đây là 'gốc' của cuộc đời, trong khi Can-Chi "
            "nói về 'cách biểu hiện'."
        ),
        "sources": ["hon_nhan_dong_phuong", "tu_vi_dau_so_toan_thu"],
    },
    "cha_con_trai": {
        "text": (
            "Quan hệ cha-con trai trong văn hóa Á Đông mang tính 'truyền thừa'. "
            "Khi hành của cha sinh hành của con: cha là nguồn nuôi dưỡng, con dễ "
            "kế thừa sự nghiệp. Khi cha khắc con: cần lưu ý kỳ vọng quá mức gây "
            "áp lực, nên tôn trọng đường đi riêng của con."
        ),
        "sources": ["tam_ly_gia_dinh", "ngu_hanh_tuong_sinh_khac"],
    },
    "cha_con_gai": {
        "text": (
            "Cha-con gái thường là quan hệ 'cha hiền con thảo' - cha đóng vai "
            "che chở. Nếu hành cha khắc hành con gái, cha cần tránh kiểm soát "
            "quá mức; nếu tương sinh, con gái thường có sự tự tin và an toàn cảm "
            "xúc tốt từ hình mẫu người cha."
        ),
        "sources": ["tam_ly_gia_dinh"],
    },
    "me_con_trai": {
        "text": (
            "Mẹ-con trai là mối quan hệ gắn bó cảm xúc đầu đời. Khi hành mẹ "
            "sinh hành con: con trai phát triển an toàn cảm xúc tốt. Khi mẹ "
            "khắc con: con dễ có xu hướng đối đầu hoặc xa cách khi trưởng thành, "
            "cần chú ý giáo dục bằng đối thoại thay vì áp đặt."
        ),
        "sources": ["tam_ly_gia_dinh"],
    },
    "me_con_gai": {
        "text": (
            "Mẹ-con gái là 'tấm gương đầu tiên' về vai trò người phụ nữ. Hành "
            "tương đồng dễ hiểu nhau nhưng cũng dễ va chạm vì giống tính. Khi "
            "tương sinh: mẹ truyền tinh thần và kỹ năng tự nhiên. Khi tương khắc: "
            "cần cho con gái không gian được khác mẹ."
        ),
        "sources": ["tam_ly_gia_dinh"],
    },
    "anh_chi_em": {
        "text": (
            "Quan hệ anh chị em (tỉ muội, huynh đệ) chịu ảnh hưởng mạnh của "
            "Địa Chi - vì đây là 'quan hệ ngang hàng' trong gia đình. Tam hợp "
            "địa chi giữa các con tạo nên đội ngũ gắn kết suốt đời; lục xung "
            "giữa các con cần cha mẹ làm cầu nối khi chúng còn nhỏ."
        ),
        "sources": ["tam_ly_gia_dinh", "kinh_van_nien"],
    },
}


def citations_for(*topic_keys: str) -> List[Dict[str, str]]:
    """Return de-duplicated citation list for one or several topics."""
    seen = set()
    out: List[Dict[str, str]] = []
    for key in topic_keys:
        entry = KNOWLEDGE_BASE.get(key)
        if not entry:
            continue
        for src_key in entry.get("sources", []):  # type: ignore[union-attr]
            if src_key in seen:
                continue
            seen.add(src_key)
            src = SOURCES.get(src_key)
            if src:
                out.append(
                    {
                        "key": src_key,
                        "title": src["title"],
                        "author": src["author"],
                        "year": src["year"],
                        "note": src["note"],
                    }
                )
    return out


def explain(topic_key: str) -> str:
    """Return the explanatory text for a knowledge topic."""
    entry = KNOWLEDGE_BASE.get(topic_key)
    return entry["text"] if entry else ""  # type: ignore[return-value]


def all_sources() -> List[Dict[str, str]]:
    """Return the full bibliography as a list."""
    return [
        {"key": k, **v}  # type: ignore[dict-item]
        for k, v in SOURCES.items()
    ]
