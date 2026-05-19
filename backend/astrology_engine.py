"""
Core Tử Vi / Can Chi calculation engine
Handles Vietnamese/Eastern astrology calculations
"""

# Thiên Can (Heavenly Stems)
THIEN_CAN = ["Giáp", "Ất", "Bính", "Đinh", "Mậu", "Kỷ", "Canh", "Tân", "Nhâm", "Quý"]

# Địa Chi (Earthly Branches)
DIA_CHI = ["Tý", "Sửu", "Dần", "Mão", "Thìn", "Tị", "Ngọ", "Mùi", "Thân", "Dậu", "Tuất", "Hợi"]

# Ngũ Hành (Five Elements) for Thiên Can
THIEN_CAN_HANH = {
    "Giáp": "Mộc", "Ất": "Mộc",
    "Bính": "Hỏa", "Đinh": "Hỏa",
    "Mậu": "Thổ", "Kỷ": "Thổ",
    "Canh": "Kim", "Tân": "Kim",
    "Nhâm": "Thủy", "Quý": "Thủy"
}

# Ngũ Hành for Địa Chi
DIA_CHI_HANH = {
    "Tý": "Thủy", "Sửu": "Thổ",
    "Dần": "Mộc", "Mão": "Mộc",
    "Thìn": "Thổ", "Tị": "Hỏa",
    "Ngọ": "Hỏa", "Mùi": "Thổ",
    "Thân": "Kim", "Dậu": "Kim",
    "Tuất": "Thổ", "Hợi": "Thủy"
}

# Nạp Âm (Nayin) - 60 combinations
NAP_AM = {
    ("Giáp", "Tý"): ("Ất", "Sửu", "Kim Hải Trung"),
    ("Bính", "Dần"): ("Đinh", "Mão", "Hỏa Lô Trung"),
    ("Mậu", "Thìn"): ("Kỷ", "Tị", "Mộc Đại Lâm"),
    ("Canh", "Ngọ"): ("Tân", "Mùi", "Thổ Lộ Bàng"),
    ("Nhâm", "Thân"): ("Quý", "Dậu", "Kim Kiếm Phong"),
    ("Giáp", "Tuất"): ("Ất", "Hợi", "Hỏa Sơn Đầu"),
    ("Bính", "Tý"): ("Đinh", "Sửu", "Thủy Giản Hạ"),
    ("Mậu", "Dần"): ("Kỷ", "Mão", "Thổ Thành Đầu"),
    ("Canh", "Thìn"): ("Tân", "Tị", "Mộc Bạch Lạp"),
    ("Nhâm", "Ngọ"): ("Quý", "Mùi", "Mộc Dương Liễu"),
    ("Giáp", "Thân"): ("Ất", "Dậu", "Thủy Tuyền Trung"),
    ("Bính", "Tuất"): ("Đinh", "Hợi", "Thổ Ốc Thượng"),
    ("Mậu", "Tý"): ("Kỷ", "Sửu", "Hỏa Tích Lịch"),
    ("Canh", "Dần"): ("Tân", "Mão", "Mộc Tòng Bách"),
    ("Nhâm", "Thìn"): ("Quý", "Tị", "Thủy Trường Lưu"),
    ("Giáp", "Ngọ"): ("Ất", "Mùi", "Kim Sa Trung"),
    ("Bính", "Thân"): ("Đinh", "Dậu", "Hỏa Sơn Hạ"),
    ("Mậu", "Tuất"): ("Kỷ", "Hợi", "Mộc Bình Địa"),
    ("Canh", "Tý"): ("Tân", "Sửu", "Thổ Bích Thượng"),
    ("Nhâm", "Dần"): ("Quý", "Mão", "Kim Kim Phác"),
    ("Giáp", "Thìn"): ("Ất", "Tị", "Hỏa Phúc Đăng"),
    ("Bính", "Ngọ"): ("Đinh", "Mùi", "Thủy Thiên Hà"),
    ("Mậu", "Thân"): ("Kỷ", "Dậu", "Thổ Đại Dịch"),
    ("Canh", "Tuất"): ("Tân", "Hợi", "Kim Thoa Xuyến"),
    ("Nhâm", "Tý"): ("Quý", "Sửu", "Mộc Tang Đố"),
    ("Giáp", "Dần"): ("Ất", "Mão", "Thủy Đại Khê"),
    ("Bính", "Thìn"): ("Đinh", "Tị", "Thổ Sa Trung"),
    ("Mậu", "Ngọ"): ("Kỷ", "Mùi", "Hỏa Thiên Thượng"),
    ("Canh", "Thân"): ("Tân", "Dậu", "Mộc Thạch Lựu"),
    ("Nhâm", "Tuất"): ("Quý", "Hợi", "Thủy Đại Hải"),
}

