# 📁 Excel Upload & Update System with FastAPI

ระบบอัปโหลดไฟล์ ZIP/RAR ที่ภายในมีไฟล์ Excel เพื่ออัปเดตข้อมูลในฐานข้อมูล SQLite พร้อมแสดง Dashboard และประวัติการอัปโหลด

## ✅ ฟีเจอร์หลัก

- ล็อกอินผู้ใช้ (Session-based)
- Drag-and-drop UI สำหรับอัปโหลดไฟล์ `.zip` / `.rar`
- อ่านข้อมูลจาก Excel Sheet: `Worksheet`
- อัปเดตตาราง `DISPUTE` ในฐานข้อมูล
- บันทึกผลลงใน `UPDATE_LOG` (สำเร็จ/ล้มเหลว)
- แสดง Dashboard และประวัติอัปโหลด
- รองรับ Docker

---

## 📦 โครงสร้างโปรเจกต์

```
excel_upload_project/
├── app/
│   ├── main.py               # FastAPI main app
│   ├── init_db.py            # สร้างฐานข้อมูล local.db
│   └── templates/            # HTML templates (upload, login, history, dashboard)
├── tests/
│   └── test_main.py          # Unit test ด้วย pytest
├── Dockerfile                # สำหรับรันผ่าน Docker
├── docker-compose.yml        # Docker Compose
├── requirements.txt          # รายชื่อไลบรารี
└── README.md                 # เอกสารนี้
```

---

## 🚀 วิธีใช้งาน

### 1. รันแบบ Local

```bash
# สร้าง virtualenv และติดตั้ง
pip install -r requirements.txt

# สร้างฐานข้อมูล SQLite
python app/init_db.py

# รันแอป
uvicorn app.main:app --reload
```

เข้าที่: [http://localhost:8000](http://localhost:8000)

### 2. รันผ่าน Docker

```bash
docker-compose up --build
```

---

## 🔐 Login

- ชื่อผู้ใช้: `admin`
- รหัสผ่าน: `123456`

---

## 📊 ตารางในฐานข้อมูล

```sql
-- ตารางข้อมูล
CREATE TABLE DISPUTE (
  ENFORCEMENT_ID TEXT PRIMARY KEY,
  GOV_NAME TEXT,
  GOV_RESULT TEXT,
  GOV_UPDATE_DATE TIMESTAMP
);

-- ตาราง log
CREATE TABLE UPDATE_LOG (
  ID INTEGER PRIMARY KEY AUTOINCREMENT,
  ENFORCEMENT_ID TEXT,
  GOV_NAME TEXT,
  GOV_RESULT TEXT,
  STATUS TEXT,
  ERROR_MESSAGE TEXT,
  UPDATED_AT TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 🧪 ทดสอบระบบ

```bash
pytest tests/test_main.py
```

---

## 🛠 เทคโนโลยีที่ใช้

- Python 3.10
- FastAPI
- SQLite
- Pandas, Openpyxl
- Patool (สำหรับ .rar)
- TailwindCSS (UI)
- Docker

---

## 📬 ติดต่อผู้พัฒนา

> 
