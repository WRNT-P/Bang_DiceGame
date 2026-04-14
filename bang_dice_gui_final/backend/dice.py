"""
dice.py — หน้าลูกเต๋า, การสุ่ม, และการคำนวณผล

ชื่อ face ต้องตรงกับ DICE_FACES ใน gui/constants.py
และตรงกับชื่อไฟล์รูปใน Images/Dice/
"""
import random


# ─────────────────────────────────────────────────────────────────────────────
#  DiceFace  — ค่าคงที่ชื่อหน้าลูกเต๋า
#  *** ห้ามเปลี่ยนค่า string เด็ดขาด — ต้องตรงกับไฟล์รูปและ GUI ***
# ─────────────────────────────────────────────────────────────────────────────
class DiceFace:
    ARROW       = "arrow"      # 🏹  รับ 1 ลูกศร
    BANG        = "bang1"      # 💥  ยิง 1 ครั้ง
    DOUBLE_BANG = "bang2"      # 💥💥 ยิง 2 ครั้ง
    BEER        = "beer"       # 🍺  ฟื้น 1 HP
    DYNAMITE    = "dynamite"   # 💣  สะสม 3 ตัวต่อกัน = ตาย
    GATLING     = "gatling"    # 🔱  ทุกคนรับ damage = arrow ที่ตัวเองถือ


# รายการ face ทั้งหมดสำหรับสุ่ม
ALL_FACES: list[str] = [
    DiceFace.ARROW,
    DiceFace.BANG,
    DiceFace.DOUBLE_BANG,
    DiceFace.BEER,
    DiceFace.DYNAMITE,
    DiceFace.GATLING,
]


# ─────────────────────────────────────────────────────────────────────────────
#  roll_dice(current_faces, locked_indices) -> list[str]
#
#  Args:
#    current_faces   : list[str]  — face ปัจจุบัน (5 ตัว)
#    locked_indices  : list[int]  — index ที่ lock ไว้ (ไม่สุ่มใหม่)
#  Returns:
#    list[str]  — face ใหม่ทั้ง 5 ตัว
# ─────────────────────────────────────────────────────────────────────────────

def roll_dice(current_faces: list[str], locked_indices: list[int]) -> list[str]:
    result = list(current_faces)  # copy ค่าเดิมไว้ก่อน
    for i in range(len(result)):
        # บังคับล็อคถ้าหน้าเดิมเป็น DYNAMITE
        if current_faces[i] == DiceFace.DYNAMITE:
            continue
            
        if i not in locked_indices:
            result[i] = random.choice(ALL_FACES)
    return result

# ─────────────────────────────────────────────────────────────────────────────
#  apply_dice_results(faces) -> dict
#
#  Args:
#    faces : list[str]  — face ที่ออกมา (5 ตัว)
#  Returns:
#    dict ที่มี key:
#      "arrows"    : int  — จำนวนลูกศร
#      "bang1"     : int  — จำนวน bang ธรรมดา (ยิงระยะ 1)
#      "bang2"     : int  — จำนวน double-bang (ยิงระยะ 1 และ 2)
#      "beers"     : int  — จำนวน beer
#      "dynamites" : int  — จำนวน dynamite
#      "gatlings"  : int  — จำนวน gatling
# ─────────────────────────────────────────────────────────────────────────────
def apply_dice_results(faces: list[str]) -> dict:
    results = {
        "arrows":    0,
        "bang1":     0,
        "bang2":     0,
        "beers":     0,
        "dynamites": 0,
        "gatlings":  0,
    }
    for face in faces:
        if face == DiceFace.ARROW:
            results["arrows"]    += 1
        elif face == DiceFace.BANG:
            results["bang1"]     += 1
        elif face == DiceFace.DOUBLE_BANG:
            results["bang2"]     += 1
        elif face == DiceFace.BEER:
            results["beers"]     += 1
        elif face == DiceFace.DYNAMITE:
            results["dynamites"] += 1
        elif face == DiceFace.GATLING:
            results["gatlings"]  += 1
    return results