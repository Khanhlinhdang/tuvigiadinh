"""
Family Compatibility Engine
Analyzes relationships between family members
"""
from astrology_engine import (
    analyze_can_compatibility,
    analyze_chi_compatibility,
    analyze_hanh_compatibility,
    get_personality_traits,
    get_energy_role,
    calculate_annual_energy,
    TUONG_SINH,
    TUONG_KHAC,
)
from data_sources import citations_for, explain
from typing import List, Dict

MAX_EXECUTIVE_STRENGTHS = 3
MAX_EXECUTIVE_RISKS = 3
MAX_EXECUTIVE_ACTIONS = 5


def get_compatibility_level(score: int) -> str:
    """Convert numeric score to compatibility level"""
    if score >= 60:
        return "Rất tốt ✨"
    elif score >= 35:
        return "Tốt 👍"
    elif score >= 10:
        return "Trung bình 📊"
    elif score >= -10:
        return "Cần chú ý ⚠️"
    else:
        return "Thách thức 🔥"


def get_relationship_recommendations(
    member1: dict, member2: dict,
    can_compat: dict, chi_compat: dict, hanh_compat: dict
) -> List[str]:
    """Generate actionable recommendations based on compatibility analysis"""
    recommendations = []
    role1, role2 = member1["role"], member2["role"]
    hanh1 = member1.get("ngu_hanh", "")
    hanh2 = member2.get("ngu_hanh", "")
    chi1 = member1.get("dia_chi", "")
    chi2 = member2.get("dia_chi", "")

    # Role-specific recommendations
    if set([role1, role2]) == {"chồng", "vợ"}:
        recommendations.append("Dành thời gian chất lượng ít nhất 30 phút mỗi ngày để nói chuyện không liên quan đến công việc hay con cái")

        if chi_compat["primary_relation"] in ["xung", "thách thức"]:
            recommendations.append("Thiết lập 'quy tắc tranh luận': không nói chuyện lớn sau 9 giờ tối, không ngắt lời nhau")
            recommendations.append("Mỗi tháng tổ chức một buổi 'date night' để tái kết nối cảm xúc")

        if hanh_compat["score"] < 0:
            recommendations.append("Phân chia vai trò rõ ràng: ai quản lý tài chính, ai quyết định lớn, để tránh xung đột về quyền lực")

    elif "con" in [role1, role2]:
        parent_role = role1 if role2 == "con" else role2
        parent = member1 if member2["role"] == "con" else member2
        child = member2 if member2["role"] == "con" else member1

        child_hanh = child.get("ngu_hanh", "")
        parent_hanh = parent.get("ngu_hanh", "")

        if child_hanh == "Kim":
            recommendations.append(f"Bé {child['name']} hành Kim: cần môi trường có kỷ luật rõ ràng, công bằng và nhất quán")
            recommendations.append("Khuyến khích các hoạt động thể thao, âm nhạc hoặc nghệ thuật để phát triển cảm xúc")
        elif child_hanh == "Hỏa":
            recommendations.append(f"Bé {child['name']} hành Hỏa: rất năng động, cần kênh giải phóng năng lượng như thể thao, nghệ thuật")
            recommendations.append("Dạy con cách kiểm soát cảm xúc qua thiền, yoga thiếu nhi hoặc hoạt động sáng tạo")
        elif child_hanh == "Mộc":
            recommendations.append(f"Bé {child['name']} hành Mộc: có tư duy độc lập, cần được tôn trọng ý kiến và có không gian riêng")
        elif child_hanh == "Thủy":
            recommendations.append(f"Bé {child['name']} hành Thủy: thông minh và thích nghi tốt, phát triển tốt trong môi trường linh hoạt")
        elif child_hanh == "Thổ":
            recommendations.append(f"Bé {child['name']} hành Thổ: cần sự ổn định và nhất quán trong giáo dục, ghét thay đổi đột ngột")

        if hanh_compat["score"] < 0:
            recommendations.append("Tránh áp đặt kỳ vọng quá cao, thay vào đó tìm hiểu thế mạnh tự nhiên của con")

    elif set([role1, role2]) & {"anh", "chị", "em"}:
        if chi_compat["primary_relation"] in ["xung", "thách thức"]:
            recommendations.append("Thiết lập 'giờ gia đình' chung như bữa ăn tối không có điện thoại để tăng kết nối")
        recommendations.append("Khuyến khích anh/chị/em cùng tham gia hoạt động chung ít nhất 1 lần/tuần")

    # General recommendations based on elements
    if hanh1 and hanh2:
        if {hanh1, hanh2} == {"Hỏa", "Thủy"}:
            recommendations.append("Hành Hỏa và Thủy cần học cách cân bằng: người Hỏa cần kiên nhẫn hơn, người Thủy cần cởi mở hơn")
        elif {hanh1, hanh2} == {"Kim", "Mộc"}:
            recommendations.append("Hành Kim và Mộc: cần tìm điểm chung qua các hoạt động thực tế, tránh tranh luận trừu tượng")

    # Always add a positive recommendation
    recommendations.append("Thực hành 'lời cảm ơn hàng ngày': mỗi ngày nói một điều bạn trân trọng ở người kia")

    return recommendations[:4]  # Return max 4 recommendations


