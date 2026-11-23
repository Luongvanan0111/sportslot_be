import http
import json
import time

from fastapi import Request
from fastapi.responses import Response

from app.core.logging import logger, request_context


async def log_requests_middleware(request: Request, call_next):
    """Middleware quản lý ngữ cảnh và ghi log cho API request/response."""
    start_time = time.perf_counter()
    client_ip = request.client.host if request.client else "unknown"
    method = request.method
    path = request.url.path

    ctx = {
        "method": method,
        "path": path,
        "client": client_ip,
        "start_time": start_time,
        "status": "200 OK",
        "has_logged": False,
    }
    token = request_context.set(ctx)

    try:
        response = await call_next(request)
        duration_ms = (time.perf_counter() - start_time) * 1000
        content_type = response.headers.get("content-type", "")

        # Tên chuẩn của mã trạng thái HTTP (vd: 200 OK, 404 Not Found)
        try:
            status_phrase = http.HTTPStatus(response.status_code).phrase
        except ValueError:
            status_phrase = ""
        status_str = f"{response.status_code} {status_phrase}".strip()
        ctx["status"] = status_str

        # Nếu trong quá trình xử lý endpoint chưa từng gọi logger, middleware sẽ tự động log
        if not ctx.get("has_logged"):
            msg_text = ""
            is_docs = path in ("/docs", "/redoc", "/openapi.json", "/favicon.ico")

            if "application/json" in content_type and not is_docs:
                response_body = b""
                async for chunk in response.body_iterator:
                    response_body += chunk

                new_response = Response(
                    content=response_body,
                    status_code=response.status_code,
                    headers=dict(response.headers),
                    media_type=response.media_type,
                )

                try:
                    data = json.loads(response_body.decode("utf-8"))
                    if isinstance(data, dict):
                        msg_text = str(data.get("message") or data.get("detail") or "")
                except (json.JSONDecodeError, UnicodeDecodeError):
                    pass

                log_line = f"API {method} {path} | Status: {status_str} | Time: {duration_ms:.2f}ms | Client: {client_ip}"
                if msg_text:
                    log_line += f" | Message: {msg_text}"

                logger.info(log_line)
                return new_response
            else:
                logger.info(
                    f"API {method} {path} | Status: {status_str} | Time: {duration_ms:.2f}ms | Client: {client_ip}"
                )
                return response

        return response
    except Exception as e:
        duration_ms = (time.perf_counter() - start_time) * 1000
        logger.error(
            f"API {method} {path} | ERROR | Time: {duration_ms:.2f}ms | Client: {client_ip} | Lỗi: {e}",
            exc_info=True,
        )
        raise
    finally:
        request_context.reset(token)