# Ngũ Hành tương sinh tương khắc
TUONG_SINH = {
    "Mộc": "Hỏa",  # Mộc sinh Hỏa
    "Hỏa": "Thổ",  # Hỏa sinh Thổ
    "Thổ": "Kim",  # Thổ sinh Kim
    "Kim": "Thủy", # Kim sinh Thủy
    "Thủy": "Mộc"  # Thủy sinh Mộc
}

TUONG_KHAC = {
    "Mộc": "Thổ",  # Mộc khắc Thổ
    "Thổ": "Thủy", # Thổ khắc Thủy
    "Thủy": "Hỏa", # Thủy khắc Hỏa
    "Hỏa": "Kim",  # Hỏa khắc Kim
    "Kim": "Mộc"   # Kim khắc Mộc
}

# Thiên Can tương hợp
THIEN_CAN_HOP = {
    ("Giáp", "Kỷ"): "Thổ", ("Kỷ", "Giáp"): "Thổ",
    ("Ất", "Canh"): "Kim", ("Canh", "Ất"): "Kim",
    ("Bính", "Tân"): "Thủy", ("Tân", "Bính"): "Thủy",
    ("Đinh", "Nhâm"): "Mộc", ("Nhâm", "Đinh"): "Mộc",
    ("Mậu", "Quý"): "Hỏa", ("Quý", "Mậu"): "Hỏa",
}

# Thiên Can tương xung (6 pairs)
THIEN_CAN_XUNG = [
    ("Giáp", "Canh"), ("Ất", "Tân"), ("Bính", "Nhâm"),
    ("Đinh", "Quý"), ("Mậu", "Giáp"), ("Kỷ", "Ất")
]

# Địa Chi tam hợp
DIA_CHI_TAM_HOP = [
    ["Tý", "Thìn", "Thân"],  # Tam hợp Thủy
    ["Sửu", "Tị", "Dậu"],   # Tam hợp Kim
    ["Dần", "Ngọ", "Tuất"],  # Tam hợp Hỏa
    ["Mão", "Mùi", "Hợi"],  # Tam hợp Mộc
]

# Địa Chi lục hợp
DIA_CHI_LUC_HOP = {
    ("Tý", "Sửu"): "Thổ", ("Sửu", "Tý"): "Thổ",
    ("Dần", "Hợi"): "Mộc", ("Hợi", "Dần"): "Mộc",
    ("Mão", "Tuất"): "Hỏa", ("Tuất", "Mão"): "Hỏa",
    ("Thìn", "Dậu"): "Kim", ("Dậu", "Thìn"): "Kim",
    ("Tị", "Thân"): "Thủy", ("Thân", "Tị"): "Thủy",
    ("Ngọ", "Mùi"): "Thổ", ("Mùi", "Ngọ"): "Thổ",
}

# Tứ hành xung (4 clashes)
TU_HANH_XUNG = [
    ["Tý", "Ngọ", "Mão", "Dậu"],   # Tứ hành xung
    ["Dần", "Thân", "Tị", "Hợi"],  # Tứ hành xung
    ["Thìn", "Tuất", "Sửu", "Mùi"], # Tứ hành xung
]

# Lục hại
LUC_HAI = {
    ("Tý", "Mùi"): True, ("Mùi", "Tý"): True,
    ("Sửu", "Ngọ"): True, ("Ngọ", "Sửu"): True,
    ("Dần", "Tị"): True, ("Tị", "Dần"): True,
    ("Mão", "Thìn"): True, ("Thìn", "Mão"): True,
    ("Thân", "Hợi"): True, ("Hợi", "Thân"): True,
    ("Dậu", "Tuất"): True, ("Tuất", "Dậu"): True,
}

