import re
import unicodedata


def normalize_text(text: str | None) -> str:
    """Chuẩn hóa chuỗi văn bản tiếng Việt sang không dấu, chữ thường để tìm kiếm."""
    if not text:
        return ""

    # Chuyển đổi ký tự đ/Đ trước khi phân rã Unicode
    text = text.replace("đ", "d").replace("Đ", "D")

    # Phân rã ký tự có dấu thành ký tự gốc + dấu kết hợp (NFD)
    decomposed = unicodedata.normalize("NFD", text)
    # Loại bỏ các ký tự dấu (Combining Diacritical Marks)
    without_marks = "".join(ch for ch in decomposed if unicodedata.category(ch) != "Mn")

    # Chuẩn hóa về NFC, chuyển chữ thường và loại bỏ khoảng trắng thừa
    result = unicodedata.normalize("NFC", without_marks).strip().lower()
    return re.sub(r"\s+", " ", result)
