# ພະແນກຮັບແຈ້ງຄວາມ ແລະ ປະສານງານ (Borisat)

PWA ພາສາລາວ ສຳລັບເກັບຂໍ້ມູນ **ບໍລິສัດ** (+ ລະບົບລັອກສະຖານະ) ແລະ **ຜູ້ຕ້ອງຫາ** (ຈັດເປັນກຸ່ມ,
ສະຖິຕິ, ໄຟລ໌ແນບ). ເຮັດວຽກໄດ້ offline, ຕິດຕັ້ງເປັນແອັບໄດ້ (Add to Home Screen) ທັງ Android ແລະ iOS.
ຂໍ້ມູນທັງໝົດເກັບໃນເຄື່ອງ (IndexedDB) — ບໍ່ມີເຊີບເວີ.

## ໄຟລ໌

| ໄຟລ໌ | ໜ້າທີ່ |
|------|--------|
| `index.html` | ທັງແອັບໃນໄຟລ໌ດຽວ (HTML + CSS + JS) |
| `sw.js` | service worker (offline app-shell) |
| `manifest.json` | PWA manifest |
| `icons/` | ໄອຄອນແອັບ + ຕາຕຳຫຼວດລາວ (`emblem-police.svg`) |
| `tools/make_icons.py` | ສະຄຣິບເກົ່າ (ບໍ່ໃຊ້ແລ້ວ) |

ບໍ່ມີ build step — ເປັນ static files ລ້ວນໆ. ທຸກ path ເປັນ relative (`./`) ຈຶ່ງ deploy ໃຕ້ subpath ໄດ້.

## Deploy ຂຶ້ນ GitHub Pages

```bash
# 1) push ຂຶ້ນ repo GitHub ຂອງທ່ານ
git remote add origin https://github.com/<USER>/<REPO>.git
git push -u origin main

# 2) ໃນ GitHub: Settings → Pages → Branch = main / (root) → Save
```

ຈາກນັ້ນເປີດ `https://<USER>.github.io/<REPO>/` — ໃຊ້ງານ ແລະ ຕິດຕັ້ງເປັນແອັບໄດ້ເລີຍ.

> ต้องเสิร์ฟผ่าน **HTTPS** (GitHub Pages เป็น HTTPS อยู่แล้ว) service worker ຈຶ່ງທຳງານ.
> ຖ້າ deploy ໃໝ່ແລ້ວແອັບບໍ່ອັບເດດ ໃຫ້ bump `VERSION` ໃນ `sw.js`.
