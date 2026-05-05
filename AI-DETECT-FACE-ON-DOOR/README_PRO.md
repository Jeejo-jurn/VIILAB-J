# 🛡️ NIN-FACENet Professional Guide

ระบบประมวลผลใบหน้าอัจฉริยะสำหรับทางเข้า-ออกห้องแล็บ พัฒนาขึ้นเพื่อความเร็ว ความปลอดภัย และความเสถียรสูงสุดบน NVIDIA Jetson Nano

## 🏗️ Architecture Overview
- **Core Engine:** รันแบบ Multithreaded Async 30+ FPS พร้อมระบบ Self-healing (กู้คืนตัวเองอัตโนมัติ)
- **Security:** ตรวจสอบ Liveness (Texture/Geometry/Persistence) และดักจับหน้าจอโทรศัพท์
- **Database:** ใช้ FAISS สำหรับการค้นหาใบหน้าในระดับมิลลิวินาที
- **Reporting:** ส่งข้อมูลผ่าน HTTPS พร้อม API-KEY Security ไปยัง Web Portal หลัก
- **Maintenance:** ระบบ Auto-cleanup 90 วัน ป้องกัน Disk เต็ม

## 📂 Project Structure
- `src/core/`: สมองกลหลัก (Engine, VectorDB, Reporter)
- `src/api/`: ระบบหลังบ้านสำหรับ Web Portal และ History
- `src/hardware/`: ตัวควบคุม Relay และ GPIO สำหรับกลอนประตู
- `data/authorized_users/`: เก็บรูปภาพสำหรับลงทะเบียน (รองรับ Remote Enrollment)

## 🚦 How to Run
1. **Install Dependencies:**
   `pip install -r requirements.txt`
2. **Setup User Database:**
   ใส่รูปใน `data/authorized_users` แล้วรัน `python enroll.py`
3. **Start Engine (Production Mode):**
   `python main.py --jetson` (หากรันบน PC ปกติไม่ต้องใส่ --jetson)

## 📊 Remote API Endpoints
- **Access Log:** `POST /api/log_access` (ส่งจาก Jetson ไป Server หลัก)
- **Status Check:** `GET /status` (เช็คสถานะจาก Admin Panel)
- **Remote Enrollment:** `POST /enroll_remote` (ส่งรูปจากเว็บไปเพิ่มคนใน Jetson)

## 🪵 Debugging
- ตรวจสอบไฟล์ `app.log` สำหรับประวัติการทำงานและ Error ต่างๆ ของระบบ