def classify_relationship(member1: dict, member2: dict) -> dict:
    """Classify the relationship type between two family members.

    Returns a dict with:
      - relation_key: one of vo_chong / cha_con_trai / cha_con_gai /
        me_con_trai / me_con_gai / anh_chi_em / khac
      - relation_label: human-readable Vietnamese label
      - knowledge_key: data_sources knowledge base key to use for citations
    """
    r1, r2 = member1.get("role", ""), member2.get("role", "")
    g1, g2 = member1.get("gender", ""), member2.get("gender", "")
    roles = {r1, r2}

    if roles == {"chồng", "vợ"}:
        return {
            "relation_key": "vo_chong",
            "relation_label": "Vợ - Chồng",
            "knowledge_key": "vo_chong",
        }

    if "con" in roles and ({"cha", "bố"} & roles):
        # Determine child gender
        child_gender = g1 if r1 == "con" else g2
        if child_gender == "nam":
            return {
                "relation_key": "cha_con_trai",
                "relation_label": "Cha - Con trai",
                "knowledge_key": "cha_con_trai",
            }
        return {
            "relation_key": "cha_con_gai",
            "relation_label": "Cha - Con gái",
            "knowledge_key": "cha_con_gai",
        }

    if "con" in roles and "mẹ" in roles:
        child_gender = g1 if r1 == "con" else g2
        if child_gender == "nam":
            return {
                "relation_key": "me_con_trai",
                "relation_label": "Mẹ - Con trai",
                "knowledge_key": "me_con_trai",
            }
        return {
            "relation_key": "me_con_gai",
            "relation_label": "Mẹ - Con gái",
            "knowledge_key": "me_con_gai",
        }

    if roles & {"anh", "chị", "em"} and len(roles - {"anh", "chị", "em"}) == 0:
        return {
            "relation_key": "anh_chi_em",
            "relation_label": "Anh - Chị - Em",
            "knowledge_key": "anh_chi_em",
        }

    if roles == {"con"}:
        # Both are children of the same family
        return {
            "relation_key": "anh_chi_em",
            "relation_label": "Anh - Chị - Em (con cái)",
            "knowledge_key": "anh_chi_em",
        }

    return {
        "relation_key": "khac",
        "relation_label": f"{r1.capitalize()} - {r2.capitalize()}",
        "knowledge_key": "",
    }


def describe_sinh_khac(hanh1: str, hanh2: str, name1: str, name2: str) -> dict:
    """Produce a detailed Tương Sinh / Tương Khắc description between two
    five-element values. Returns dict with keys: type, headline, detail."""
    if not hanh1 or not hanh2:
        return {"type": "unknown", "headline": "Chưa đủ dữ liệu", "detail": ""}

    if hanh1 == hanh2:
        return {
            "type": "tuong_ty",
            "headline": f"Tương tỷ - cùng hành {hanh1}",
            "detail": (
                f"{name1} và {name2} cùng hành {hanh1}, tính cách có nhiều "
                "điểm tương đồng - dễ hiểu nhau nhưng cũng dễ va chạm vì "
                "thiếu sự bổ sung. Cần chủ động tạo khác biệt để bổ trợ nhau."
            ),
        }

    if TUONG_SINH.get(hanh1) == hanh2:
        return {
            "type": "tuong_sinh_xuoi",
            "headline": f"Tương sinh thuận: {hanh1} sinh {hanh2}",
            "detail": (
                f"{name1} ({hanh1}) là nguồn nuôi dưỡng cho {name2} ({hanh2}). "
                f"{name1} đóng vai trò người dẫn dắt, truyền năng lượng; "
                f"{name2} hấp thu và phát triển. Đây là quan hệ rất tốt cho "
                "sự phát triển dài hạn."
            ),
        }

    if TUONG_SINH.get(hanh2) == hanh1:
        return {
            "type": "tuong_sinh_nguoc",
            "headline": f"Tương sinh nghịch: {hanh2} sinh {hanh1}",
            "detail": (
                f"{name2} ({hanh2}) là nguồn nuôi dưỡng cho {name1} ({hanh1}). "
                f"{name2} có xu hướng hi sinh, hỗ trợ {name1}. Cần đảm bảo sự "
                "trao đổi cân bằng để bên 'sinh' không bị kiệt sức."
            ),
        }

    if TUONG_KHAC.get(hanh1) == hanh2:
        return {
            "type": "tuong_khac_xuoi",
            "headline": f"Tương khắc: {hanh1} khắc {hanh2}",
            "detail": (
                f"{name1} ({hanh1}) có xu hướng chế ngự hoặc kiểm soát "
                f"{name2} ({hanh2}). Đây không hẳn là điều xấu - khắc là cơ chế "
                "giữ cân bằng. Tuy nhiên cần lưu ý: bên 'khắc' nên giảm áp đặt, "
                "bên 'bị khắc' cần giữ ranh giới cá nhân."
            ),
        }

    if TUONG_KHAC.get(hanh2) == hanh1:
        return {
            "type": "tuong_khac_nguoc",
            "headline": f"Bị khắc: {hanh2} khắc {hanh1}",
            "detail": (
                f"{name2} ({hanh2}) có ảnh hưởng mạnh - đôi khi áp đảo - lên "
                f"{name1} ({hanh1}). {name1} nên tự tin giữ vững bản sắc của "
                "mình, không để bị cuốn theo."
            ),
        }

    return {
        "type": "binh_hoa",
        "headline": "Bình hòa",
        "detail": (
            f"Hành {hanh1} và {hanh2} không có quan hệ sinh khắc trực tiếp - "
            "quan hệ trung tính, ổn định, cần chủ động tạo giá trị chung."
        ),
    }


