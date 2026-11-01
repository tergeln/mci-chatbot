import json
from pathlib import Path

from .clean import clean_text
from .models import Section


# Хэрэглэгчид хамааралгүй дотоод талбарууд: хайлтыг бохирдуулж, бот хэрэглэгчид давтаж хэлэх эрсдэлтэй.
# "_"-ээр эхэлсэн түлхүүр бүр мөн алгасагдана.
INTERNAL_KEYS = {
    "schema_version", "version", "language", "document_id", "document_type", "visibility",
    "approval_status", "source_basis", "source_reference", "related_documents",
    "requires_live_lookup", "knowledge_status", "do_not_invent", "do_not_index_secrets",
    "do_not_index_personal_data", "id",
    # ажлын урсгалын төлвийн кодууд (planned_behavior, confirm_via_backend г.м.)
    "status", "published_status", "public_release_status", "catalog_status", "purchasing_live_status",
    "availability", "availability_source", "price_source", "price_lookup", "pricing_source",
    "price_type", "request_channel", "course_details_source", "title_is_official", "type",
    "live_source", "live_api_available", "snapshot_not_authoritative", "snapshot_observed",
}


def _skip(key: str) -> bool:
    return key.startswith("_") or key in INTERNAL_KEYS


def _flatten(value, prefix: str = "") -> list[str]:
    """Дурын JSON утгыг 'түлхүүр: утга' мөрүүд болгоно."""
    label = prefix[:-1] if prefix.endswith(".") else prefix
    lines: list[str] = []

    if isinstance(value, dict):
        for key, val in value.items():
            if not _skip(key):
                lines.extend(_flatten(val, f"{prefix}{key}."))
    elif isinstance(value, list):
        if all(not isinstance(v, (dict, list)) for v in value):
            joined = ", ".join(str(v) for v in value if v is not None)
            if joined:
                lines.append(f"{label}: {joined}" if label else joined)
        else:
            for i, val in enumerate(value, start=1):
                lines.extend(_flatten(val, f"{label}[{i}]." if label else f"[{i}]."))
    elif value is not None and str(value).strip() != "":
        lines.append(f"{label}: {value}" if label else str(value))

    return lines


def read_json(path: Path) -> list[Section]:
    data = json.loads(path.read_text(encoding="utf-8-sig"))

    # (бүлгийн нэр, бичлэгүүд) гэсэн жагсаалт болгон бэлтгэнэ
    groups: list[tuple[str | None, list]] = []
    if isinstance(data, list):
        groups.append((None, data))
    elif isinstance(data, dict):
        scalars = {}
        for key, val in data.items():
            if _skip(key):
                continue
            if isinstance(val, list):
                groups.append((key, val))
            else:
                scalars[key] = val
        if scalars:
            groups.insert(0, (None, [scalars]))
    else:
        raise ValueError(f"{path.name}: JSON-ийн дээд түвшин объект эсвэл жагсаалт байх ёстой")

    sections: list[Section] = []
    for key, items in groups:
        for index, item in enumerate(items):
            text = clean_text("\n".join(_flatten(item)))
            if text:
                sections.append(
                    Section(
                        text=text,
                        heading=key,
                        meta={"json_key": key, "index": index},
                    )
                )
    return sections