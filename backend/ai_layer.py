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

    # Build structured prompt
    structured_data = {
        "gia_dinh": family_data["name"],
        "thanh_vien": [
            {
                "ten": m["name"],
                "vai_tro": m["role"],
                "can_chi": f"{m['thien_can']} {m['dia_chi']}",
                "ngu_hanh": m["ngu_hanh"],
                "nap_am": m.get("nap_am", ""),
            }
            for m in family_data["members"]
        ],
        "phan_tich_tuong_hop": [
            {
                "cap": f"{p['member1_name']} - {p['member2_name']}",
                "quan_he": f"{p['member1_role']} - {p['member2_role']}",
                "diem_so": p["overall_score"],
                "muc_do": p["compatibility_level"],
                "chi_tiet": {
                    "can": p["can_compatibility"]["relation"],
                    "chi": p["chi_compatibility"]["primary_relation"],
                    "hanh": p["hanh_compatibility"]["relation"],
                }
            }
            for p in analysis_data["pairs_analysis"]
        ],
        "diem_tong_gia_dinh": analysis_data["family_overall_score"],
    }

    system_prompt = """Bạn là chuyên gia tử vi và tâm lý gia đình Đông phương với hơn 20 năm kinh nghiệm.
Nhiệm vụ của bạn là diễn giải dữ liệu phân tích can chi, ngũ hành gia đình theo cách:
- Khoa học, tích cực, mang tính xây dựng
- Tập trung vào self-awareness và cải thiện quan hệ
- KHÔNG đưa ra tiên tri tiêu cực hay kết luận tuyệt đối
- Đưa ra lời khuyên thực tế, có thể áp dụng được
- Viết bằng tiếng Việt, giọng văn ấm áp, chuyên nghiệp
- Dài khoảng 300-400 từ"""

    user_prompt = f"""Hãy phân tích và diễn giải dữ liệu tử vi gia đình sau:

{json.dumps(structured_data, ensure_ascii=False, indent=2)}

Hãy viết:
1. Tổng quan động lực gia đình (2-3 câu)
2. Điểm mạnh của gia đình này
3. Những thách thức cần chú ý và cách vượt qua
4. Lời khuyên tổng thể cho gia đình"""

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
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
                    "max_tokens": 800
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

    family_context = {
        "gia_dinh": family_data["name"],
        "thanh_vien": [
            {
                "ten": m["name"],
                "vai_tro": m["role"],
                "can_chi": f"{m['thien_can']} {m['dia_chi']}",
                "ngu_hanh": m["ngu_hanh"],
            }
            for m in family_data["members"]
        ]
    }

    system_prompt = """Bạn là AI Cố Vấn Gia Đình chuyên về tử vi và tâm lý Đông phương.
Bạn hiểu sâu về:
- Can Chi, Ngũ Hành và ảnh hưởng đến tính cách
- Dynamics gia đình và quan hệ giữa các thành viên
- Tâm lý hành vi dựa trên tri thức Đông phương

Nguyên tắc trả lời:
- Tích cực, xây dựng, không tiêu cực hay đáng sợ
- Dựa vào dữ liệu can chi thực tế của gia đình
- Đưa ra lời khuyên cụ thể, thực tế
- Viết bằng tiếng Việt, ấm áp và chuyên nghiệp
- Trả lời ngắn gọn (150-250 từ)"""

    user_prompt = f"""Thông tin gia đình:
{json.dumps(family_context, ensure_ascii=False, indent=2)}

Tóm tắt phân tích:
{analysis_context}

Câu hỏi: {question}"""

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
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
                    "max_tokens": 400
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
            lines.append(
                f"* Sinh âm lịch: {m.get('lunar_day','?'):>02}/"
                f"{m.get('lunar_month','?'):>02}/{m.get('lunar_year')}{leap}"
            )
        if m.get("solar_year"):
            lines.append(
                f"* Sinh dương lịch: {m.get('solar_day','?'):>02}/"
                f"{m.get('solar_month','?'):>02}/{m.get('solar_year')}"
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
