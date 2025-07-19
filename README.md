# Machine Alarm Summary Dashboard

แดชบอร์ดสำหรับสรุปและแสดงผลข้อมูล Alarm ของเครื่องจักรจากฐานข้อมูล MongoDB

## คุณสมบัติ (Features)

- แสดงผลข้อมูล Alarm ตามช่วงเวลาที่เลือก
- สรุปความถี่ของ Alarm แต่ละประเภทในรูปแบบตารางและกราฟแท่ง
- สามารถเลือกดูข้อมูล Top N alarm ได้
- กรองข้อมูล Alarm ที่ต้องการแสดงผลได้
- Export ข้อมูลที่แสดงผลเป็นไฟล์ Excel
- มีระบบ Auto-refresh เพื่ออัปเดตข้อมูลอัตโนมัติทุก 5 นาที

## สิ่งที่ต้องมี (Prerequisites)

- Python 3.8+
- Python 3.11+

## การติดตั้งและใช้งาน (Setup & Usage)

ทำตามขั้นตอนต่อไปนี้เพื่อติดตั้งและรันโปรเจกต์บนเครื่องของคุณ

1. **Clone a repository (ถ้ามี):**

    ```bash
    git clone <your-repository-url>
    cd alarm-dashboard
    ```

2. **สร้างและเปิดใช้งาน Virtual Environment:**
    การใช้ Virtual Environment เป็นวิธีที่ดีที่สุดเพื่อแยกสภาพแวดล้อมของโปรเจกต์นี้ออกจากโปรเจกต์อื่น ๆ

    - **สร้าง venv:**
        (แนะนำให้ใช้ Python Launcher เพื่อระบุเวอร์ชันที่ต้องการ เช่น 3.11)

      ```bash
      # บน Windows (ใช้ Python 3.11)
      py -3.11 -m venv venv
      # บน macOS/Linux หรือถ้ามี python3.11 ใน PATH
      python -m venv venv
      ```

    - **เปิดใช้งาน venv (Activate):**
      - บน Windows:

        ```bash
        .\venv\Scripts\activate
        ```

      - บน macOS/Linux:

        ```bash
        source venv/bin/activate
        ```

    หลังจาก activate แล้ว คุณจะเห็น `(venv)` นำหน้า command prompt ของคุณ

3. **ติดตั้ง Dependencies:**
    ติดตั้งไลบรารีที่จำเป็นทั้งหมดจากไฟล์ `requirements.txt`

    ```bash
    pip install -r requirements.txt
    ```

4. **รันแอปพลิเคชัน:**

    ```bash
    python app.py
    ```

    จากนั้นเปิดเว็บเบราว์เซอร์ไปที่ <http://127.0.0.1:8050/>

5. **หยุดการทำงานของ Virtual Environment:**
    เมื่อใช้งานเสร็จแล้ว สามารถปิด venv ได้ด้วยคำสั่ง:

    ```bash
    deactivate
    ```
