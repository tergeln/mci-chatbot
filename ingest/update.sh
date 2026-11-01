#!/usr/bin/env bash
# Мэдлэгийн санг нэг командаар шинэчилнэ:
#   1) mci-web сайтын өгөгдлийг knowledge/ руу экспортлох
#   2) өөрчлөгдсөн файлуудыг Supabase руу ачаалах
#   3) knowledge/-аас устгасан файлуудыг DB-ээс цэвэрлэх
#
#   ./update.sh                  # mci-web нь ../../mci-web дээр байвал
#   ./update.sh ~/код/mci-web    # өөр газар байвал
#   ./update.sh --force          # бүх файлыг дахин ачаална (reader/embedding өөрчлөгдсөний дараа)
set -euo pipefail
cd "$(dirname "$0")"

FORCE=""
SITE=""
for arg in "$@"; do
  if [[ "$arg" == "--force" ]]; then FORCE="--force"; else SITE="$arg"; fi
done
SITE="${SITE:-../../mci-web}"

if [[ -d "$SITE/src/data" ]]; then
  echo "== Сайтын өгөгдөл экспортлож байна ($SITE)"
  node export_site.mjs "$SITE"
else
  echo "== mci-web олдсонгүй ($SITE), сайтын экспортыг алгаслаа"
fi

echo "== Ачаалж байна"
.venv/bin/python ingest.py $FORCE

echo "== Устгасан файлуудыг цэвэрлэж байна"
.venv/bin/python ingest.py --prune