# Lục xung (6 clashes between earthly branches)
LUC_XUNG = {
    ("Tý", "Ngọ"): True, ("Ngọ", "Tý"): True,
    ("Sửu", "Mùi"): True, ("Mùi", "Sửu"): True,
    ("Dần", "Thân"): True, ("Thân", "Dần"): True,
    ("Mão", "Dậu"): True, ("Dậu", "Mão"): True,
    ("Thìn", "Tuất"): True, ("Tuất", "Thìn"): True,
    ("Tị", "Hợi"): True, ("Hợi", "Tị"): True,
}


def get_can_chi_from_year(year: int) -> tuple[str, str]:
    """Get Thiên Can and Địa Chi from a year"""
    # Year 4 = Giáp Tý (first sexagenary cycle year)
    can_index = (year - 4) % 10
    chi_index = (year - 4) % 12
    return THIEN_CAN[can_index], DIA_CHI[chi_index]


def get_ngu_hanh(can: str, chi: str) -> dict:
    """Get Ngũ Hành details for a Can-Chi combination"""
    can_hanh = THIEN_CAN_HANH.get(can, "")
    chi_hanh = DIA_CHI_HANH.get(chi, "")

    # Get Nạp Âm
    nap_am = ""
    for (c1, c2), (c3, c4, na) in NAP_AM.items():
        if c1 == can and c2 == chi:
            nap_am = na
            break
        if c3 == can and c4 == chi:
            nap_am = na
            break

    return {
        "can_hanh": can_hanh,
        "chi_hanh": chi_hanh,
        "nap_am": nap_am,
    }


def analyze_can_compatibility(can1: str, can2: str) -> dict:
    """Analyze compatibility between two Thiên Can"""
    result = {
        "relation": "bình thường",
        "type": "neutral",
        "score": 0,
        "description": ""
    }

    # Check hợp
    if (can1, can2) in THIEN_CAN_HOP:
        element = THIEN_CAN_HOP[(can1, can2)]
        result.update({
            "relation": "thiên can hợp",
            "type": "hop",
            "score": 20,
            "description": f"{can1} và {can2} thiên can hợp, tạo hành {element}. Hai người có sự kết nối tự nhiên, dễ đồng thuận."
        })
    # Check xung
    elif (can1, can2) in THIEN_CAN_XUNG or (can2, can1) in THIEN_CAN_XUNG:
        result.update({
            "relation": "thiên can xung",
            "type": "xung",
            "score": -15,
            "description": f"{can1} và {can2} thiên can xung. Có thể có bất đồng quan điểm, cần học cách lắng nghe nhau."
        })

    return result


def analyze_chi_compatibility(chi1: str, chi2: str) -> dict:
    """Analyze compatibility between two Địa Chi"""
    result = {
        "relations": [],
        "score": 0,
        "primary_relation": "bình thường",
        "description": ""
    }

    # Check lục xung
    if (chi1, chi2) in LUC_XUNG:
        result["relations"].append("lục xung")
        result["score"] -= 25
        result["primary_relation"] = "xung"

    # Check lục hợp
    if (chi1, chi2) in DIA_CHI_LUC_HOP:
        element = DIA_CHI_LUC_HOP[(chi1, chi2)]
        result["relations"].append(f"lục hợp ({element})")
        result["score"] += 25
        result["primary_relation"] = "hợp"

    # Check tam hợp
    for group in DIA_CHI_TAM_HOP:
        if chi1 in group and chi2 in group:
            result["relations"].append("tam hợp")
            result["score"] += 20
            if result["primary_relation"] != "xung":
                result["primary_relation"] = "tam hợp"
            break

    # Check tứ hành xung
    for group in TU_HANH_XUNG:
        if chi1 in group and chi2 in group:
            result["relations"].append("tứ hành xung")
            result["score"] -= 20
            if result["primary_relation"] == "bình thường":
                result["primary_relation"] = "xung nhẹ"
            break

    # Check lục hại
    if (chi1, chi2) in LUC_HAI:
        result["relations"].append("lục hại")
        result["score"] -= 15

    # Build description based on relations
    if not result["relations"]:
        result["description"] = f"{chi1} và {chi2} không có quan hệ đặc biệt, vận khí trung bình."
    else:
        desc_parts = []
        for rel in result["relations"]:
            if "lục xung" in rel:
                desc_parts.append(f"xung trực tiếp (lục xung) - có thể mâu thuẫn và va chạm")
            elif "lục hợp" in rel:
                desc_parts.append(f"hợp duyên tự nhiên (lục hợp) - dễ hòa hợp, bổ trợ nhau")
            elif "tam hợp" in rel:
                desc_parts.append(f"tam hợp - đồng nhóm năng lượng, có điểm chung sâu sắc")
            elif "tứ hành xung" in rel:
                desc_parts.append(f"thuộc tứ hành xung - có áp lực nhất định trong quan hệ")
            elif "lục hại" in rel:
                desc_parts.append(f"lục hại - có thể ảnh hưởng không tốt đến nhau")
        result["description"] = f"{chi1} và {chi2}: " + "; ".join(desc_parts) + "."

    return result


