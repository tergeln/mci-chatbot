import argparse
import sys
from pathlib import Path

from chunker import build_chunks
from readers import SUPPORTED, load_document
from settings import ROOT, require
from chunker import build_chunks
from embedder import embed_documents
from readers import SUPPORTED, load_document
from settings import ROOT, require

KNOWLEDGE = ROOT / "knowledge"
BUSINESSES = {"course", "web", "merch", "general"}
INSERT_BATCH = 50


def get_db():
    from supabase import create_client
    return create_client(require("SUPABASE_URL"), require("SUPABASE_SERVICE_ROLE_KEY"))


def business_of(path: Path) -> str:
    parts = path.relative_to(KNOWLEDGE).parts
    if len(parts) > 1 and parts[0] in BUSINESSES:
        return parts[0]
    print(f"  ⚠ чиглэл тодорхойгүй (файлыг {sorted(BUSINESSES)}-ийн нэг хавтсанд тавина уу). 'general' гэж авлаа")
    return "general"


def find_files(target: Path) -> list[Path]:
    if target.is_file():
        return [target]
    return sorted(
        p for p in target.rglob("*")
        if p.is_file()
        and p.suffix.lower() in SUPPORTED
        and not any(part.startswith(".") for part in p.relative_to(target).parts)
    )


def process_file(path: Path, db, dry_run: bool, force: bool) -> None:
    rel = path.relative_to(KNOWLEDGE).as_posix()
    business = business_of(path)
    title = path.stem.replace("_", " ").replace("-", " ")

    doc = load_document(path)
    chunks = build_chunks(doc, title)
    if not chunks:
        print(f"{rel}: текст олдсонгүй, алгасав")
        return

    lengths = [len(c.content) for c in chunks]
    print(f"{rel} [{doc.doc_type}, {business}]: {len(doc.sections)} section → "
          f"{len(chunks)} хэсэг (урт {min(lengths)}–{max(lengths)})")

    if dry_run:
        for c in chunks:
            first_line = c.content.split("\n")[0][:70]
            print(f"    #{c.index:<3} {len(c.content):>5} тэмд.  {first_line}")
        return

    existing = (
        db.table("kb_sources").select("id, content_hash")
        .eq("source_path", rel).execute().data
    )
    if existing and existing[0]["content_hash"] == doc.content_hash and not force:
        print("  өөрчлөгдөөгүй, алгасав")
        return

    # Эхлээд embedding хийнэ: алдаа гарвал DB-д хуучин өгөгдөл хэвээр үлдэнэ
    vectors = embed_documents([c.content for c in chunks])

    if existing:
        db.table("kb_sources").delete().eq("id", existing[0]["id"]).execute()
        print("  хуучин хувилбарыг устгалаа")

    source = db.table("kb_sources").insert({
        "source_path": rel,
        "title": title,
        "business": business,
        "doc_type": doc.doc_type,
        "content_hash": doc.content_hash,
        "metadata": {"chunk_count": len(chunks)},
    }).execute().data[0]

    try:
        rows = [
            {
                "source_id": source["id"],
                "chunk_index": c.index,
                "content": c.content,
                "page": c.page,
                "metadata": c.meta,
                "embedding": v,
            }
            for c, v in zip(chunks, vectors)
        ]
        for i in range(0, len(rows), INSERT_BATCH):
            db.table("kb_chunks").insert(rows[i:i + INSERT_BATCH]).execute()
    except Exception:
        # хагас орсон файл үлдэхгүйн тулд буцаана
        db.table("kb_sources").delete().eq("id", source["id"]).execute()
        raise

    print(f"  ✓ {len(rows)} хэсэг хадгалагдлаа")


def main() -> None:
    parser = argparse.ArgumentParser(description="Файлуудыг мэдлэгийн санд ачаалах")
    parser.add_argument("target", nargs="?", default=str(KNOWLEDGE),
                        help="файл эсвэл хавтас (анхдагч: knowledge/)")
    parser.add_argument("--dry-run", action="store_true",
                        help="зөвхөн хэсэглэлтийг харуулна, embedding/DB-д хүрэхгүй")
    parser.add_argument("--force", action="store_true",
                        help="өөрчлөгдөөгүй файлыг ч дахин ачаалах")
    args = parser.parse_args()

    target = Path(args.target).resolve()
    if not target.exists():
        raise SystemExit(f"Зам олдсонгүй: {target}")
    try:
        target.relative_to(KNOWLEDGE.resolve())
    except ValueError:
        raise SystemExit(f"Файл {KNOWLEDGE} доторх байх ёстой")

    files = find_files(target)
    if not files:
        raise SystemExit("Дэмжигдэх файл олдсонгүй")

    db = None
    if not args.dry_run:
        require("GEMINI_API_KEY")   # түлхүүрийг эхлээд шалгана
        db = get_db()

    failed = 0
    for path in files:
        try:
            process_file(path, db, args.dry_run, args.force)
        except Exception as e:
            failed += 1
            print(f"{path.name}: АЛДАА → {e}")

    print(f"\nДууслаа: {len(files) - failed} амжилттай, {failed} алдаатай")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()