def relationship_specific_advice(
    relation_key: str,
    sinh_khac: dict,
    chi_compat: dict,
    member1: dict,
    member2: dict,
) -> List[str]:
    """Produce role-specific actionable advice based on relationship type
    and the Sinh-Khắc result."""
    advice: List[str] = []
    sk_type = sinh_khac.get("type", "")

    if relation_key == "vo_chong":
        if "khac" in sk_type:
            advice.append(
                "Bản mệnh tương khắc: phân chia rõ vai trò 'người quyết định "
                "chính' cho từng lĩnh vực (tài chính, giáo dục con, đối ngoại) "
                "để giảm va chạm quyền lực."
            )
            advice.append(
                "Tránh tranh luận khi cả hai đang đói, mệt hoặc sau 22h - "
                "tương khắc dễ bùng phát ở các thời điểm năng lượng thấp."
            )
        elif "sinh" in sk_type:
            advice.append(
                "Bản mệnh tương sinh: tận dụng bằng cách cùng học, cùng đầu "
                "tư hoặc cùng phát triển một dự án dài hạn - năng lượng sẽ "
                "cộng hưởng rất mạnh."
            )
        if chi_compat.get("primary_relation") == "xung":
            advice.append(
                "Địa chi xung (Tý-Ngọ, Mão-Dậu...): mỗi tháng nên có 1-2 "
                "ngày 'reset' riêng cho từng người để giữ không gian cá nhân."
            )

    elif relation_key in ("cha_con_trai", "cha_con_gai"):
        if "khac" in sk_type:
            advice.append(
                "Người cha cần ý thức không 'truyền áp lực kỳ vọng' lên con - "
                "tương khắc dễ biến thành đối đầu khi con bước vào tuổi vị thành niên."
            )
            advice.append(
                "Dành thời gian 1-1 với con (đi dạo, ăn sáng riêng) tối thiểu "
                "1 lần/tuần để duy trì kênh đối thoại."
            )
        elif "sinh" in sk_type:
            advice.append(
                "Tương sinh cha-con: người cha là 'kim chỉ nam' tự nhiên. "
                "Hãy chủ động chia sẻ kinh nghiệm nghề nghiệp, đạo đức sống."
            )
        if relation_key == "cha_con_gai":
            advice.append(
                "Cha-con gái: hình mẫu người cha ảnh hưởng tới cách con gái "
                "chọn bạn đời sau này. Hãy luôn thể hiện sự tôn trọng phụ nữ "
                "trong gia đình."
            )

    elif relation_key in ("me_con_trai", "me_con_gai"):
        if "khac" in sk_type:
            advice.append(
                "Mẹ và con tương khắc: tránh giáo dục bằng cách so sánh "
                "(với con nhà khác, với anh chị) - dễ tạo tổn thương sâu."
            )
        elif "sinh" in sk_type:
            advice.append(
                "Tương sinh mẹ-con: gắn bó cảm xúc sâu sắc. Lưu ý cân bằng "
                "để con vẫn phát triển tính tự lập, tránh phụ thuộc cảm xúc."
            )
        if relation_key == "me_con_gai" and sinh_khac.get("type") == "tuong_ty":
            advice.append(
                "Mẹ-con gái cùng hành: dễ va chạm vì tính giống nhau. Hãy "
                "cho con gái không gian để khác mẹ, tránh áp đặt 'phải giống mẹ'."
            )

    elif relation_key == "anh_chi_em":
        if chi_compat.get("primary_relation") == "tam hợp":
            advice.append(
                "Anh chị em tam hợp địa chi: đây là 'đội ngũ' tự nhiên - "
                "khuyến khích các con cùng tham gia hoạt động chung, "
                "lập 'truyền thống của các anh em'."
            )
        if "khac" in sk_type or chi_compat.get("primary_relation") == "xung":
            advice.append(
                "Anh chị em có yếu tố xung khắc: cha mẹ cần đóng vai 'người "
                "phân xử công bằng', không thiên vị, không so sánh giữa các con."
            )

    return advice


def analyze_pair(member1: dict, member2: dict) -> dict:
    """Analyze compatibility between two family members"""
    can1 = member1.get("thien_can", "")
    can2 = member2.get("thien_can", "")
    chi1 = member1.get("dia_chi", "")
    chi2 = member2.get("dia_chi", "")
    hanh1 = member1.get("ngu_hanh", "")
    hanh2 = member2.get("ngu_hanh", "")

    can_compat = analyze_can_compatibility(can1, can2)
    chi_compat = analyze_chi_compatibility(chi1, chi2)
    hanh_compat = analyze_hanh_compatibility(hanh1, hanh2)

    # Calculate overall score (0-100 base + adjustments)
    base_score = 50
    total_adjustment = can_compat["score"] + chi_compat["score"] + hanh_compat["score"]
    overall_score = max(0, min(100, base_score + total_adjustment))

    compatibility_level = get_compatibility_level(overall_score)
    recommendations = get_relationship_recommendations(
        member1, member2, can_compat, chi_compat, hanh_compat
    )

    # Build summary
    summary_parts = []
    if can_compat["description"]:
        summary_parts.append(can_compat["description"])
    if chi_compat["description"]:
        summary_parts.append(chi_compat["description"])
    if hanh_compat["description"]:
        summary_parts.append(hanh_compat["description"])

    summary = " | ".join(summary_parts) if summary_parts else "Vận khí trung bình, ổn định."

    # Radar chart scores
    radar_scores = calculate_radar_scores(member1, member2, can_compat, chi_compat, hanh_compat)

    # Deep relationship classification (vợ-chồng, cha-con, mẹ-con, anh-chị-em)
    relation_info = classify_relationship(member1, member2)
    sinh_khac = describe_sinh_khac(
        hanh1, hanh2, member1.get("name", ""), member2.get("name", "")
    )
    relationship_advice = relationship_specific_advice(
        relation_info["relation_key"], sinh_khac, chi_compat, member1, member2
    )
    knowledge_key = relation_info.get("knowledge_key") or ""
    relationship_explanation = explain(knowledge_key) if knowledge_key else ""
    citation_keys = [k for k in [knowledge_key, "tuong_sinh", "tuong_khac"] if k]
    pair_citations = citations_for(*citation_keys)

    return {
        "member1_id": member1["id"],
        "member2_id": member2["id"],
        "member1_name": member1["name"],
        "member2_name": member2["name"],
        "member1_role": member1["role"],
        "member2_role": member2["role"],
        "member1_can_chi": f"{can1} {chi1}",
        "member2_can_chi": f"{can2} {chi2}",
        "can_compatibility": can_compat,
        "chi_compatibility": chi_compat,
        "hanh_compatibility": hanh_compat,
        "overall_score": overall_score,
        "compatibility_level": compatibility_level,
        "summary": summary,
        "recommendations": recommendations,
        "radar_scores": radar_scores,
        "relationship_type": relation_info["relation_label"],
        "relationship_key": relation_info["relation_key"],
        "sinh_khac": sinh_khac,
        "relationship_advice": relationship_advice,
        "relationship_explanation": relationship_explanation,
        "citations": pair_citations,
    }


