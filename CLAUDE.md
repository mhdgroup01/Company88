# Borisat — ພະແນກຮັບແຈ້ງຄວາມ ແລະ ປະສານງານ (แอปทะเบียน + ระบบล็อคสถานะ)

> ชื่อแอปที่แสดง = "ພະແນກຮັບແຈ້ງຄວາມ ແລະ ປະສານງານ" (เปลี่ยนจาก "ທະບຽນບໍລິສັດ" เมื่อ 2026-07-13).
> โลโก้ = ตราตำรวจลาว `icons/emblem-police.svg` (ตัด watermark ออกจากไฟล์ต้นฉบับ seeklogo แล้ว).
> ไอคอน PWA (icon-192/512, maskable, apple-touch) เรนเดอร์จาก SVG นี้ผ่าน **browser canvas** (ไม่ใช่ PIL — PIL เรนเดอร์ SVG ไม่ได้). `tools/make_icons.py` = โลโก้เก่า เลิกใช้ (มี guard --force กันเขียนทับ).


PWA เก็บข้อมูลบริษัท (ชื่อ เบอร์โทรหลายเบอร์ อีเมล เลขทะเบียน ประเภท หมายเหตุ
ที่อยู่ = ບ້ານ/ເມືອງ/ແຂວງ + **ไฟล์แนบ** PDF/รูป/ไฟล์อื่น — **ไม่มีรูป/โลโก้บริษัท** ผู้ใช้สั่งถอดออก)
พร้อม **ระบบล็อคสถานะ**: ล็อคแล้วแก้ไข/ลบไม่ได้จนกว่าจะปลดล็อค, เก็บเหตุผล + เวลาล็อค
+ **ประวัติ lockLog ต่อบริษัท** และรายงานรวมทุกบริษัทในเมนู ⋯ ("ລາຍງານ ລັອກ/ປົດລັອກ").
การ์ดมีปุ่มโทร (tel:) + ปุ่ม WhatsApp (wa.me — เบอร์ขึ้นต้น 0 แปลงเป็น 856 ใน `waNumber()`).
UI **ภาษาลาวล้วน** ฟอนต์ Noto Sans Lao (webfont, SW cache ให้ใช้ offline ได้ทั้ง Android/iOS).
โทนสี: เขียวเข้มตำรวจลาว + ทองตราสัญลักษณ์ (ยืม forest/sun palette จากระบบ Phi ที่ ~/raw).

## โครงสร้าง

| ไฟล์ | บทบาท |
|------|-------|
| `index.html` | ทั้งแอปใน 1 ไฟล์ — CSS (token 2 ชั้น) + HTML + vanilla JS |
| `sw.js` | service worker `borisat-v2` — แก้ shell ต้อง **bump VERSION** |
| `manifest.json` | W3C manifest (standalone, theme เขียว) |
| `icons/` | สร้างจาก `tools/make_icons.py` (ต้องมี PIL) — อย่าแก้ PNG ตรง |

ไม่มี build step. ต้องเปิดผ่าน http (SW) — preview: config `borisat` ใน `~/raw/.claude/launch.json` (พอร์ต 8095).

## สองระบบใน 1 แอป (module switcher)

แอปมี 2 ระบบ สลับด้วยแท็บใต้ header (`.mod-tabs`), จำค่าใน localStorage `borisat-module`:
- **company** ("ບໍລິສัด") — ทะเบียนบริษัท + ล็อคสถานะ (เดิม)
- **suspect** ("ຜູ້ຕ້ອງຫາ") — "ລະບົບເກັບຂໍ້ມູນ ແລະ ຄຸ້ມຄອງສະຖິຕິຜູ້ຕ້ອງຫາ"

`MODULES[module]` เก็บ config (subtitle/searchPh/filters/fabLabel). `syncModuleUI()` อัปเดต label/แท็บ/stats/chips. `render()` แยกไป `renderCompanies()`/`renderSuspects()`. Stats/chips/FAB/grid-click/search เป็น **module-aware ตัวเดียวใช้ร่วม** (อย่าแยก DOM). `filter`=company, `sFilter`=suspect.

## กลุ่มผู้ต้องหา (store `groups`, IndexedDB v3) — drill-in

