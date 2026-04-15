"""
utils.py — Utility functions
รวบรวมฟังก์ชันช่วยเหลือ (Helper Functions) อรรถประโยชน์ต่างๆ ที่สามารถเรียกใช้จากส่วนไหนก็ได้ในแอพ
"""
import os
import sys
from pathlib import Path


def get_project_root() -> Path:
    """คืนค่า Path ของโฟลเดอร์หลักของโปรเจกต์"""
    return Path(__file__).parent.absolute()


def get_resource_path(relative_path: str) -> str:
    """
    รับ Path สัมพัทธ์และคืนค่า Path เต็ม (Absolute Path)
    ฟังก์ชันนี้ช่วยให้ไฟล์ Asset (รูปภาพ, เสียง) ยังสามารถโหลดได้ถูกต้อง
    เมื่อนำโปรเจกต์ไปแปลงเป็นไฟล์ .exe (Packaging/Deployment) ตามข้อกำหนด 3.3
    """
    try:
        # กรณีรันผ่าน PyInstaller (PyInstaller จะเก็บ path ไว้ใน sys._MEIPASS)
        base_path = sys._MEIPASS
    except AttributeError:
        # กรณีรันปกติด้วย Python
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


def clamp(value: int, min_value: int, max_value: int) -> int:
    """จำกัดค่าตัวเลขให้อยู่ในช่วงที่กำหนด"""
    return max(min_value, min(value, max_value))