def calculate_radar_scores(
    member1: dict, member2: dict,
    can_compat: dict, chi_compat: dict, hanh_compat: dict
) -> dict:
    """Calculate radar chart scores for different relationship dimensions"""
    # Base scores from compatibility
    base = 50
    hanh_adj = hanh_compat["score"]
    chi_adj = chi_compat["score"]
    can_adj = can_compat["score"]

    # Emotional compatibility (mainly chi-based)
    emotional = max(10, min(100, base + chi_adj * 1.2 + can_adj * 0.5))

    # Communication (can-based + chi)
    communication = max(10, min(100, base + can_adj * 1.2 + chi_adj * 0.3))

    # Financial (hanh-based)
    financial = max(10, min(100, base + hanh_adj * 1.5))

    # Lifestyle harmony (chi-based)
    lifestyle = max(10, min(100, base + chi_adj * 0.8 + hanh_adj * 0.5))

    # Long-term stability (hanh + chi)
    stability = max(10, min(100, base + (hanh_adj + chi_adj) * 0.6))

    return {
        "emotional": round(emotional),
        "communication": round(communication),
        "financial": round(financial),
        "lifestyle": round(lifestyle),
        "stability": round(stability),
    }


def analyze_family(members: List[dict]) -> dict:
    """Analyze all relationships in a family"""
    if len(members) < 2:
        return {
            "pairs_analysis": [],
            "family_overall_score": 50,
            "family_dynamics": "Cần ít nhất 2 thành viên để phân tích quan hệ gia đình.",
            "energy_distribution": {},
            "executive_summary": {
                "strengths": [],
                "risks": [],
                "actions": ["Thêm ít nhất 2 thành viên để bắt đầu phân tích tương hợp."],
                "energy_keeper": None,
                "best_pair": None,
                "attention_pair": None,
                "positioning_note": "Kết quả mang tính tham khảo văn hoá, hỗ trợ hiểu nhau và cải thiện giao tiếp gia đình.",
            },
        }

    pairs_analysis = []

    # Analyze all pairs
    for i in range(len(members)):
        for j in range(i + 1, len(members)):
            pair_result = analyze_pair(members[i], members[j])
            pairs_analysis.append(pair_result)

    # Calculate family overall score
    if pairs_analysis:
        avg_score = sum(p["overall_score"] for p in pairs_analysis) / len(pairs_analysis)
        family_overall_score = round(avg_score)
    else:
        family_overall_score = 50

    # Analyze energy distribution
    energy_distribution = {}
    for member in members:
        hanh = member.get("ngu_hanh", "Không rõ")
        energy_distribution[hanh] = energy_distribution.get(hanh, 0) + 1

    # Determine family dynamics
    family_dynamics = determine_family_dynamics(members, pairs_analysis, energy_distribution)

    # Find energy roles
    energy_roles = []
    for member in members:
        role = get_energy_role(
            member.get("thien_can", ""),
            member.get("dia_chi", ""),
            {"can_hanh": member.get("ngu_hanh", "")}
        )
        energy_roles.append({"name": member["name"], "role": role})

    executive_summary = build_executive_summary(
        members, pairs_analysis, family_overall_score, energy_distribution, energy_roles
    )

    return {
        "pairs_analysis": pairs_analysis,
        "family_overall_score": family_overall_score,
        "family_dynamics": family_dynamics,
        "energy_distribution": energy_distribution,
        "energy_roles": energy_roles,
        "executive_summary": executive_summary,
    }


def _pair_summary(pair: dict | None) -> dict | None:
    if not pair:
        return None
    sinh_khac = pair.get("sinh_khac") or {}
    return {
        "member1_name": pair.get("member1_name", ""),
        "member2_name": pair.get("member2_name", ""),
        "relationship_type": pair.get("relationship_type", ""),
        "overall_score": pair.get("overall_score", 0),
        "compatibility_level": pair.get("compatibility_level", ""),
        "headline": sinh_khac.get("headline") or pair.get("summary", ""),
    }


