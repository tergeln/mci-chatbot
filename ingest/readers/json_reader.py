import json
from pathlib import Path

from .clean import clean_text
from .models import Section


def _flatten(value, prefix: str = "") -> list[str]:
    """Дурын JSON утгыг 'түлхүүр: утга' мөрүүд болгоно."""
    label = prefix[:-1] if prefix.endswith(".") else prefix
    lines: list[str] = []

    if isinstance(value, dict):
        for key, val in value.items():
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