ระบบผู้ต้องหาเป็น **2 ระดับ** ควบคุมด้วย `currentGroupId`:
- `null` = ระดับ **"รายชื่อกลุ่ม"**: การ์ด = กลุ่ม (ชื่อ, X/planned ຄົນ, วันที่, สรุปสถานะ); FAB = **ສ້າງກຸ່ມ** (`openGroupForm`); stats = ກຸ່ມ/ຄົນ/ສົ່ງກັບແລ້ວ (แสดงอย่างเดียว ไม่กรอง); chips+catFilter ซ่อน; search=ชื่อกลุ่ม. คลิกการ์ด → `openGroup(gid)`.
- มีค่า = ระดับ **"ในกลุ่ม"** (drill-in): breadcrumb `#crumb` (ปุ่มกลับ/แก้ไข/ลบกลุ่ม); การ์ด=ผู้ต้องหาในกลุ่มนั้น; FAB=**ເพີ່ມຜູ້ຕ້ອงຫา**; chips(สถานะ)+catFilter ทำงาน; stats=ของกลุ่มนั้น. `backToGroups()` กลับ.

group = { id, name*, plannedCount (number|''), createdDate (YYYY-MM-DD, default วันนี้), createdAt, updatedAt }. ผู้ต้องหามี `groupId` (ตั้งอัตโนมัติ = currentGroupId ตอนเพิ่ม). **ลบกลุ่ม = ลบผู้ต้องหาในกลุ่มด้วย** (เตือนจำนวน). `ensureGrouped()` ย้ายผู้ต้องหาที่ groupId ว่าง/ไม่ตรง → กลุ่ม "ກຸ່ມທົ່ວໄປ" (เรียกตอน init + หลัง import). export/import v3 มี `groups` (import กลุ่มก่อนผู้ต้องหา).
`paintStats()`/`paintChips()` ทาสี stat/chip จาก config; `MODULES.suspect` มี groupStats/groupSearchPh/fabGroupLabel แยกจาก in-group.

## ระบบผู้ต้องหา (store `suspects`, IndexedDB v3)

fields: name, **category (ໝວด)**, dob, nationality, borderPassNo, detainedAt, detentionPlace, charge, handlingUnit, caseClosedAt, repatriatedAt, exitCheckpoint (+createdAt/updatedAt). วันที่เก็บเป็น "YYYY-MM-DD" จาก `<input type=date>` แสดงด้วย `fmtDay()` (parse เองกัน timezone เลื่อน).
**บังคับกรอก (validate ใน submit เพราะ form novalidate):** name, detainedAt (ວັນທີ່ຖືກກັກຕົວ), detentionPlace (ສະຖານທີ່) — 2 ตัวหลังอยู่แถวแรกถัดจากชื่อ.
**caseClosedAt + repatriatedAt มี checkbox "ຂ້າມກ່ອນ"** (`#sCaseClosedSkip`/`#sRepatriatedSkip`): ติ๊ก=ปิด+ล้างช่องวันที่ (ยังไม่ดำเนินการ) ค่อยกลับมา edit ปลดติ๊กใส่วันที่ทีหลัง. `wireSkip()` ผูก checkbox↔date, `applySkip()` ตั้ง state ตอนเปิดฟอร์ม (มีวันที่=ปลดติ๊ก, ว่าง=ติ๊กข้าม). status ผู้ต้องหา = repatriated ก็ต่อเมื่อมี repatriatedAt.
**หมวดผู้ต้องหา** (ผู้ใช้ตั้งเอง): localStorage `borisat-suspect-cats` (เริ่มว่าง — ไม่มี default), จัดการผ่าน dialog `#catDialog` ที่ใช้ร่วมกับประเภทบริษัทผ่าน `catMode` ('company'|'suspect'); auto-learn ตอน save; มี dropdown `#sCatFilter` ใน toolbar กรองตามหมวด (โชว์เฉพาะโหมดผู้ต้องหาที่มีหมวด ≥1). แยกขาดจาก `borisat-categories` (ประเภทธุรกิจบริษัท) — อย่าปนกัน. export/import v3 มี `suspectCategories` ด้วย.
สถานะอนุมานจากวันที่ (`suspectStatus()`): มี `repatriatedAt` → **repatriated** (ສົ່ງກັບແລ້ວ), ไม่มี → **detained** (ຖືກກັກຕົວ) — ไม่มีระบบล็อค. Export/import = version 3 (companies + suspects + categories ในไฟล์เดียว).

