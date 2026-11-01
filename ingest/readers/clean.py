import re


def clean_text(text: str) -> str:
    """Текстийг цэвэрлэнэ. NUL тэмдэгтийг заавал арилгана: Postgres-д хадгалагдахгүй."""
    text = text.replace("\x00", "")
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t\u00a0]+", " ", text)   # олон зайг нэг болгох
    text = re.sub(r" *\n *", "\n", text)        # мөрийн захын зай арилгах
    text = re.sub(r"\n{3,}", "\n\n", text)      # олон хоосон мөрийг хоёр болгох
    return text.strip()