def analyze_hanh_compatibility(hanh1: str, hanh2: str) -> dict:
    """Analyze compatibility between two Ngũ Hành"""
    result = {
        "relation": "bình hòa",
        "score": 0,
        "description": ""
    }

    if TUONG_SINH.get(hanh1) == hanh2:
        result.update({
            "relation": "tương sinh (thuận)",
            "score": 20,
            "description": f"{hanh1} sinh {hanh2}: quan hệ nuôi dưỡng, người {hanh1} hỗ trợ người {hanh2} phát triển."
        })
    elif TUONG_SINH.get(hanh2) == hanh1:
        result.update({
            "relation": "tương sinh (nghịch)",
            "score": 15,
            "description": f"{hanh2} sinh {hanh1}: người {hanh2} hỗ trợ người {hanh1}."
        })
    elif TUONG_KHAC.get(hanh1) == hanh2:
        result.update({
            "relation": "tương khắc (thuận)",
            "score": -20,
            "description": f"{hanh1} khắc {hanh2}: người {hanh1} có xu hướng kiểm soát hoặc ảnh hưởng tiêu cực đến người {hanh2}."
        })
    elif TUONG_KHAC.get(hanh2) == hanh1:
        result.update({
            "relation": "bị khắc",
            "score": -15,
            "description": f"{hanh2} khắc {hanh1}: người {hanh2} có ảnh hưởng mạnh lên người {hanh1}."
        })
    elif hanh1 == hanh2:
        result.update({
            "relation": "tương tỷ (đồng hành)",
            "score": 10,
            "description": f"Cùng hành {hanh1}: có điểm tương đồng về tính cách và năng lượng."
        })

    return result


def get_personality_traits(can: str, chi: str) -> dict:
    """Get personality traits based on Can Chi"""
    traits = {
        "Giáp": {"core": "lãnh đạo, quyết đoán, cứng rắn", "strength": "sáng tạo, tiên phong", "weakness": "bướng bỉnh, thiếu linh hoạt"},
        "Ất": {"core": "linh hoạt, kiên nhẫn, thích nghi", "strength": "nhẫn nại, tinh tế", "weakness": "thiếu quyết đoán"},
        "Bính": {"core": "nhiệt tình, năng động, hướng ngoại", "strength": "truyền cảm hứng, lạc quan", "weakness": "bốc đồng, dễ nóng"},
        "Đinh": {"core": "suy nghĩ sâu, nhạy cảm, tình cảm", "strength": "trực giác tốt, quan tâm", "weakness": "lo lắng, nhạy cảm quá"},
        "Mậu": {"core": "ổn định, đáng tin, thực tế", "strength": "bền vững, trung thành", "weakness": "bảo thủ, chậm thay đổi"},
        "Kỷ": {"core": "cẩn thận, chu đáo, thận trọng", "strength": "tỉ mỉ, đáng tin cậy", "weakness": "lo xa, thiếu quyết đoán"},
        "Canh": {"core": "mạnh mẽ, trực tiếp, dứt khoát", "strength": "công bằng, rõ ràng", "weakness": "cứng nhắc, khắt khe"},
        "Tân": {"core": "tinh tế, nhạy cảm, hoàn hảo chủ nghĩa", "strength": "sáng suốt, chính xác", "weakness": "hay phán xét, cầu toàn"},
        "Nhâm": {"core": "thông minh, linh hoạt, giao tiếp tốt", "strength": "thích nghi nhanh, sáng tạo", "weakness": "thiếu tập trung, hay thay đổi"},
        "Quý": {"core": "trực giác, sâu sắc, huyền bí", "strength": "hiểu người, có chiều sâu", "weakness": "bi quan, khép kín"},
    }

    chi_traits = {
        "Tý": {"energy": "thủy", "type": "hoạt động ban đêm, thông minh, nhanh nhẹn"},
        "Sửu": {"energy": "thổ", "type": "chăm chỉ, kiên định, thực tế"},
        "Dần": {"energy": "mộc", "type": "dũng cảm, tham vọng, độc lập"},
        "Mão": {"energy": "mộc", "type": "nhẹ nhàng, sáng tạo, hòa bình"},
        "Thìn": {"energy": "thổ", "type": "thông minh, đặc biệt, đa tài"},
        "Tị": {"energy": "hỏa", "type": "sâu sắc, phân tích, khôn ngoan"},
        "Ngọ": {"energy": "hỏa", "type": "năng động, độc lập, nồng nhiệt"},
        "Mùi": {"energy": "thổ", "type": "nhân từ, nghệ thuật, ổn định"},
        "Thân": {"energy": "kim", "type": "nhanh nhẹn, thông minh, linh hoạt"},
        "Dậu": {"energy": "kim", "type": "hoàn hảo chủ nghĩa, thẩm mỹ, cẩn thận"},
        "Tuất": {"energy": "thổ", "type": "trung thành, bảo vệ, thực tế"},
        "Hợi": {"energy": "thủy", "type": "rộng lượng, ngây thơ, may mắn"},
    }

    can_info = traits.get(can, {})
    chi_info = chi_traits.get(chi, {})

    return {
        "can_traits": can_info,
        "chi_traits": chi_info,
        "summary": f"Người {can} {chi}: {can_info.get('core', '')}. {chi_info.get('type', '')}"
    }