## Data model (IndexedDB `borisat` v2 / stores `companies` + `suspects`)

- `province` = **index ตัวเลข** ของ `PROVINCES` (0 = ນະຄອນຫຼວງວຽງຈັນ — ระวัง falsiness), `''` = ไม่ระบุ
- `district` = ชื่อเมืองเป็น string (cascade จาก `DISTRICTS[province]` — 148 เมือง/18 แขวง)
- `address` = ບ້ານ (กรอกเอง), `files` = `[{id,name,type,size,blob}]` (Blob ต้นฉบับ, จำกัด 25MB/ไฟล์)
- `lockLog` = `[{action:'lock'|'unlock', at:ISO, reason}]` — append ทุกครั้งที่ toggle; migrate จาก lockedAt ตอน init
- `photo` ถูกถอดออกแล้ว (record เก่าอาจมี blob ค้าง — ไม่อ่าน ไม่ export)
- วันที่แสดงผลด้วย `fmtDate()` เดือนลาว hard-coded (`LAO_MONTHS`) — อย่าเปลี่ยนกลับไปใช้ locale `lo-LA` (หลายเครื่องไม่มี → หลุดเป็นอังกฤษ)
- ประเภทธุรกิจ: ผู้ใช้จัดการเองใน localStorage `borisat-categories` + auto-learn ตอน save
- Export/Import = JSON v2 (มี categories + files เป็น dataURL); import **sanitize ทุก field** — ห้ามผ่อน (กัน XSS/crash)

## กติกา

- **ห้าม hard-code สี/ระยะ** — ใช้ token ใน `:root`/`[data-theme="dark"]`; สี alias ใหม่ต้องกำหนดทั้ง 2 ธีม
- **user data ทุกตัวผ่าน `esc()`** ก่อนลง innerHTML — รวม id/ชื่อไฟล์ (XSS จากไฟล์ import ทำได้จริง)
- **confirmDlg**: resolve ผ่าน `finish()` จุดเดียว + interval เฝ้า `dlg.open` — อย่ากลับไป resolve จาก listener OK ตรงๆ (บั๊กเก่า: backdrop ปิดแล้ว promise ค้าง → OK ครั้งถัดไปยิง action ใส่บริษัทผิดตัว)
- contrast: `--text-tertiary` light ต้อง ≥4.5:1 บน bg-sunken; `--border-strong`/สวิตช์ ≥3:1; focus บน hero ใช้สีทอง
- SW: ลบเฉพาะ cache `borisat-*` (per-origin — กันชน paruay ถ้า deploy ร่วม parme.me); navigate cache ทับ index.html เฉพาะ `res.ok && !redirected && path ตรง scope`
- toast เป็น `popover` (อยู่เหนือ dialog) — อย่าเปลี่ยนกลับเป็น div ธรรมดา
- formDialog/catDialog/suspectFormDialog **ไม่ปิดด้วย backdrop** (กันข้อมูลพิมพ์ค้างหาย)
- **dialog ต้องเป็น flex column**: `dialog[open]{display:flex;flex-direction:column}` + `.dlg-body{flex:1 1 auto;min-height:0;overflow-y:auto}` — head/foot อยู่กับที่ body scroll ตัวเดียว. **ห้ามใช้ `dialog{display:flex}` เฉยๆ** (dialog ที่ปิดจะไม่ถูก UA ซ่อน แล้วโผล่ค้าง — ต้อง `[open]`). เดิมเป็น block+overflow ทำให้ sticky header ทับฟิลด์แรกบนมือถือ กรอกไม่ได้

## ทดสอบ

preview `borisat` → เพิ่มบริษัท (เลือกแขวง→เมืองต้องขึ้นเอง, แนบ PDF/รูป) → ล็อคพร้อมเหตุผล →
รีโหลดต้องคงสถานะ → ปลดล็อค → ตรวจ confirm: แตะ backdrop = ยกเลิกจริง ไม่มี action ค้าง.