def _sinh_khac_type(pair: dict) -> str:
    sinh_khac = pair.get("sinh_khac")
    if not isinstance(sinh_khac, dict):
        return ""
    value = sinh_khac.get("type")
    return value if isinstance(value, str) else ""


def build_executive_summary(
    members: List[dict],
    pairs_analysis: List[dict],
    family_overall_score: int,
    energy_distribution: dict,
    energy_roles: List[dict],
) -> dict:
    """Build a short, UI-friendly summary that is cheap to compute.

    This gives users quick value before reading the long AI/offline report and
    reduces the need to repeatedly call the AI just to understand the result.
    """
    best_pair = max(pairs_analysis, key=lambda p: p.get("overall_score", 0)) if pairs_analysis else None
    attention_pair = (
        min(pairs_analysis, key=lambda p: p.get("overall_score", 0))
        if len(pairs_analysis) > 1
        else None
    )
    dominant_hanh = max(energy_distribution, key=energy_distribution.get) if energy_distribution else ""
    energy_keeper = energy_roles[0] if energy_roles else None

    sinh_pairs = [p for p in pairs_analysis if "sinh" in _sinh_khac_type(p)]
    khac_pairs = [p for p in pairs_analysis if "khac" in _sinh_khac_type(p)]
    xung_pairs = [
        p for p in pairs_analysis
        if (p.get("chi_compatibility") or {}).get("primary_relation") == "xung"
    ]

    strengths = []
    if family_overall_score >= 65:
        strengths.append("Nền tảng tương hợp gia đình khá tốt, dễ tạo đồng thuận nếu duy trì giao tiếp đều đặn.")
    elif family_overall_score >= 45:
        strengths.append("Gia đình có nền tảng ổn định, các khác biệt vẫn có thể chuyển thành bổ trợ nếu biết phân vai rõ.")
    else:
        strengths.append("Gia đình có nhiều khác biệt, đây là cơ hội để mỗi người học cách lắng nghe và trưởng thành.")
    if dominant_hanh:
        strengths.append(f"Năng lượng nổi bật là hành {dominant_hanh}, tạo màu sắc riêng cho nhịp sống gia đình.")
    if best_pair:
        strengths.append(
            f"Cặp thuận lợi nhất hiện là {best_pair['member1_name']} - {best_pair['member2_name']} "
            f"({best_pair['overall_score']}/100)."
        )
    if sinh_pairs:
        strengths.append(f"Có {len(sinh_pairs)} cặp tương sinh, phù hợp để cùng học hỏi, hỗ trợ và phát triển dài hạn.")
    strengths = strengths[:MAX_EXECUTIVE_STRENGTHS]

    risks = []
    if khac_pairs:
        risks.append(f"Có {len(khac_pairs)} cặp tương khắc cần chú ý cách nói chuyện và ranh giới cá nhân.")
    if xung_pairs:
        risks.append(f"Có {len(xung_pairs)} cặp địa chi xung, nên tránh quyết định nóng khi cảm xúc cao.")
    if attention_pair and attention_pair.get("overall_score", 50) < 45:
        risks.append(
            f"Cặp cần điều hòa nhất là {attention_pair['member1_name']} - {attention_pair['member2_name']} "
            f"({attention_pair['overall_score']}/100)."
        )
    if not risks:
        risks.append("Chưa thấy xung khắc nổi bật, nhưng vẫn nên duy trì thói quen lắng nghe và cảm ơn nhau.")
    risks = risks[:MAX_EXECUTIVE_RISKS]

    actions = [
        "Mỗi tuần chọn một buổi trò chuyện gia đình không điện thoại trong 20-30 phút.",
        "Với cặp có điểm thấp nhất, thống nhất một nguyên tắc tranh luận: không ngắt lời, không kết luận khi đang nóng.",
        "Dùng cặp thuận lợi nhất làm 'cầu nối' để lan tỏa năng lượng tích cực trong nhà.",
        "Khi đọc báo cáo dài, ưu tiên biến mỗi khuyến nghị thành một hành động nhỏ có thể làm ngay trong tuần.",
        "Lưu kết quả hiện tại để so sánh lại sau khi gia đình thay đổi hoặc bước sang năm mới.",
    ][:MAX_EXECUTIVE_ACTIONS]

    return {
        "strengths": strengths,
        "risks": risks,
        "actions": actions,
        "energy_keeper": energy_keeper,
        "best_pair": _pair_summary(best_pair),
        "attention_pair": _pair_summary(attention_pair),
        "positioning_note": (
            "Kết quả mang tính tham khảo văn hoá - không phải tiên tri tuyệt đối; "
            "mục tiêu chính là giúp gia đình hiểu nhau, giao tiếp tốt hơn và nuôi dưỡng quan hệ bền vững."
        ),
    }


