#!/bin/bash
# อัปเดตเว็บ https://pol207.parme.me บน VPS — nginx (container pol207-prod) เสิร์ฟไฟล์ตรง
# ส่งขึ้นเฉพาะไฟล์ runtime (index.html + sw.js + manifest.json + icons/)
# เอกสารพัฒนา (CLAUDE.md, README.md, tools/) เก็บไว้ในเครื่อง ไม่เผยแพร่
set -euo pipefail

KEY="$HOME/.ssh/hostinger_vps_ed25519"
HOST="root@187.127.209.83"
DEST="/docker/pol207-prod/html/"
SRC="$(cd "$(dirname "$0")" && pwd)"

rsync -az --delete -e "ssh -i $KEY" \
  "$SRC/index.html" "$SRC/sw.js" "$SRC/manifest.json" "$SRC/icons" \
  "$HOST:$DEST"

echo -n "verify: "
curl -sS -o /dev/null -w "https://pol207.parme.me/ -> %{http_code}\n" https://pol207.parme.me/
