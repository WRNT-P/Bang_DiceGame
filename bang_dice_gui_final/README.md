# 🤠 Bang! Dice Game — Project README

> **Pygame-based digital implementation of Bang! The Dice Game**

---

## 📁 โครงสร้างโปรเจกต์ปัจจุบัน

```
bang_dice_gui_final/
│
├── main.py                 ← Entry point (เริ่มเกม)
│
├── gui/  (FRONTEND ✅)     ← ส่วนแสดงผล / UI ทั้งหมด
│   ├── __init__.py
│   ├── constants.py        ← สี, ฟอนต์, ค่าคงที่, ฟังก์ชัน helper
│   ├── button.py           ← ปุ่ม interactive ที่ใช้ throughout
│   ├── menu.py             ← หน้าเมนูหลัก + SceneManager
│   ├── lobby.py            ← หน้าเลือกผู้เล่น + ตัวละคร
│   ├── game_screen.py      ← หน้าเล่นเกม (ลูกเต๋า, โต๊ะ, ผู้เล่น)
│   └── result.py           ← หน้าแสดงผลเกมและ Role Reveal
│
├── Images/                 ← รูปภาพทั้งหมด
│   ├── Chars/              ← รูปตัวละคร 16 ตัว (.jpg)
│   ├── Dice/               ← รูปหน้าลูกเต๋า 6 หน้า (.jpg)
│   └── BangDice_BG.webp   ← ภาพพื้นหลัง
│
└── backend/  (MISSING ❌)  ← ยังไม่มี! ต้องสร้างขึ้นมา
```

---

## ✅ สิ่งที่ทำเสร็จแล้ว (Frontend)

| หน้าจอ | ไฟล์ | สถานะ | รายละเอียด |
|--------|------|--------|------------|
| Menu | `gui/menu.py` | ✅ เสร็จ | หน้าต้อนรับ, ปุ่ม Play/Quit, SceneManager |
| Lobby | `gui/lobby.py` | ✅ เสร็จ | เพิ่ม/ลบผู้เล่น 2-8 คน, แสดง Character Card |
| Game | `gui/game_screen.py` | ✅ เสร็จ (UI เท่านั้น) | ลูกเต๋า 5 ลูก, Lock/Roll animation, Player Token ring |
| Result | `gui/result.py` | ✅ เสร็จ (UI เท่านั้น) | Winner banner, Role Reveal cards, Confetti |

**Frontend มีครบแล้ว แต่ทุกอย่างเป็นแค่ "การแสดงผล" เท่านั้น — ยังไม่มีระบบเกมจริง**

---

## ❌ สิ่งที่ยังขาดอยู่ (Backend)

### 1. ระบบตัวละคร (Character System)
- [ ] ข้อมูลตัวละครแต่ละตัว: HP, ความสามารถพิเศษ (Special Power)
- [ ] ตัวอย่าง: **Lucky Duke** → สุ่มลูกเต๋า 2 ครั้ง เอาผลที่ดีกว่า

### 2. ระบบบทบาท (Role System)
- [ ] แจก Role แบบสุ่มและปิดลับ: Sheriff, Deputy, Outlaw, Renegade
- [ ] กำหนดเงื่อนไขชนะ-แพ้ของแต่ละ Role

### 3. ระบบลูกเต๋า (Dice Engine)
- [ ] สุ่มลูกเต๋าจริงๆ ตามกฎเกม (ปัจจุบันแค่สุ่ม visual เท่านั้น)
- [ ] คำนวณผลลัพธ์ลูกเต๋า: Bang!, Beer, Arrow, Gatling, Dynamite
- [ ] Re-roll ได้ 3 ครั้งต่อ turn (ล็อกลูกเต๋าที่ต้องการได้)

### 4. ระบบ HP และความเสียหาย
- [ ] ติดตาม HP ของผู้เล่นแต่ละคนจริงๆ (ปัจจุบัน HP แค่ random visual)
- [ ] ลด HP เมื่อโดน Bang!, Arrow attack
- [ ] เพิ่ม HP เมื่อกิน Beer
- [ ] ผู้เล่ยตายเมื่อ HP = 0 → ออกจากเกม