def get_energy_role(can: str, chi: str, ngu_hanh: dict) -> str:
    """Determine energy role in family dynamics"""
    hanh = ngu_hanh.get("can_hanh", "")

    roles = {
        "Kim": "Trụ quyết định - người đưa ra quyết định cuối cùng, giữ kỷ luật gia đình",
        "Mộc": "Trụ phát triển - người thúc đẩy tăng trưởng và sáng tạo trong gia đình",
        "Hỏa": "Trụ cảm xúc - người mang năng lượng, nhiệt tình và kết nối cảm xúc",
        "Thổ": "Trụ ổn định - người tạo nền tảng vững chắc và sự ổn định cho gia đình",
        "Thủy": "Trụ trí tuệ - người mang trí tuệ, thích nghi và giao tiếp cho gia đình",
    }

    return roles.get(hanh, "Năng lượng cân bằng")


def calculate_annual_energy(birth_year: int, current_year: int) -> dict:
    """Calculate annual energy/fortune for a given birth year"""
    birth_can, birth_chi = get_can_chi_from_year(birth_year)
    year_can, year_chi = get_can_chi_from_year(current_year)

    # Check Thái Tuế xung (when current year chi clashes with birth chi)
    is_thai_tue = year_chi == birth_chi
    is_xung = (year_chi, birth_chi) in LUC_XUNG

    # Calculate energy score
    chi_compat = analyze_chi_compatibility(year_chi, birth_chi)
    can_compat = analyze_can_compatibility(year_can, birth_can)

    total_score = chi_compat["score"] + can_compat["score"]

    if is_thai_tue:
        forecast = "Năm Thái Tuế - năm bản mệnh. Cần thận trọng trong quyết định lớn, dễ có biến động. Nên cúng sao giải hạn."
        energy_level = "biến động"
    elif is_xung:
        forecast = "Năm xung bản mệnh. Có thể gặp khó khăn, thử thách. Cần kiên nhẫn và thận trọng."
        energy_level = "thách thức"
    elif total_score >= 30:
        forecast = "Năm vận khí tốt. Nhiều cơ hội thuận lợi, dễ thành công trong công việc và quan hệ."
        energy_level = "thuận lợi"
    elif total_score >= 10:
        forecast = "Năm vận khí trung bình. Ổn định, không có biến động lớn."
        energy_level = "ổn định"
    else:
        forecast = "Năm cần chú ý. Có thể gặp một số trở ngại, cần cẩn thận trong quyết định."
        energy_level = "cần chú ý"

    return {
        "birth_can_chi": f"{birth_can} {birth_chi}",
        "year_can_chi": f"{year_can} {year_chi}",
        "is_thai_tue": is_thai_tue,
        "is_xung": is_xung,
        "energy_level": energy_level,
        "forecast": forecast,
        "score": total_score
    }
