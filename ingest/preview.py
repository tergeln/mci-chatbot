import sys
from pathlib import Path

from readers import SUPPORTED, load_document


def find_files(target: Path) -> list[Path]:
    if target.is_file():
        return [target]
    return sorted(
        p for p in target.rglob("*")
        if p.is_file() and p.suffix.lower() in SUPPORTED
    )


def main():
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("../knowledge")

    if not target.exists():
        print(f"Зам олдсонгүй: {target.resolve()}")
        print("Одоо ажиллаж байгаа хавтас:", Path.cwd())
        return

    files = find_files(target)
    if not files:
        print(f"{target} дотор дэмжигдэх файл (.pdf .docx .json .txt .md) олдсонгүй")
        return

    for path in files:
        print("=" * 70)
        try:
            doc = load_document(path)
        except Exception as e:
            print(f"{path.name}: АЛДАА → {e}")
            continue

        total = sum(len(s.text) for s in doc.sections)
        print(f"{path.name}  [{doc.doc_type}]")
        print(f"  хэсгийн тоо : {len(doc.sections)}")
        print(f"  нийт тэмдэгт: {total}")
        print(f"  hash        : {doc.content_hash[:12]}...")

        if total < 200:
            print("  ⚠ Текст бараг олдсонгүй. Scan хийсэн (зураг) PDF байж магадгүй.")
        if any("\ufffd" in s.text for s in doc.sections):
            print("  ⚠ Эвдэрсэн тэмдэгт (�) олдлоо. Кодчилол эсвэл фонт асуудал байж болно.")

        if doc.sections:
            first = doc.sections[0]
            meta = []
            if first.page:
                meta.append(f"хуудас {first.page}")
            if first.heading:
                meta.append(f"гарчиг: {first.heading}")
            print(f"  эхний хэсэг ({', '.join(meta) or 'мета байхгүй'}):")
            preview = first.text[:300].replace("\n", "\n    ")
            print(f"    {preview}")


if __name__ == "__main__":
    main()