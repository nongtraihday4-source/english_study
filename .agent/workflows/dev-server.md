---
description: Khởi động môi trường development cho English Study (Django backend + Vite frontend)
---

# Khởi động Dev Server — English Study

## Yêu cầu hệ thống
- Python virtualenv đã active (`source .venv/bin/activate`)
- PostgreSQL đang chạy (database `english_study_dev` đã tạo)
- Redis đang chạy (`redis-server`)
- Node.js 18+ và npm đã cài

---

## Bước 1: Khởi động Redis (nếu chưa chạy)

```bash
redis-server --daemonize yes
```

## Bước 2: Khởi động Django Backend

```bash
cd backend
source ../.venv/bin/activate
DJANGO_SETTINGS_MODULE=english_study.settings.development python manage.py runserver 0.0.0.0:8000
```

Backend sẽ chạy tại: http://localhost:8000  
API Docs (Swagger): http://localhost:8000/api/schema/swagger-ui/

## Bước 3: Khởi động Celery Worker (cho AI grading)

Mở terminal mới:

```bash
cd backend
source ../.venv/bin/activate
DJANGO_SETTINGS_MODULE=english_study.settings.development celery -A english_study worker -l info -Q ai_grading,default
```

> ⚠️ Celery bắt buộc phải chạy nếu test tính năng Speaking/Writing AI grading. Nếu skip, tasks sẽ bị pending.

## Bước 4: Khởi động Vue Frontend

Mở terminal mới:

```bash
cd frontend
npm run dev
```

Frontend sẽ chạy tại: http://localhost:5173  
Proxy API calls đến Django được cấu hình trong `vite.config.js`.

---

## Checklist sau khởi động

- [ ] http://localhost:8000/api/v1/health/ trả về `{"status": "ok"}`
- [ ] http://localhost:5173/ hiển thị trang login
- [ ] Login với `admin@gmail.com` / `12345678a.` thành công
- [ ] Redis CLI: `redis-cli ping` trả về `PONG`
- [ ] Celery: Log hiện `celery@hostname ready.`

---

## Troubleshooting

| Lỗi | Nguyên nhân | Fix |
|-----|-------------|-----|
| `Error connecting to PostgreSQL` | PostgreSQL chưa chạy | `sudo service postgresql start` |
| `CORS error` trên frontend | `CORS_ALLOWED_ORIGINS` thiếu localhost:5173 | Kiểm tra `settings/development.py` |
| `Redis connection refused` | Redis chưa chạy | `redis-server --daemonize yes` |
| `ModuleNotFoundError` | Venv chưa active hoặc thiếu package | `pip install -r requirements.txt` |
| Trang trắng trên frontend | Vite build fail | Kiểm tra console, chạy `npm install` |
