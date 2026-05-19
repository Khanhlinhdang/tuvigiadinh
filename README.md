# 🌟 Tử Vi Gia Đình - Family Relationship Intelligence System

> **Hệ thống phân tích quan hệ và vận khí gia đình theo tri thức Đông phương**

Kết hợp tri thức **Can Chi - Ngu Hanh** truyền thống với **AI hiện đại** để phân tích động lực gia đình, tương hợp giữa các thành viên và đưa ra hướng dẫn phát triển quan hệ bền vững.

---

## Tinh Nang

| Module | Mo ta |
|--------|-------|
| Family Profile Engine | Tu dong tinh Thien Can, Dia Chi, Ngu Hanh, Nap Am tu nam sinh |
| Compatibility Engine | Phan tich tuong hop: luc hop, tam hop, luc xung, tu hanh xung |
| Radar Chart | Bieu do 5 chieu: Cam xuc, Giao tiep, Tai chinh, Loi song, Ben vung |
| AI Co Van | Chat AI hieu tu vi Dong phuong, tu van ca nhan hoa |
| Du Bao Nam | Phan tich van khi tung thanh vien, canh bao Thai Tue |
| Khuyen Nghi | Loi khuyen thuc te ve giao tiep, tai chinh, giao duc |

---

## Cach Chay

### Cach 1: Chay truc tiep (Development)

**Backend (FastAPI):**
```bash
cd backend
pip install -r requirements.txt

# Tuy chon: cau hinh API key
cp .env.example .env
# Chinh sua .env va them OPENAI_API_KEY neu muon dung AI that

python -m uvicorn main:app --reload --port 8000
```

**Frontend (Next.js):**
```bash
cd frontend
npm install
npm run dev
```

Mo trinh duyet: **http://localhost:3000**

---

### Cach 2: Docker Compose

```bash
# Tuy chon: tao file .env o thu muc goc
echo "OPENAI_API_KEY=your_key_here" > .env

# Chay
docker compose up -d
```

- Frontend: **http://localhost:3000**
- Backend API: **http://localhost:8000**  
- API Docs: **http://localhost:8000/docs**

---

## Cau Hinh

### OPENAI_API_KEY (Tuy chon)

Ung dung **hoat dong day du** ma khong can API Key.
Khi khong co key, AI se dung template thong minh dua tren rule-based engine.

De dung AI that (OpenAI GPT-4o-mini):
```bash
# backend/.env
OPENAI_API_KEY=sk-...
```

---

## Kien Truc

```
tuvigiadinh/
├── backend/                    # FastAPI Python
│   ├── main.py                 # API endpoints
│   ├── astrology_engine.py     # Can Chi, Ngu Hanh calculations
│   ├── compatibility_engine.py # Relationship analysis logic
│   ├── ai_layer.py             # AI interpretation layer
│   ├── models.py               # SQLAlchemy models
│   └── schemas.py              # Pydantic schemas
│
├── frontend/                   # Next.js TypeScript
│   ├── app/
│   │   ├── page.tsx            # Landing page
│   │   ├── families/
│   │   │   ├── page.tsx        # Family list
│   │   │   └── [id]/page.tsx   # Family detail + analysis
│   │   └── globals.css
│   ├── components/
│   │   └── NavBar.tsx
│   └── lib/
│       ├── api.ts              # API client
│       └── utils.ts
│
└── docker-compose.yml
```

---

## He Thong Tinh Toan

### Can Chi (Thien Can + Dia Chi)
Tu dong tinh tu nam sinh theo chu ky 60 nam (Luc Thap Hoa Giap).

### Phan Tich Tuong Hop

**Thien Can:**
- Hop: Giap-Ky, At-Canh, Binh-Tan, Dinh-Nham, Mau-Quy
- Xung: 6 cap xung

**Dia Chi:**
- Luc hop: Ty-Suu, Dan-Hoi, Mao-Tuat, Thin-Dau, Ti-Than, Ngo-Mui
- Tam hop: 4 nhom
- Luc xung: 6 cap
- Tu hanh xung: 3 nhom
- Luc hai: 6 cap

**Ngu Hanh:**
- Tuong sinh: Moc→Hoa→Tho→Kim→Thuy→Moc
- Tuong khac: Moc→Tho→Thuy→Hoa→Kim→Moc

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js 16, TypeScript, Tailwind CSS, Recharts |
| Backend | FastAPI, SQLAlchemy, SQLite |
| AI | OpenAI GPT-4o-mini (optional) |
| Deploy | Docker Compose |

---

*Danh cho muc dich tham khao va phat trien ban than theo van hoa Dong phuong.*