### 5. ระบบลูกศร (Arrow System)
- [ ] ติดตาม Arrow จำนวนกลาง (Arrow Pile)
- [ ] เมื่อ Gatling ออก → ทุกคนรับ damage เท่าจำนวน Arrow ที่ถือ
- [ ] Arrow ทั้งหมดคืน pile เมื่อ Gatling ออก

### 6. ระบบ Turn และ Game Loop
- [ ] เช็คเงื่อนไขชนะ-แพ้หลังแต่ละ turn (ปัจจุบัน END TURN ไม่มีผลจริง)
- [ ] ข้ามผู้เล่นที่ตายแล้วในวง turn
- [ ] เงื่อนไขจบเกม: Sheriff ตาย หรือ Outlaw ทุกคนตาย

### 7. การเชื่อมต่อ Frontend ↔ Backend
- [ ] ส่ง Game State จาก backend ไปให้ frontend แสดงผลจริง
- [ ] ปุ่ม ROLL / END TURN ต้องเรียก game logic จริง ไม่ใช่แค่ animation

---

## 🗺️ แผนการพัฒนาต่อ (Roadmap)

### Phase 1 — สร้างโฟลเดอร์ `backend/`
```
backend/
├── __init__.py
├── dice.py         ← Dice faces, สุ่มลูกเต๋า, คำนวณผล
├── player.py       ← Player class: HP, role, char, alive status
├── roles.py        ← Role definitions + win conditions
├── characters.py   ← Character abilities (special powers)
└── game.py         ← Game class: game loop, turn, arrow pile, win check
```

### Phase 2 — เชื่อม Backend กับ Frontend
- ให้ `game_screen.py` ดึง state จาก `Game` object แทนที่จะ hardcode
- HP ที่แสดงบน PlayerToken มาจาก `player.hp` จริงๆ
- Arrow counter มาจาก `game.arrow_count` จริงๆ
- ปุ่ม ROLL → เรียก `game.roll_dice()` → อัป dice faces
- ปุ่ม END TURN → เรียก `game.end_turn()` → เช็ค win → เปลี่ยน scene ถ้าจบ

### Phase 3 — Polish
- [ ] Special Power ของตัวละครแต่ละตัว
- [ ] Sound effects (pygame.mixer)
- [ ] Animation เพิ่มเมื่อ Bang!, Dynamite, Gatling
- [ ] Save/Load game state

---

## 🎲 กฎเกม Bang! Dice Game (สรุปย่อ)

| หน้าลูกเต๋า | ผล |
|-------------|-----|
| 🏹 Arrow | เอา 1 ลูกศรจาก pile มาถือ |
| 💥 Bang! (x1 หรือ x2) | ยิง Sheriff (ถ้าเป็น Outlaw/Renegade) |
| 🍺 Beer | ฟื้น 1 HP |
| 💣 Dynamite | เก็บไว้ 3 ตัวต่อกัน = เสียชีวิต |
| 🔱 Gatling | ทุกคนรับ damage = Arrow ที่ตัวเองถือ, Arrow คืน pile |

**บทบาท:**
- **Sheriff** — ต้องกำจัด Outlaw และ Renegade ทั้งหมด
- **Deputy** — ช่วย Sheriff (แต่ปิดบทบาท)
- **Outlaw** — กำจัด Sheriff
- **Renegade** — เหลือคนสุดท้าย

---

## 🚀 วิธีรันโปรเจกต์ปัจจุบัน

```bash
# ติดตั้ง dependency
pip install pygame

# รันเกม
python main.py

# Shortcut เพื่อ dev
F1 → Menu
F2 → Lobby
F3 → Game Screen
F4 → Result Screen
ESC → ออก
```

---

## 📌 สรุปงานที่ต้องทำถัดไป

1. **สร้าง `backend/` folder** พร้อม `dice.py`, `player.py`, `game.py`
2. **เขียน Game Loop** ให้จัดการ turn, HP, arrow, win condition
3. **เชื่อม GameScreen** ให้ดึงข้อมูลจาก Game object จริง
4. **ทดสอบ** กฎเกมทุก edge case (Dynamite chain, Gatling, ผู้เล่นตาย)
5. (Optional) เพิ่ม Character Abilities และ Sound Effects