def determine_family_dynamics(
    members: List[dict],
    pairs_analysis: List[dict],
    energy_distribution: dict
) -> str:
    """Determine the overall family dynamics description"""
    avg_score = sum(p["overall_score"] for p in pairs_analysis) / len(pairs_analysis) if pairs_analysis else 50

    # Check dominant elements
    elements = list(energy_distribution.keys())
    dominant = max(energy_distribution, key=energy_distribution.get) if energy_distribution else ""

    if avg_score >= 65:
        dynamics = f"Gia đình hài hòa và gắn kết. "
    elif avg_score >= 45:
        dynamics = f"Gia đình có nền tảng ổn định với một số điểm cần chú ý. "
    else:
        dynamics = f"Gia đình có nhiều sự khác biệt, là cơ hội để mỗi người học hỏi và phát triển. "

    # Add element-based insight
    if len(energy_distribution) >= 3:
        dynamics += "Sự đa dạng ngũ hành tạo nên một gia đình đa chiều và phong phú. "
    elif dominant:
        hanh_descriptions = {
            "Kim": "Gia đình mang năng lượng Kim - mạnh mẽ, kỷ luật và quyết đoán.",
            "Mộc": "Gia đình mang năng lượng Mộc - phát triển, sáng tạo và hướng tới tương lai.",
            "Hỏa": "Gia đình mang năng lượng Hỏa - nhiệt tình, năng động và cảm xúc phong phú.",
            "Thổ": "Gia đình mang năng lượng Thổ - ổn định, đáng tin cậy và có nền tảng vững chắc.",
            "Thủy": "Gia đình mang năng lượng Thủy - linh hoạt, thông minh và sáng tạo.",
        }
        dynamics += hanh_descriptions.get(dominant, "")

    return dynamics


def _health_focus_for_hanh(hanh: str) -> List[str]:
    """Common health focus areas by Ngũ hành of bản mệnh."""
    return {
        "Kim": ["hô hấp - phổi", "đại tràng", "da", "khớp xương", "viêm xoang"],
        "Mộc": ["gan - mật", "mắt", "gân cơ", "đầu - cổ", "căng thẳng thần kinh"],
        "Hỏa": ["tim mạch", "huyết áp", "tuần hoàn", "mất ngủ", "ruột non"],
        "Thổ": ["tiêu hoá - dạ dày", "lá lách", "cơ", "cân nặng", "đường huyết"],
        "Thủy": ["thận - bàng quang", "nội tiết", "khí huyết", "tai", "sinh lý"],
    }.get(hanh, ["sức khỏe tổng quát", "giấc ngủ", "tinh thần"])


def _is_child(role: str, year: int, birth_year: int | None) -> bool:
    if role in {"con", "anh", "chị", "em"}:
        # Age-based fallback - children under 16
        if birth_year and year - birth_year <= 16:
            return True
        return role == "con"
    return False


