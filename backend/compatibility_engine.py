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
)
from typing import List, Dict


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

    return {
        "pairs_analysis": pairs_analysis,
        "family_overall_score": family_overall_score,
        "family_dynamics": family_dynamics,
        "energy_distribution": energy_distribution,
        "energy_roles": energy_roles,
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


def get_family_annual_forecast(members: List[dict], year: int) -> dict:
    """Get annual forecast for all family members"""
    forecasts = []

    for member in members:
        if member.get("birth_year"):
            forecast = calculate_annual_energy(member["birth_year"], year)
            forecasts.append({
                "name": member["name"],
                "role": member["role"],
                **forecast
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
