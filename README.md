# SportSlot Backend API

Hệ thống Backend cho nền tảng quản lý và đặt sân thể thao trực tuyến (**SportSlot**), được xây dựng trên nền tảng **FastAPI**, **SQLAlchemy 2.0 (Async)**, **PostgreSQL 16** và trình quản lý gói hiện đại **uv**.

---

## 🛠 Danh sách Công nghệ & Thư viện (Tech Stack)

### 1. Yêu cầu Môi trường
- **Python**: `>= 3.14` (quản lý qua `.python-version`)
- **Package & Project Manager**: [uv](https://astral.sh/uv/) (Astral)
- **Container**: Docker & Docker Compose (PostgreSQL 16 Alpine)

### 2. Thư viện chính (Runtime Dependencies)
| Gói thư viện | Phiên bản | Vai trò & Mục đích sử dụng |
| :--- | :--- | :--- |
| **`fastapi[standard]`** | `>= 0.162.2` | Framework API chính, tích hợp sẵn Uvicorn, Starlette, Pydantic v2. |
| **`sqlalchemy[asyncio]`** | `>= 2.1.8` | ORM bất đồng bộ hiện đại để thao tác với cơ sở dữ liệu. |
| **`asyncpg`** | `>= 0.32.0` | Driver kết nối bất đồng bộ hiệu năng cao cho PostgreSQL. |
| **`alembic`** | `>= 1.20.1` | Quản lý lịch sử và thực thi Database Migrations. |
| **`pydantic-settings`** | `>= 2.16.2` | Đọc và validate biến môi trường từ `.env` theo chuẩn Type-safe. |
| **`cloudinary`** | `>= 1.47.0` | SDK lưu trữ và tối ưu hóa hình ảnh (sân bóng, avatar...). |
| **`pwdlib[argon2]`** | `>= 0.3.1` | Mã hóa mật khẩu bảo mật cao với thuật toán Argon2id. |
| **`pyjwt`** | `>= 2.15.1` | Tạo, ký và xác thực JWT (Access Token, Refresh Token). |
| **`uuid-utils`** | `>= 1.2.0` | Sinh UUIDv7 có sắp xếp thời gian làm khóa chính (Primary Key). |
| **`apscheduler`** | `>= 3.11.3` | Lập lịch tác vụ nền định kỳ (dọn dẹp OTP, reset lượt login...). |
| **`python-multipart`** | `>= 0.0.33` | Xử lý dữ liệu form-data và upload file. |

### 3. Thư viện phát triển & kiểm thử (Dev Dependencies)
| Gói thư viện | Phiên bản | Vai trò & Mục đích sử dụng |
| :--- | :--- | :--- |
| **`pytest`** | `>= 9.2.0` | Khung kiểm thử tự động (Unit / Integration Test). |
| **`pytest-asyncio`** | `>= 1.4.1.post1` | Hỗ trợ viết test cho các hàm `async/await`. |
| **`httpx`** | `>= 0.28.1` | HTTP client gửi request kiểm thử API thông qua `AsyncClient`. |
| **`aiosqlite`** | `>= 0.22.1` | SQLite Async phục vụ chạy test cô lập (in-memory) không cần DB thật. |
| **`ruff`** | `>= 0.17.4` | Linter và code formatter tự động siêu tốc. |
| **`mypy`** | `>= 2.4.1` | Kiểm tra tính nhất quán của kiểu dữ liệu tĩnh. |

---

## 📁 Cấu trúc Thư mục Dự án

```text
sportslot_be/
├── alembic/                # Cấu hình và các phiên bản migration DB
│   └── versions/           # Danh sách các file migration
├── app/                    # Mã nguồn chính của ứng dụng
│   ├── core/               # Các module kỹ thuật dùng chung
│   │   ├── config.py       # Cấu hình tập trung (Pydantic Settings)
│   │   ├── logging.py      # Hệ thống log ghi Terminal & File theo timestamp
│   │   ├── middlewares.py  # HTTP Middleware (log request, latency, status)
│   │   └── service_checker.py # Kiểm tra kết nối dịch vụ (DB, SMTP, Cloudinary)
│   ├── models/             # SQLAlchemy ORM Models (User, Venue, Booking...)
│   ├── schemas/            # Pydantic Schemas (Request/Response validation)
│   ├── repositories/       # Tầng truy vấn cơ sở dữ liệu
│   ├── services/           # Tầng logic nghiệp vụ
│   ├── routers/            # Các endpoint API
│   └── main.py             # Entrypoint khởi tạo FastAPI app & mount components
├── knowledge/              # Tài liệu thiết kế chi tiết (DB, APIs, RBAC...)
├── logs/                   # Thư mục lưu file log theo phiên (bị git ignore)
├── .env.example            # Mẫu khai báo biến môi trường
├── docker-compose.yml      # Cấu hình PostgreSQL 16 container
├── pyproject.toml          # Khai báo cấu hình dự án và dependencies
└── README.md               # Tài liệu hướng dẫn sử dụng
```

---

## 🚀 Hướng dẫn Cài đặt & Khởi chạy

### 1. Chuẩn bị môi trường
Yêu cầu đã cài đặt trên máy:
- **Python >= 3.14**
- **Docker & Docker Compose**
- **uv** (trình quản lý gói Python thế hệ mới):
  ```bash
  # Linux / macOS / WSL:
  curl -LsSf https://astral.sh/uv/install.sh | sh

  # Windows (PowerShell):
  powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
  ```

### 2. Cài đặt Dependencies
Cài đặt toàn bộ thư viện chính và thư viện dev bằng `uv`:
```bash
uv sync
```

### 3. Cấu hình Biến môi trường (`.env`)
Tạo file `.env` từ file mẫu:
```bash
cp .env.example .env
```
Điền các giá trị thực tế vào file `.env`:
```ini
# --- Database (Khớp với docker-compose.yml) ---
DATABASE_URL=postgresql+asyncpg://sportslot:123456@localhost:5439/sportslot

# --- Security & JWT ---
SECRET_KEY=your_jwt_secret_key_here
OTP_SECRET_KEY=your_otp_secret_key_here

# --- SMTP (Gửi OTP qua Gmail) ---
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_gmail_app_password
SMTP_FROM_EMAIL=your_email@gmail.com

# --- Cloudinary (Lưu trữ ảnh) ---
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret

# --- CORS ---
CORS_ORIGINS=http://localhost:3000
```

### 4. Khởi động Cơ sở dữ liệu (PostgreSQL)
Khởi chạy container PostgreSQL nền bằng Docker:
```bash
docker compose up -d
```
*(Cổng kết nối mặc định của Database là `5439:5432`, volume lưu tại `pgdata`)*.

### 5. Áp dụng Database Migrations
Chạy migration để cập nhật cấu trúc bảng vào PostgreSQL:
```bash
uv run alembic upgrade head
```

### 6. Khởi động Ứng dụng
Khởi chạy server ở chế độ phát triển (auto-reload):
```bash
uv run fastapi dev app/main.py
```
Khi khởi động thành công, hệ thống sẽ tự động kiểm tra kết nối tới các dịch vụ:
```text
==================================================
[STARTUP] Đang kiểm tra kết nối dịch vụ...
[LOG FILE] logs/app_2026-11-16_10-00-00.log
==================================================
  [OK]     [Database] connected
  [OK]     [Smtp] connected
  [OK]     [Cloudinary] connected
==================================================
```

---

## 📖 Tài liệu API & Giám sát

Sau khi server khởi động, bạn có thể truy cập các đường dẫn sau:

| Đường dẫn | Mô tả |
| :--- | :--- |
| **`http://localhost:8000/docs`** | Giao diện tài liệu Swagger UI tương tác trực tiếp |
| **`http://localhost:8000/redoc`** | Giao diện tài liệu ReDoc chi tiết |
| **`http://localhost:8000/health`** | Endpoint kiểm tra sức khỏe hệ thống & trạng thái các dịch vụ |

---

## 📝 Cơ chế Logging

- Mỗi lần chạy server, hệ thống tự động sinh một file log độc lập mang tên theo timestamp trong thư mục `logs/` (ví dụ: `logs/app_2026-11-16_10-00-00.log`).
- Khi có bất kỳ request API nào được gọi, hệ thống sẽ tự động log ngắn gọn:
  ```text
  2026-11-16 10:00:05 | INFO | API GET /health | Status: 200 OK | Time: 1.15ms | Client: 127.0.0.1 | Message: Server is running
  ```
- Dữ liệu thô và mã HTML tài liệu được loại bỏ để đảm bảo file log sạch sẽ, bảo mật và không bị phình to dung lượng.

---

## 🧪 Công cụ Kiểm tra Chất lượng Mã nguồn

- **Kiểm tra lỗi và format mã nguồn (Ruff)**:
  ```bash
  uv run ruff check .
  uv run ruff format .
  ```
- **Kiểm tra kiểu dữ liệu tĩnh (Mypy)**:
  ```bash
  uv run mypy app
  ```
- **Chạy toàn bộ Unit/Integration Tests (Pytest)**:
  ```bash
  uv run pytest
  ```
