"""
AI Integration Layer for Tử Vi Gia Đình
Uses OpenAI API with structured prompts for consistent interpretation.

When no OpenAI API key is configured, this module falls back to a rich,
rule-based interpretation engine (offline analysis) that produces the
same multi-section output as the AI version, plus academic citations.
"""
import os
import json
import httpx
from datetime import datetime
from dotenv import load_dotenv

from data_sources import all_sources, citations_for, explain

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")


def has_openai_key() -> bool:
    return bool(OPENAI_API_KEY) and OPENAI_API_KEY.startswith("sk-")


async def get_ai_interpretation(family_data: dict, analysis_data: dict) -> str:
    """
    Get AI interpretation of family compatibility analysis
    Uses structured prompt to ensure consistent, meaningful output
    """
    if not has_openai_key():
        return generate_fallback_interpretation(family_data, analysis_data)

    current_year = datetime.now().year
    year_can_chi = _year_can_chi(current_year)

    def _fmt_date(m: dict) -> str:
        """Format both solar and lunar birth dates if available."""
        parts = []
        if m.get("solar_year") and m.get("solar_month") and m.get("solar_day"):
            parts.append(
                f"dương lịch {m['solar_day']:02d}/{m['solar_month']:02d}/{m['solar_year']}"
            )
        if m.get("lunar_year") and m.get("lunar_month") and m.get("lunar_day"):
            leap = " (nhuận)" if m.get("is_leap_month") else ""
            parts.append(
                f"âm lịch {m['lunar_day']:02d}/{m['lunar_month']:02d}/{m['lunar_year']}{leap}"
            )
        if not parts:
            parts.append(f"năm sinh {m.get('birth_year', '?')}")
        return ", ".join(parts)

    # Build structured prompt with rich member detail
    structured_data = {
        "gia_dinh": family_data["name"],
        "nam_xem": {"nam": current_year, "can_chi": year_can_chi},
        "thanh_vien": [
            {
                "ten": m["name"],
                "vai_tro": m["role"],
                "gioi_tinh": m.get("gender", ""),
                "ngay_sinh": _fmt_date(m),
                "can_chi": f"{m.get('thien_can','')} {m.get('dia_chi','')}".strip(),
                "ngu_hanh_can": m.get("ngu_hanh", ""),
                "nap_am": m.get("nap_am", ""),
                "vai_tro_nang_luong": m.get("energy_role", ""),
            }
            for m in family_data["members"]
        ],
        "phan_tich_tuong_hop": [
            {
                "cap": f"{p['member1_name']} - {p['member2_name']}",
                "loai_quan_he": p.get("relationship_type") or f"{p['member1_role']} - {p['member2_role']}",
                "diem_so": p["overall_score"],
                "muc_do": p["compatibility_level"],
                "thien_can": p["can_compatibility"].get("description") or p["can_compatibility"].get("relation"),
                "dia_chi": p["chi_compatibility"].get("description") or p["chi_compatibility"].get("primary_relation"),
                "ngu_hanh": p["hanh_compatibility"].get("description") or p["hanh_compatibility"].get("relation"),
                "sinh_khac": (p.get("sinh_khac") or {}).get("headline", ""),
            }
            for p in analysis_data.get("pairs_analysis", [])
        ],
        "phan_bo_ngu_hanh": analysis_data.get("energy_distribution", {}),
        "diem_tong_gia_dinh": analysis_data.get("family_overall_score"),
        "tong_quan_dong_luc": analysis_data.get("family_dynamics", ""),
    }

    # Attach this year's forecast snapshot so model can reference vận khí năm
    annual = analysis_data.get("annual_forecast") or {}
    if annual.get("member_forecasts"):
        structured_data["du_bao_nam"] = {
            "nam": annual.get("year", current_year),
            "tom_tat_gia_dinh": annual.get("family_year_summary", ""),
            "tung_thanh_vien": [
                {
                    "ten": mf.get("name"),
                    "vai_tro": mf.get("role"),
                    "ban_menh": mf.get("birth_can_chi"),
                    "nam_can_chi": mf.get("year_can_chi"),
                    "muc_do": mf.get("energy_level"),
                    "thai_tue": mf.get("is_thai_tue"),
                    "xung_nam": mf.get("is_xung"),
                    "tom_tat": mf.get("forecast"),
                }
                for mf in annual["member_forecasts"]
            ],
        }

    system_prompt = (
        "Bạn là chuyên gia tử vi - ngũ hành - thiên can địa chi và tâm lý "
        "gia đình Đông phương với hơn 20 năm kinh nghiệm. Bạn viết phân "
        "tích bằng tiếng Việt theo phong cách kết hợp giữa văn hóa Á Đông "
        "truyền thống và tư duy hiện đại, mạch lạc, ấm áp, có chiều sâu, "
        "tránh tiên tri tuyệt đối hay tiêu cực hoá. Mọi nhận định đều "
        "được dẫn về hành động cụ thể, có thể áp dụng được trong đời sống.\n\n"
        "Bắt buộc:\n"
        "- Trả lời bằng MARKDOWN có cấu trúc rõ (heading #, ##, ###; bullet "
        "  list; bảng |...|; blockquote >; đường ngăn ---).\n"
        "- Phân tích phải dựa đúng vào dữ liệu Can-Chi, Ngũ hành, Nạp âm, "
        "  vai trò, giới tính, độ tuổi của từng thành viên đã cho.\n"
        "- TÙY BIẾN theo cấu trúc gia đình thực tế: số thành viên, vai trò "
        "  (chồng/vợ/con/cha/mẹ/anh/chị/em), giới tính, tuổi để chọn nội "
        "  dung phù hợp - không áp đặt một khuôn mẫu cứng.\n"
        "- Luôn nhắc 'mang tính tham khảo văn hoá - không phải tiên tri "
        "  tuyệt đối' ở phần đầu.\n"
        "- Văn phong xây dựng, tôn trọng, hữu ích."
    )

    user_prompt = f"""Hãy phân tích TOÀN DIỆN tử vi - ngũ hành gia đình dưới đây
dưới góc nhìn tử vi truyền thống, ngũ hành, thiên can - địa chi và quan
niệm dân gian Á Đông. Năm cần phân tích là **{current_year} ({year_can_chi})**.

Dữ liệu gia đình (JSON):
```json
{json.dumps(structured_data, ensure_ascii=False, indent=2)}
```

Yêu cầu cấu trúc bài viết (BẮT BUỘC dùng Markdown, đúng các heading bên dưới,
nhưng TÙY BIẾN nội dung theo dữ liệu thật của gia đình):

# Tổng quan cấu trúc gia đình
- Mô tả ngắn cấu trúc gia đình theo Ngũ hành (ai sinh ai, ai khắc ai),
  điểm đặc biệt (ví dụ: con đóng vai trò cân bằng, bố mẹ xung, v.v.).
- Một câu nhắc tính tham khảo.

# 1. Tổng quan lá số ngũ hành gia đình
Với MỖI thành viên (lặp lại theo vai trò - tên):
## {{Vai trò}} - {{Tên}}
- Sinh: (ngày âm/dương)
- Tuổi: Can Chi
- Mệnh nạp âm
- Tính khí thường (3-6 bullet)
- Nhược điểm (2-4 bullet)

# 2. Tổng vận gia đình năm {current_year} ({year_can_chi})
- Thiên can - Địa chi - Nạp âm của năm
- Bức tranh tổng thể, chu kỳ gia đình đang bước vào.

# 3+. Phân tích chi tiết từng thành viên năm {current_year}
Với MỖI thành viên (chồng, vợ, từng con, hoặc các vai trò khác đang có),
tạo một section riêng (## {{Tên}} - {{Vai trò}}), gồm các tiểu mục:
- ### Vận công việc - sự nghiệp
- ### Tài chính
- ### Tâm sinh lý
- ### Tình cảm / quan hệ
- ### Sức khỏe (lưu ý cơ quan cụ thể theo ngũ hành)
Lưu ý:
- Với trẻ nhỏ, thay "sự nghiệp" bằng "phát triển - giáo dục".
- Tùy giới tính (nam/nữ) và vai trò mà chọn từ ngữ cho phù hợp.

# Quan hệ vợ chồng năm {current_year} (chỉ khi có cặp vợ - chồng)
- Đánh giá theo Thiên Can, Địa Chi, Ngũ hành.
- Biểu hiện dễ gặp, điểm tích cực, lời khuyên cụ thể.

# Quan hệ cha/mẹ - con (nếu có con)
- Phân tích Sinh-Khắc giữa cha-con, mẹ-con từng cặp.

# Quan hệ anh chị em (nếu có ≥ 2 con)
- Phân tích Sinh-Khắc, Lục hợp/Tam hợp, đặc điểm song sinh nếu cùng năm.

# Tài chính gia đình năm {current_year}
# Nhà cửa - môi trường sống năm {current_year}
# Tổng kết vận khí từng thành viên
Trình bày dưới dạng BẢNG Markdown:

| Thành viên | Điểm nổi bật {current_year} |
| --- | --- |
| ... | ... |

# Kết luận toàn diện
- Điểm mạnh lớn nhất
- Thử thách lớn nhất
- 4-6 lời khuyên hành động cụ thể cho cả gia đình

Cuối bài: ghi một dòng in nghiêng nhắc tính tham khảo văn hoá.

QUAN TRỌNG: Văn phong PHẢI thể hiện rõ sự khác biệt giữa các thành viên
dựa trên Can-Chi, Ngũ hành, giới tính và vai trò của họ - không viết
chung chung. Mỗi phần phải có ít nhất 4-6 câu, chi tiết, cụ thể, có
chiều sâu, kèm gợi ý hành động."""

    try:
        async with httpx.AsyncClient(timeout=90.0) as client:
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {OPENAI_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "gpt-4o-mini",
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    "temperature": 0.7,
                    "max_tokens": 3500
                }
            )
            data = response.json()
            if "choices" in data and data["choices"]:
                return data["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"AI API error: {e}")

    return generate_fallback_interpretation(family_data, analysis_data)


async def get_ai_family_chat(family_data: dict, question: str, analysis_context: str) -> str:
    """
    AI Family Advisor chat - answers questions about family dynamics
    """
    if not has_openai_key():
        return generate_fallback_chat_response(question, family_data, analysis_context)

    def _fmt_date(m: dict) -> str:
        parts = []
        if m.get("solar_year") and m.get("solar_month") and m.get("solar_day"):
            parts.append(
                f"DL {m['solar_day']:02d}/{m['solar_month']:02d}/{m['solar_year']}"
            )
        if m.get("lunar_year") and m.get("lunar_month") and m.get("lunar_day"):
            leap = " (nhuận)" if m.get("is_leap_month") else ""
            parts.append(
                f"AL {m['lunar_day']:02d}/{m['lunar_month']:02d}/{m['lunar_year']}{leap}"
            )
        if not parts:
            parts.append(f"năm {m.get('birth_year', '?')}")
        return ", ".join(parts)

    current_year = datetime.now().year

    family_context = {
        "gia_dinh": family_data["name"],
        "nam_hien_tai": current_year,
        "nam_can_chi": _year_can_chi(current_year),
        "so_thanh_vien": len(family_data.get("members", [])),
        "thanh_vien": [
            {
                "ten": m["name"],
                "vai_tro": m["role"],
                "gioi_tinh": m.get("gender", ""),
                "ngay_sinh": _fmt_date(m),
                "can_chi": f"{m.get('thien_can','')} {m.get('dia_chi','')}".strip(),
                "ngu_hanh": m.get("ngu_hanh", ""),
                "nap_am": m.get("nap_am", ""),
                "vai_tro_nang_luong": m.get("energy_role", ""),
            }
            for m in family_data["members"]
        ]
    }

    system_prompt = """Bạn là AI Cố Vấn Gia Đình chuyên về tử vi và tâm lý Đông phương.
Bạn hiểu sâu về:
- Can Chi, Ngũ Hành, Nạp âm và ảnh hưởng đến tính cách, vận khí
- Dynamics gia đình và quan hệ giữa các thành viên dựa trên Sinh - Khắc
- Tâm lý hành vi dựa trên tri thức Đông phương và hiện đại

Nguyên tắc trả lời:
- BẮT BUỘC bám sát dữ liệu Can-Chi, Ngũ hành, nạp âm, giới tính, vai trò, tuổi
  của TỪNG THÀNH VIÊN cụ thể trong gia đình đã cho. Khi đề cập đến một người,
  hãy nhắc tên + can chi + ngũ hành của họ.
- Tích cực, xây dựng, không tiêu cực hay tiên tri tuyệt đối.
- Đưa ra lời khuyên cụ thể, thực tế, có thể áp dụng được.
- Viết bằng Markdown (có bullet, đôi khi heading nhỏ nếu cần) - ấm áp, chuyên nghiệp.
- Trả lời tập trung, không lan man (200-400 từ là vừa)."""

    user_prompt = f"""Thông tin gia đình (BẮT BUỘC dùng làm căn cứ trả lời):
```json
{json.dumps(family_context, ensure_ascii=False, indent=2)}
```

Tóm tắt phân tích đã có:
{analysis_context}

Câu hỏi của người dùng: {question}

Hãy trả lời câu hỏi trên dựa trên dữ liệu thật của gia đình. Nếu câu hỏi
hướng tới một thành viên cụ thể, hãy nêu rõ Can-Chi và Ngũ hành của họ
trong câu trả lời. Nếu hỏi về quan hệ giữa hai người, hãy chỉ ra rõ
hành nào sinh/khắc hành nào, địa chi có xung/hợp gì."""

    try:
        async with httpx.AsyncClient(timeout=45.0) as client:
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {OPENAI_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "gpt-4o-mini",
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    "temperature": 0.7,
                    "max_tokens": 700
                }
            )
            data = response.json()
            if "choices" in data and data["choices"]:
                return data["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"AI API error: {e}")

    return generate_fallback_chat_response(question, family_data, analysis_context)


def generate_fallback_interpretation(family_data: dict, analysis_data: dict) -> str:
    """Generate a rich, kq.md-style rule-based interpretation when no AI is
    available. Output is structured by sections matching the reference
    document and includes academic citations.
    """
    members = family_data.get("members", [])
    score = analysis_data.get("family_overall_score", 50)
    pairs = analysis_data.get("pairs_analysis", [])
    energy_distribution = analysis_data.get("energy_distribution", {}) or {}
    current_year = datetime.now().year

    lines = []
    lines.append(
        f"_Phân tích tử vi gia đình **{family_data.get('name','')}** dưới góc "
        "nhìn ngũ hành, thiên can - địa chi và quan niệm dân gian Á Đông "
        "(mang tính tham khảo văn hóa - tâm linh)._"
    )
    lines.append("")

    # 1. Thông tin cơ bản
    lines.append("## 1. Thông tin cơ bản các thành viên")
    lines.append("")
    for m in members:
        role = (m.get("role") or "").capitalize()
        name = m.get("name", "")
        can_chi = f"{m.get('thien_can','')} {m.get('dia_chi','')}".strip()
        hanh = m.get("ngu_hanh", "")
        nap_am = m.get("nap_am", "")
        lines.append(f"### {role} - {name}")
        if m.get("lunar_year"):
            leap = " (nhuận)" if m.get("is_leap_month") else ""
            ld = m.get("lunar_day")
            lm = m.get("lunar_month")
            ld_s = f"{ld:02d}" if isinstance(ld, int) else "??"
            lm_s = f"{lm:02d}" if isinstance(lm, int) else "??"
            lines.append(
                f"* Sinh âm lịch: {ld_s}/{lm_s}/{m.get('lunar_year')}{leap}"
            )
        if m.get("solar_year"):
            sd = m.get("solar_day")
            sm = m.get("solar_month")
            sd_s = f"{sd:02d}" if isinstance(sd, int) else "??"
            sm_s = f"{sm:02d}" if isinstance(sm, int) else "??"
            lines.append(
                f"* Sinh dương lịch: {sd_s}/{sm_s}/{m.get('solar_year')}"
            )
        if can_chi:
            lines.append(f"* Năm sinh: **{can_chi}**")
        if hanh:
            lines.append(f"* Ngũ hành Thiên Can: **{hanh}**")
        if nap_am:
            lines.append(f"* Nạp âm (bản mệnh sâu): **{nap_am}**")
        lines.append("")

    can_chi_year = _year_can_chi(current_year)
    lines.append(f"### Năm xem hiện tại")
    lines.append(f"* {current_year} = **{can_chi_year}**")
    lines.append("")
    lines.append("---")

    # 2. Đánh giá từng cặp quan hệ với tương sinh / tương khắc
    lines.append("")
    lines.append("## 2. Phân tích tương sinh - tương khắc giữa các mối quan hệ")
    lines.append("")
    if not pairs:
        lines.append("_Chưa đủ thành viên để phân tích các cặp quan hệ._")
    for p in pairs:
        rel_label = p.get("relationship_type") or f"{p.get('member1_role','')} - {p.get('member2_role','')}"
        lines.append(f"### {rel_label}: {p.get('member1_name','')} & {p.get('member2_name','')}")
        lines.append("")
        lines.append(
            f"* Bộ Can Chi: **{p.get('member1_can_chi','')}** ↔ "
            f"**{p.get('member2_can_chi','')}**"
        )
        # Thiên Can
        can_c = p.get("can_compatibility", {})
        if can_c.get("description"):
            lines.append(f"* **Thiên Can**: {can_c.get('description','')}")
        # Địa Chi
        chi_c = p.get("chi_compatibility", {})
        if chi_c.get("description"):
            lines.append(f"* **Địa Chi**: {chi_c.get('description','')}")
        # Sinh khắc bản mệnh
        sk = p.get("sinh_khac", {})
        if sk:
            lines.append(f"* **Ngũ hành bản mệnh**: {sk.get('headline','')}. {sk.get('detail','')}")
        lines.append("")
        # Relationship explanation (knowledge base)
        if p.get("relationship_explanation"):
            lines.append(f"> 📖 {p['relationship_explanation']}")
            lines.append("")
        # Recommendations
        advice = (p.get("relationship_advice") or []) + (p.get("recommendations") or [])
        # de-duplicate
        seen = set()
        unique_advice = []
        for a in advice:
            if a in seen:
                continue
            seen.add(a)
            unique_advice.append(a)
        if unique_advice:
            lines.append("**Khuyến nghị cụ thể:**")
            for a in unique_advice[:5]:
                lines.append(f"- {a}")
            lines.append("")
        # Score
        lines.append(
            f"_Điểm tương hợp cặp này: **{p.get('overall_score',0)}/100** "
            f"({p.get('compatibility_level','')})_"
        )
        lines.append("")

    lines.append("---")

    # 3. Vận khí năm hiện tại (annual snapshot) - if forecast data attached
    forecasts = analysis_data.get("annual_forecast", {}) or {}
    member_forecasts = forecasts.get("member_forecasts") or []
    if member_forecasts:
        lines.append("")
        lines.append(f"## 3. Tổng quan vận khí năm {forecasts.get('year', current_year)}")
        lines.append("")
        for mf in member_forecasts:
            lines.append(
                f"* **{mf.get('name','')}** ({mf.get('role','')}, {mf.get('birth_can_chi','')}): "
                f"{mf.get('energy_level','').capitalize()} - {mf.get('forecast','')}"
            )
        lines.append("")
        lines.append("---")

    # 4. Đánh giá hôn nhân
    couple = next((p for p in pairs if p.get("relationship_key") == "vo_chong"), None)
    if couple:
        lines.append("")
        lines.append("## 4. Đánh giá hôn nhân")
        lines.append("")
        sk = couple.get("sinh_khac", {})
        chi_c = couple.get("chi_compatibility", {})
        if "khac" in (sk.get("type") or "") or chi_c.get("primary_relation") == "xung":
            lines.append(
                "Đây là cặp có yếu tố **thử thách tự nhiên** - không phải kiểu "
                "'đại hợp' êm đềm, nhưng là **duyên nghiệp mạnh** với khả năng "
                "cùng nhau tạo thành tựu lớn nếu cả hai biết nhường nhịn và "
                "trưởng thành về cảm xúc."
            )
        elif "sinh" in (sk.get("type") or ""):
            lines.append(
                "Đây là cặp có **nền tảng tương sinh tự nhiên** - dễ hòa hợp, "
                "bổ trợ và cùng nhau phát triển bền vững."
            )
        else:
            lines.append(
                "Đây là cặp có **nền tảng cân bằng**, vận khí trung tính, "
                "cần chủ động xây dựng giá trị chung."
            )
        lines.append("")
        lines.append("**Biểu hiện thường gặp:**")
        for a in (couple.get("relationship_advice") or [])[:3]:
            lines.append(f"- {a}")
        lines.append("")
        lines.append("---")

    # 5. Quan hệ với con cái (parent-child overview)
    parent_child_pairs = [
        p for p in pairs
        if p.get("relationship_key") in {"cha_con_trai", "cha_con_gai", "me_con_trai", "me_con_gai"}
    ]
    if parent_child_pairs:
        lines.append("")
        lines.append("## 5. Quan hệ cha mẹ - con cái và giáo dục")
        lines.append("")
        for p in parent_child_pairs:
            sk = p.get("sinh_khac", {})
            lines.append(
                f"* **{p.get('relationship_type','')}** ({p.get('member1_name','')} "
                f"& {p.get('member2_name','')}): {sk.get('headline','')}. "
                f"{sk.get('detail','')}"
            )
        lines.append("")
        lines.append("---")

    # 6. Quan hệ giữa các con (sibling)
    sibling_pairs = [p for p in pairs if p.get("relationship_key") == "anh_chi_em"]
    if sibling_pairs:
        lines.append("")
        lines.append("## 6. Quan hệ giữa các con (anh - chị - em)")
        lines.append("")
        for p in sibling_pairs:
            sk = p.get("sinh_khac", {})
            chi_c = p.get("chi_compatibility", {})
            lines.append(
                f"* **{p.get('member1_name','')} & {p.get('member2_name','')}**: "
                f"{sk.get('headline','')}. {chi_c.get('description','')}"
            )
        lines.append("")
        lines.append("---")

    # 7. Phân bố ngũ hành và động lực gia đình
    lines.append("")
    lines.append("## 7. Phân bố ngũ hành trong gia đình")
    lines.append("")
    if energy_distribution:
        for hanh, count in sorted(energy_distribution.items(), key=lambda x: -x[1]):
            lines.append(f"* Hành **{hanh}**: {count} thành viên")
        lines.append("")
        missing = {"Kim", "Mộc", "Thủy", "Hỏa", "Thổ"} - set(energy_distribution.keys())
        if missing:
            lines.append(
                f"_Gia đình thiếu hành: **{', '.join(sorted(missing))}**. "
                "Có thể bổ trợ bằng màu sắc, vật phẩm phong thủy, hoặc lựa chọn "
                "môi trường sống thuận hành đó._"
            )
        lines.append("")
    lines.append(analysis_data.get("family_dynamics", ""))
    lines.append("")
    lines.append("---")

    # 8. Lời khuyên tổng thể
    lines.append("")
    lines.append("## 8. Lời khuyên tổng thể cho gia đình")
    lines.append("")
    if score >= 65:
        lines.append("- Gia đình có nền tảng năng lượng rất tốt. Tận dụng giai đoạn này để củng cố truyền thống chung.")
    elif score >= 45:
        lines.append("- Nền tảng ổn định, có một số điểm cần chú ý. Đối thoại định kỳ là chìa khóa.")
    else:
        lines.append("- Có nhiều khác biệt năng lượng - đây là cơ hội học hỏi lẫn nhau. Cần kiên nhẫn và bao dung.")
    lines.append("- Tôn trọng sự khác biệt về tính cách thay vì áp đặt 'phải giống nhau'.")
    lines.append("- Thực hành 'lời cảm ơn hàng ngày' - mỗi ngày nói một điều trân trọng ở người thân.")
    lines.append("- Tránh quyết định lớn trong các giai đoạn cảm xúc bất ổn.")
    lines.append("")

    # 9. Tổng kết bảng
    lines.append("## 9. Tổng kết")
    lines.append("")
    lines.append("| Mặt | Đánh giá |")
    lines.append("| --- | --- |")
    lines.append(f"| Điểm tổng hợp | {score}/100 |")
    lines.append(f"| Số mối quan hệ phân tích | {len(pairs)} |")
    lines.append(f"| Số hành xuất hiện | {len(energy_distribution)}/5 |")
    if couple:
        sk = couple.get("sinh_khac", {})
        lines.append(f"| Quan hệ vợ chồng | {sk.get('headline','-')} |")
    if parent_child_pairs:
        lines.append(f"| Quan hệ cha mẹ - con | {len(parent_child_pairs)} cặp được phân tích |")
    if sibling_pairs:
        lines.append(f"| Quan hệ giữa các con | {len(sibling_pairs)} cặp |")
    lines.append("")

    # 10. Citations / Sources
    lines.append("## 10. Nguồn dữ liệu & trích dẫn tham khảo")
    lines.append("")
    used_keys = ["tuong_sinh", "tuong_khac", "thien_can_xung", "luc_xung", "luc_hop", "tam_hop", "thai_tue"]
    for p in pairs:
        if p.get("relationship_key") and p["relationship_key"] != "khac":
            used_keys.append(p["relationship_key"])
    citations = citations_for(*used_keys)
    if not citations:
        citations = all_sources()
    for c in citations:
        lines.append(
            f"- **{c['title']}** - {c['author']} ({c['year']}). _{c['note']}_"
        )
    lines.append("")
    lines.append(
        "_Lưu ý: Đây là phân tích offline dựa trên luật ngũ hành - can chi cổ "
        "điển. Kết quả mang tính tham khảo văn hóa, không phải tiên tri tuyệt đối._"
    )

    return "\n".join(lines)


def _year_can_chi(year: int) -> str:
    """Helper: return 'Can Chi' string for a year."""
    try:
        from astrology_engine import THIEN_CAN, DIA_CHI
        return f"{THIEN_CAN[(year - 4) % 10]} {DIA_CHI[(year - 4) % 12]}"
    except Exception:
        return str(year)


def generate_fallback_chat_response(
    question: str,
    family_data: dict | None = None,
    analysis_context: str = "",
) -> str:
    """Offline chat advisor - keyword-based responses grounded in the
    family's actual Can Chi data, with citations. Used when no OpenAI
    API key is configured."""
    family_data = family_data or {}
    members = family_data.get("members", []) or []
    q = (question or "").lower().strip()

    def member_brief(m: dict) -> str:
        return (
            f"{m.get('name','?')} ({m.get('role','?')}, "
            f"{m.get('thien_can','')} {m.get('dia_chi','')} - hành "
            f"{m.get('ngu_hanh','?')})"
        )

    # Topic detection
    topics = []
    if any(k in q for k in ["vợ", "chồng", "hôn nhân", "vợ chồng"]):
        topics.append("vo_chong")
    if any(k in q for k in ["con", "con cái", "con trai", "con gái", "giáo dục"]):
        topics.append("parent_child")
    if any(k in q for k in ["anh", "chị", "em", "anh chị em"]):
        topics.append("siblings")
    if any(k in q for k in ["tài chính", "tiền", "kinh doanh"]):
        topics.append("financial")
    if any(k in q for k in ["sức khỏe", "bệnh", "stress"]):
        topics.append("health")
    if any(k in q for k in ["năm", "vận", "thái tuế", "2024", "2025", "2026"]):
        topics.append("annual")

    parts = []
    parts.append(
        "💡 **Trả lời (chế độ offline - không cần API key):**"
    )
    parts.append("")

    if not members:
        parts.append("Bạn cần thêm thành viên vào gia đình trước khi đặt câu hỏi.")
        return "\n".join(parts)

    parts.append(
        f"Dựa trên dữ liệu Can Chi của gia đình **{family_data.get('name','')}** "
        f"với {len(members)} thành viên:"
    )
    for m in members[:6]:
        parts.append(f"- {member_brief(m)}")
    parts.append("")

    if analysis_context:
        parts.append(f"📊 _{analysis_context}_")
        parts.append("")

    # Add topic-specific knowledge
    citation_keys: list[str] = []
    if "vo_chong" in topics:
        parts.append("**Về quan hệ vợ chồng:**")
        parts.append(explain("vo_chong"))
        citation_keys += ["vo_chong", "tuong_sinh", "tuong_khac"]
        parts.append("")
    if "parent_child" in topics:
        parts.append("**Về quan hệ cha mẹ - con cái:**")
        parts.append(explain("cha_con_trai") + " " + explain("me_con_gai"))
        citation_keys += ["cha_con_trai", "me_con_gai"]
        parts.append("")
    if "siblings" in topics:
        parts.append("**Về quan hệ anh chị em:**")
        parts.append(explain("anh_chi_em"))
        citation_keys += ["anh_chi_em"]
        parts.append("")
    if "annual" in topics:
        parts.append("**Về vận khí năm:**")
        parts.append(explain("thai_tue"))
        citation_keys += ["thai_tue"]
        parts.append("")

    if not citation_keys:
        # Generic guidance
        parts.append(
            "Hệ thống chưa nhận diện rõ chủ đề câu hỏi của bạn. Bạn có thể "
            "hỏi cụ thể về:\n"
            "- Quan hệ vợ chồng / hôn nhân\n"
            "- Quan hệ cha mẹ - con cái, giáo dục con\n"
            "- Anh chị em trong gia đình\n"
            "- Vận khí năm, Thái Tuế, sao hạn\n"
            "- Hợp tuổi - ngũ hành tương sinh / tương khắc"
        )
        citation_keys = ["tuong_sinh", "tuong_khac"]
        parts.append("")

    # Add citations
    parts.append("**📚 Trích dẫn nguồn:**")
    for c in citations_for(*citation_keys):
        parts.append(f"- {c['title']} - {c['author']} ({c['year']})")
    parts.append("")
    parts.append(
        "_Để có phân tích sâu hơn bằng AI, vui lòng cấu hình OPENAI_API_KEY "
        "trong file .env và khởi động lại backend._"
    )

    return "\n".join(parts)
