from contextvars import ContextVar
import logging
import sys
import time
from datetime import datetime
from pathlib import Path

LOG_DIR = Path(__file__).resolve().parent.parent.parent / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

# Ngữ cảnh request hiện tại (Async/Thread-safe)
request_context: ContextVar[dict | None] = ContextVar("request_context", default=None)


class RequestContextFilter(logging.Filter):
    """Filter tự động chèn thông tin API, Status, Time, Client vào log message nếu đang trong HTTP request."""

    DEFAULT_STATUS = {
        logging.DEBUG: "200 OK",
        logging.INFO: "200 OK",
        logging.WARNING: "400 Warning",
        logging.ERROR: "500 Error",
        logging.CRITICAL: "500 Critical",
    }

    def filter(self, record: logging.LogRecord) -> bool:
        ctx = request_context.get()
        if ctx:
            ctx["has_logged"] = True
            msg = record.getMessage()

            # Nếu tin nhắn chưa có tiền tố API thì tự động chèn ngữ cảnh
            if not msg.startswith("API "):
                duration_ms = (time.perf_counter() - ctx["start_time"]) * 1000

                # Ưu tiên status truyền qua extra -> status của response -> mặc định theo level
                custom_status = getattr(record, "status", None)
                status_str = (
                    custom_status
                    or ctx.get("status")
                    or self.DEFAULT_STATUS.get(record.levelno, "200 OK")
                )

                method = ctx.get("method", "GET")
                path = ctx.get("path", "/")
                client = ctx.get("client", "unknown")

                record.msg = (
                    f"API {method} {path} | Status: {status_str} | "
                    f"Time: {duration_ms:.2f}ms | Client: {client} | Message: {msg}"
                )
                record.args = ()
        return True


logger = logging.getLogger("sportslot")
logger.setLevel(logging.INFO)
if not any(isinstance(f, RequestContextFilter) for f in logger.filters):
    logger.addFilter(RequestContextFilter())

# Cấu hình console handler mặc định
if not logger.handlers:
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(logging.Formatter("%(levelname)-7s | %(message)s"))
    logger.addHandler(console_handler)

_current_log_file: Path | None = None


def init_logger_file() -> Path:
    """Khởi tạo file log theo timestamp.
    CHỈ được gọi trong lifespan khi server thực sự khởi động, tránh bị Reloader process tạo file rỗng.
    """
    global _current_log_file

    # Xóa file handler cũ nếu có
    for h in list(logger.handlers):
        if isinstance(h, logging.FileHandler):
            logger.removeHandler(h)
            h.close()

    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    log_file = LOG_DIR / f"app_{timestamp}.log"
    counter = 1
    while log_file.exists():
        log_file = LOG_DIR / f"app_{timestamp}_{counter}.log"
        counter += 1

    _current_log_file = log_file

    file_formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-7s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    file_handler = logging.FileHandler(
        filename=log_file,
        mode="w",
        encoding="utf-8",
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    return log_file
