from datetime import datetime
from zoneinfo import ZoneInfo

VN_TZ = ZoneInfo("Asia/Ho_Chi_Minh")


def now_vn() -> datetime:
    """Trả về thời gian hiện tại theo múi giờ Việt Nam (+07:00)."""
    return datetime.now(VN_TZ)