def _detailed_member_forecast(
    member: dict, year: int, year_can: str, year_chi: str, base: dict
) -> dict:
    """Build a rich per-member forecast covering career, finance,
    mental, emotional, health, relationships - tailored by role, gender,
    age, ngũ hành, can-chi vs the target year.

    `base` is the output of `calculate_annual_energy(...)` for this member.
    """
    name = member.get("name", "")
    role = member.get("role", "")
    gender = member.get("gender", "")
    hanh = member.get("ngu_hanh", "")
    chi = member.get("dia_chi", "")
    can = member.get("thien_can", "")
    nap_am = member.get("nap_am", "")
    birth_year = member.get("lunar_year") or member.get("birth_year")

    is_thai_tue = base.get("is_thai_tue", False)
    is_xung = base.get("is_xung", False)
    level = base.get("energy_level", "ổn định")
    is_child = _is_child(role, year, birth_year)

    year_hanh_can = {
        "Giáp": "Mộc", "Ất": "Mộc", "Bính": "Hỏa", "Đinh": "Hỏa",
        "Mậu": "Thổ", "Kỷ": "Thổ", "Canh": "Kim", "Tân": "Kim",
        "Nhâm": "Thủy", "Quý": "Thủy",
    }.get(year_can, "")

    # Hanh interaction member vs year
    year_member_relation = ""
    if hanh and year_hanh_can:
        if hanh == year_hanh_can:
            year_member_relation = f"đồng hành ({hanh}) với thiên can năm - năng lượng được củng cố"
        elif TUONG_SINH.get(year_hanh_can) == hanh:
            year_member_relation = f"thiên can năm ({year_hanh_can}) sinh bản mệnh ({hanh}) - năm được nâng đỡ"
        elif TUONG_SINH.get(hanh) == year_hanh_can:
            year_member_relation = f"bản mệnh ({hanh}) sinh thiên can năm ({year_hanh_can}) - dễ hao tổn năng lượng, cần giữ sức"
        elif TUONG_KHAC.get(year_hanh_can) == hanh:
            year_member_relation = f"thiên can năm ({year_hanh_can}) khắc bản mệnh ({hanh}) - cần đề phòng áp lực"
        elif TUONG_KHAC.get(hanh) == year_hanh_can:
            year_member_relation = f"bản mệnh ({hanh}) khắc thiên can năm ({year_hanh_can}) - chủ động được nhưng tốn sức"

    # ------- Career / Development -------
    if is_child:
        career_title = "Phát triển - học hành"
        career = (
            f"Bé {name} (hành {hanh}, {can} {chi}) đang ở giai đoạn phát triển. "
            f"Năm {year} là dịp tốt để định hình tính cách lõi và kỹ năng nền."
        )
        if hanh == "Kim":
            career += " Hợp các hoạt động có kỷ luật rõ (võ thuật, âm nhạc theo bài bản)."
        elif hanh == "Mộc":
            career += " Hợp các hoạt động sáng tạo, khám phá thiên nhiên, ngôn ngữ."
        elif hanh == "Hỏa":
            career += " Cần kênh xả năng lượng (thể thao), học cách điều tiết cảm xúc sớm."
        elif hanh == "Thổ":
            career += " Cần môi trường ổn định, ít xáo trộn; thích hợp các hoạt động lặp lại."
        elif hanh == "Thủy":
            career += " Tư duy linh hoạt, hợp các trò chơi logic, sách truyện, ngôn ngữ."
    else:
        career_title = "Sự nghiệp - công việc"
        career_bits = []
        if is_thai_tue:
            career_bits.append(
                "Năm Thái Tuế (trùng địa chi với năm sinh) – đây là chu kỳ tái cấu "
                "trúc nghề nghiệp, dễ có thay đổi định hướng, chuyển môi trường, "
                "hoặc mở rộng quy mô. Nên chuẩn bị sẵn cho biến động."
            )
        elif is_xung:
            career_bits.append(
                "Năm xung địa chi – có thể gặp va chạm trong tổ chức, biến động "
                "công việc; nên giữ thái độ điềm tĩnh, tránh quyết định gấp."
            )
        elif level == "thuận lợi":
            career_bits.append(
                "Năm vận khí thuận – có nhiều cơ hội mở rộng công việc, có quý nhân "
                "nghề nghiệp; nên chủ động đặt mục tiêu lớn."
            )
        else:
            career_bits.append(
                "Năm ổn định – phù hợp để củng cố vị trí hiện tại, hoàn thiện kỹ năng "
                "và xây nền cho chu kỳ sau."
            )
        if year_member_relation:
            career_bits.append("Theo ngũ hành: " + year_member_relation + ".")
        # Hanh-specific career suggestions
        if hanh == "Kim":
            career_bits.append("Hành Kim hợp công việc cần kỷ luật, hệ thống: tài chính, luật, công nghệ, vận hành.")
        elif hanh == "Mộc":
            career_bits.append("Hành Mộc hợp sáng tạo - giáo dục - sản phẩm - thương hiệu - nông nghiệp công nghệ cao.")
        elif hanh == "Hỏa":
            career_bits.append("Hành Hỏa hợp truyền thông, marketing, sales, năng lượng, ngành biểu diễn.")
        elif hanh == "Thổ":
            career_bits.append("Hành Thổ hợp bất động sản, xây dựng, dịch vụ ổn định, quản trị dài hạn.")
        elif hanh == "Thủy":
            career_bits.append("Hành Thủy hợp tri thức, nghiên cứu, tư vấn, dòng chảy thông tin, fintech.")
        career = " ".join(career_bits)

    # ------- Finance -------
    if is_child:
        fin_title = "Tài lộc gia đình dành cho bé"
        finance = (
            f"Bé {name} chưa tạo dòng tiền nhưng là 'phúc khí' của gia đình. "
            "Nên có quỹ giáo dục riêng và bảo hiểm sức khỏe cơ bản."
        )
    else:
        fin_title = "Tài chính"
        fin_bits = []
        if level in {"thuận lợi", "ổn định"} and not is_thai_tue:
            fin_bits.append(
                "Dòng tiền có xu hướng tăng, có cơ hội tích lũy và đầu tư dài hạn."
            )
        else:
            fin_bits.append(
                "Tiền vào ra mạnh – chi nhiều cho gia đình, nhà cửa, thiết bị, "
                "hoặc tái đầu tư công việc. Cần kế hoạch dòng tiền rõ ràng."
            )
        if is_thai_tue or is_xung:
            fin_bits.append(
                "**Tránh**: đầu cơ nóng, vay đòn bẩy cao, 'all-in', quyết định "
                "tài chính khi đang stress."
            )
        else:
            fin_bits.append(
                "**Phù hợp**: đầu tư dài hạn, xây hệ thống thu nhập, mua tài sản phục vụ tương lai."
            )
        if hanh == "Kim":
            fin_bits.append("Người hành Kim thường giỏi giữ tiền và kỷ luật chi tiêu - đây là lợi thế năm nay.")
        elif hanh == "Thủy":
            fin_bits.append("Người hành Thủy linh hoạt với dòng tiền, hợp các kênh tài chính - nhưng cần tránh dàn trải.")
        finance = " ".join(fin_bits)

    # ------- Mental / Tâm sinh lý -------
    mental_title = "Tâm sinh lý"
    mental_bits = []
    if can == "Canh" or can == "Tân":
        mental_bits.append("Người Can Kim thường có thần kinh hoạt động mạnh, khó nghỉ ngơi, dễ ôm việc.")
    elif can in {"Giáp", "Ất"}:
        mental_bits.append("Người Can Mộc tư duy phóng khoáng, dễ căng thẳng khi bị gò bó.")
    elif can in {"Bính", "Đinh"}:
        mental_bits.append("Người Can Hỏa nhiệt thành, cảm xúc mạnh, dễ bốc nhanh - nguội nhanh.")
    elif can in {"Mậu", "Kỷ"}:
        mental_bits.append("Người Can Thổ điềm đạm, ổn định, nhưng dễ ôm nội tâm.")
    elif can in {"Nhâm", "Quý"}:
        mental_bits.append("Người Can Thủy nhạy cảm, trực giác tốt, dễ suy nghĩ nhiều và tủi thân.")
    if is_thai_tue:
        mental_bits.append("Năm Thái Tuế làm thần kinh hoạt động liên tục - dễ mất ngủ, burnout nếu không nghỉ ngơi đủ.")
    if gender == "nữ" and not is_child:
        mental_bits.append("Phụ nữ năm này nên đặc biệt giữ ổn định cảm xúc, tránh dồn nén; chia sẻ chủ động với người thân.")
    if gender == "nam" and not is_child:
        mental_bits.append("Nam giới năm này dễ chịu áp lực âm thầm; hãy chủ động nói ra cảm xúc thay vì cứng rắn một mình.")
    mental_bits.append("Khuyến nghị: thiền 10 phút/ngày, ngủ đủ 7 giờ, vận động đều.")
    mental = " ".join(mental_bits)

    # ------- Emotional / Tình cảm -------
    emo_title = "Tình cảm - quan hệ"
    if is_child:
        emotional = (
            f"Bé {name} cần được lắng nghe và công nhận cảm xúc. "
            "Cha mẹ tránh so sánh với anh chị em hoặc với 'con nhà khác'."
        )
    elif role == "chồng":
        emotional = (
            "Người chồng năm nay dễ bị cuốn vào công việc – cần dành thời gian "
            "chất lượng cho vợ, lắng nghe chủ động và không 'giải quyết' cảm xúc "
            "của vợ bằng logic."
        )
    elif role == "vợ":
        emotional = (
            "Người vợ năm nay cảm xúc dễ dao động – cần chia sẻ thẳng thay vì "
            "im lặng tích tụ. Nên có hoạt động riêng nuôi dưỡng bản thân."
        )
    elif role in {"cha", "bố", "mẹ"}:
        emotional = (
            f"Vai trò {role} năm nay là 'trục cảm xúc' của gia đình – cần giữ "
            "ổn định nội tâm để các thành viên khác có chỗ dựa."
        )
    else:
        emotional = "Năm nay nên ưu tiên những quan hệ bồi đắp năng lượng tích cực."

    # ------- Health -------
    health_title = "Sức khỏe"
    foci = _health_focus_for_hanh(hanh)
    health_intro = f"Bản mệnh hành **{hanh}**" + (f" (nạp âm: {nap_am})" if nap_am else "") + ", năm nay cần lưu ý:"
    health = (
        health_intro + " " + ", ".join(foci) + ". " +
        ("Đặc biệt năm Thái Tuế nên khám tổng quát đầu năm." if is_thai_tue else
         "Khám định kỳ 6-12 tháng/lần, ưu tiên giấc ngủ và vận động.")
    )

    # ------- Lưu ý chính -------
    highlights = []
    if is_thai_tue:
        highlights.append("⚠️ Năm Thái Tuế – chu kỳ tái cấu trúc, cần thận trọng quyết định lớn.")
    if is_xung:
        highlights.append("⚡ Năm xung địa chi – có thể có biến động về môi trường sống/công việc.")
    if level == "thuận lợi":
        highlights.append("✨ Vận khí thuận – nắm bắt cơ hội mở rộng.")
    if year_member_relation:
        highlights.append("🌿 " + year_member_relation.capitalize() + ".")

    return {
        "highlights": highlights,
        "sections": [
            {"key": "career", "title": career_title, "icon": "💼", "content": career},
            {"key": "finance", "title": fin_title, "icon": "💰", "content": finance},
            {"key": "mental", "title": mental_title, "icon": "🧠", "content": mental},
            {"key": "emotional", "title": emo_title, "icon": "💞", "content": emotional},
            {"key": "health", "title": health_title, "icon": "🩺", "content": health},
        ],
    }


