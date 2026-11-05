"""Үнэлгээний багц ажиллуулах.

api/.venv-ийг идэвхжүүлээд root-оос:

  python evals/run_evals.py                 # зөвхөн хайлт: MIN_SIMILARITY босгыг хэмжинэ (LLM дуудахгүй)
  python evals/run_evals.py --full          # локал rag.answer_question-ээр бүтэн хариулт шалгана
  python evals/run_evals.py --url https://<api>.vercel.app   # production /chat-ийг шалгана
"""
import argparse
import json
import re
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "api"))

THRESHOLDS = [round(0.40 + 0.05 * i, 2) for i in range(9)]   # 0.40 … 0.80


def load_cases(path: Path, only: str | None) -> list[dict]:
    cases = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    return [c for c in cases if not only or only in c["id"]]


def history_of(case: dict) -> list:
    from main import Message
    return [Message(**m) for m in case.get("history", [])]


def check(case: dict, resp: dict, production: bool) -> list[str]:
    """Алдааны жагсаалт буцаана, хоосон бол тэнцсэн."""
    errors = []
    found, answer = resp.get("found"), resp.get("answer", "")
    if case["expect"] == "answer" and not found:
        errors.append("хариулах ёстой байсан ч found=false")
    if case["expect"] == "refuse" and found:
        errors.append("татгалзах ёстой байсан ч found=true")
    if found:
        errors += [f"'{s}' хариултад алга" for s in case.get("must_include", []) if s not in answer]
        if not resp.get("sources"):
            errors.append("эх сурвалж хоосон")
    errors += [f"'{s}' хариултад орсон" for s in case.get("must_not_include", []) if s in answer]
    if case.get("lang") == "en":
        followups = " ".join(resp.get("followups", []))
        if re.search(r"[А-Яа-яЁёӨөҮү]", answer + followups):
            errors.append("англи хариултад кирилл үсэг орсон")
    if production and "debug" in resp:
        errors.append("debug талбар гарсан (DEBUG_RETRIEVAL production дээр асаалттай?)")
    return errors


def run_retrieval(cases: list[dict]) -> None:
    import rag

    print(f"{'дээд':>6}  {'хүлээлт':<7}  id")
    tops = []
    for c in cases:
        rows = rag.retrieve(rag.build_search_query(c["question"], history_of(c)), c.get("business"))
        top = max((r["similarity"] for r in rows), default=0.0)
        tops.append((c, top))
        print(f"{top:6.3f}  {c['expect']:<7}  {c['id']}")

    answer_n = sum(c["expect"] == "answer" for c in cases)
    refuse_n = len(cases) - answer_n
    print(f"\nБосго  хариулах давсан ({answer_n})  татгалзах хаагдсан ({refuse_n})")
    for t in THRESHOLDS:
        passed = sum(c["expect"] == "answer" and top >= t for c, top in tops)
        blocked = sum(c["expect"] == "refuse" and top < t for c, top in tops)
        print(f"{t:5.2f}  {passed:>3}/{answer_n:<20} {blocked:>3}/{refuse_n}")
    print("\nТайлбар: хариулах асуултууд бүгд давах ёстой (давахгүй бол LLM-д хүрэхгүй).")
    print("Татгалзах асуултыг хаах нь нэмэлт хамгаалалт, үлдсэнийг нь LLM found=false-ээр шүүнэ.")


def run_full(cases: list[dict], url: str | None, delay: float) -> int:
    if url:
        import httpx
        client = httpx.Client(timeout=60)
    else:
        import rag

    failed = 0
    for i, c in enumerate(cases):
        if url:
            if i:
                time.sleep(delay)   # rate limit: IP тутамд минутад 10
            r = client.post(url.rstrip("/") + "/chat", json={
                "message": c["question"],
                "history": c.get("history", []),
                **({"business": c["business"]} if c.get("business") else {}),
                "lang": c.get("lang", "mn"),
            })
            if r.status_code != 200:
                failed += 1
                print(f"✗ {c['id']}: HTTP {r.status_code} {r.text[:150]}")
                continue
            resp = r.json()
        else:
            resp = rag.answer_question(c["question"], history_of(c), c.get("business"), c.get("lang", "mn"))

        errors = check(c, resp, production=bool(url))
        failed += bool(errors)
        mark = "✗" if errors else "✓"
        print(f"{mark} {c['id']}  found={resp.get('found')}")
        for e in errors:
            print(f"     - {e}")
        if errors:
            print(f"     хариулт: {resp.get('answer', '')[:200]}")

    print(f"\n{len(cases) - failed}/{len(cases)} тэнцсэн")
    return failed


def main() -> None:
    parser = argparse.ArgumentParser(description="Чатботын үнэлгээ")
    parser.add_argument("--full", action="store_true", help="LLM-ээр бүтэн хариулт шалгах (локал)")
    parser.add_argument("--url", help="deploy хийсэн API-ийн үндсэн хаяг")
    parser.add_argument("--delay", type=float, default=6.5, help="--url үед хүсэлт хоорондын секунд")
    parser.add_argument("--only", help="id-д энэ текст агуулсан кейсүүдийг л ажиллуулах")
    parser.add_argument("--cases", default=str(HERE / "cases.jsonl"))
    args = parser.parse_args()

    cases = load_cases(Path(args.cases), args.only)
    if not cases:
        raise SystemExit("Кейс олдсонгүй")

    if args.full or args.url:
        sys.exit(1 if run_full(cases, args.url, args.delay) else 0)
    run_retrieval(cases)


if __name__ == "__main__":
    main()
