import argparse

from supabase import create_client

from embedder import embed_query
from settings import require


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("query", nargs="+")
    parser.add_argument("--business", choices=["course", "web", "merch", "general"])
    parser.add_argument("-k", type=int, default=5)
    args = parser.parse_args()

    question = " ".join(args.query)
    db = create_client(require("SUPABASE_URL"), require("SUPABASE_SERVICE_ROLE_KEY"))

    rows = db.rpc("kb_match_chunks", {
        "query_embedding": embed_query(question),
        "match_count": args.k,
        "min_similarity": 0.0,
        "filter_business": args.business,
    }).execute().data

    print(f"Асуулт: {question}\n")
    if not rows:
        print("Юу ч олдсонгүй")
    for r in rows:
        heading = (r["chunk_meta"] or {}).get("heading", "")
        preview = r["content"].replace("\n", " ")[:110]
        print(f"{r['similarity']:.3f}  [{r['business']}] {r['title']} › {heading}")
        print(f"       {preview}\n")


if __name__ == "__main__":
    main()