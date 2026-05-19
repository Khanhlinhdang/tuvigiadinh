"""
AI Integration Layer for Tử Vi Gia Đình
Uses OpenAI API with structured prompts for consistent interpretation
"""
import os
import json
import httpx
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")


async def get_ai_interpretation(family_data: dict, analysis_data: dict) -> str:
    """
    Get AI interpretation of family compatibility analysis
    Uses structured prompt to ensure consistent, meaningful output
    """
    if not OPENAI_API_KEY or not OPENAI_API_KEY.startswith("sk-"):
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
    if not OPENAI_API_KEY or not OPENAI_API_KEY.startswith("sk-"):
        return generate_fallback_chat_response(question)

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

    return generate_fallback_chat_response(question)


def generate_fallback_interpretation(family_data: dict, analysis_data: dict) -> str:
    """Generate rule-based interpretation when AI is not available"""
    score = analysis_data.get("family_overall_score", 0)
    members = family_data.get("members", [])

    # Build interpretation based on score
    if score >= 60:
        overview = "Gia đình này có vận khí tổng thể rất tốt. Các thành viên có năng lượng hỗ trợ và bổ sung cho nhau."
    elif score >= 30:
        overview = "Gia đình có nền tảng khá vững chắc. Dù có một số điểm khác biệt nhưng đây là cơ hội để mỗi người học hỏi và phát triển."
    elif score >= 0:
        overview = "Gia đình có sự đa dạng về năng lượng. Điều này tạo nên sức mạnh riêng nếu biết cách cân bằng."
    else:
        overview = "Gia đình có nhiều sự khác biệt về năng lượng. Đây là thách thức nhưng cũng là cơ hội để mỗi người phát triển bản thân."

    # Identify elements present
    elements = set()
    for m in members:
        if m.get("ngu_hanh"):
            elements.add(m["ngu_hanh"])

    strengths = []
    if len(elements) >= 3:
        strengths.append("Sự đa dạng ngũ hành tạo nên gia đình cân bằng và phong phú")
    if any(m.get("ngu_hanh") == "Thổ" for m in members):
        strengths.append("Có thành viên hành Thổ đóng vai trò nền tảng ổn định")
    if any(m.get("ngu_hanh") == "Thủy" for m in members):
        strengths.append("Có thành viên hành Thủy mang trí tuệ và sự linh hoạt")

    if not strengths:
        strengths = ["Gia đình có sự gắn kết về năng lượng", "Các thành viên dễ hiểu nhau"]

    interpretation = f"""📊 **Tổng quan gia đình:**
{overview}

✨ **Điểm mạnh:**
{chr(10).join(f'• {s}' for s in strengths)}

💡 **Lời khuyên:**
• Tạo không gian để mỗi thành viên bày tỏ cảm xúc và suy nghĩ
• Tôn trọng sự khác biệt về tính cách và phong cách sống
• Cùng nhau xây dựng truyền thống gia đình để tạo sự gắn kết

🌟 **Ghi nhớ:** Mọi gia đình đều có thách thức riêng. Điều quan trọng là tình yêu thương và sự thấu hiểu lẫn nhau."""

    return interpretation


def generate_fallback_chat_response(question: str) -> str:
    """Generate a helpful response when AI API is not available"""
    return """Xin lỗi, tính năng AI Cố Vấn hiện cần cấu hình API Key. 

Để sử dụng đầy đủ tính năng này, vui lòng:
1. Cấu hình OPENAI_API_KEY trong file .env
2. Khởi động lại ứng dụng

Trong thời gian chờ, bạn có thể xem phân tích tương hợp chi tiết ở trang Phân Tích Gia Đình để hiểu rõ hơn về động lực của từng mối quan hệ."""