def get_family_annual_forecast(members: List[dict], year: int) -> dict:
    """Get annual forecast for all family members"""
    forecasts = []
    year_can, year_chi = get_year_can_chi(year)

    for member in members:
        # Prefer lunar year (Can Chi cycle is lunar-based), fall back to
        # raw birth_year for legacy data. Use explicit None check so a
        # legitimate year of 0 (extremely unlikely) wouldn't be skipped.
        lunar_year = member.get("lunar_year")
        astro_year = lunar_year if lunar_year is not None else member.get("birth_year")
        if astro_year:
            forecast = calculate_annual_energy(astro_year, year)
            detailed = _detailed_member_forecast(member, year, year_can, year_chi, forecast)
            forecasts.append({
                "id": member.get("id"),
                "name": member["name"],
                "role": member["role"],
                "gender": member.get("gender", ""),
                "ngu_hanh": member.get("ngu_hanh", ""),
                "nap_am": member.get("nap_am", ""),
                **forecast,
                "detailed": detailed,
            })

    # Determine family year assessment
    positive_count = sum(1 for f in forecasts if f.get("score", 0) >= 10)
    thai_tue_count = sum(1 for f in forecasts if f.get("is_thai_tue", False))
    xung_count = sum(1 for f in forecasts if f.get("is_xung", False))

    if thai_tue_count > 0:
        year_can, year_chi = get_year_can_chi(year)
        family_year_summary = f"Năm {year_chi} {year} có {thai_tue_count} thành viên gặp Thái Tuế. Gia đình cần chuẩn bị cho những thay đổi lớn và hỗ trợ nhau."
    elif positive_count >= len(forecasts) * 0.6:
        family_year_summary = f"Năm {year} nhìn chung thuận lợi cho gia đình. Đây là thời điểm tốt để thực hiện các kế hoạch lớn."
    else:
        family_year_summary = f"Năm {year} cần thận trọng với một số quyết định lớn. Gia đình nên cùng nhau hỗ trợ và thảo luận trước khi hành động."

    return {
        "year": year,
        "member_forecasts": forecasts,
        "family_year_summary": family_year_summary,
        "thai_tue_count": thai_tue_count,
        "positive_count": positive_count,
    }


def get_year_can_chi(year: int) -> tuple:
    """Helper to get can chi for a year"""
    from astrology_engine import THIEN_CAN, DIA_CHI
    can_index = (year - 4) % 10
    chi_index = (year - 4) % 12
    return THIEN_CAN[can_index], DIA_CHI[chi_index]
