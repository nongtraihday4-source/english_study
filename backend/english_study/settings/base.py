"""
English Study LMS — Base Settings
Múi giờ: Asia/Ho_Chi_Minh | DB: PostgreSQL | Cache: Redis
"""
from datetime import timedelta
from pathlib import Path

from decouple import config

BASE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = config("SECRET_KEY", default="dev-insecure-key-change-in-prod")
DEBUG = config("DEBUG", default=True, cast=bool)
ALLOWED_HOSTS = config("ALLOWED_HOSTS", default="*").split(",")

# ─── Apps ────────────────────────────────────────────────────────────────────
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Third-party
    "rest_framework",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
    "corsheaders",
    "django_filters",
    "drf_spectacular",
    # Local apps
    "apps.users",
    "apps.curriculum",
    "apps.exercises",
    "apps.progress",
    "apps.vocabulary",
    "apps.gamification",
    "apps.payments",
    "apps.notifications",
    "apps.grammar",
    "apps.pronunciation",
    "apps.teacher",
    "apps.admin_portal",
    "apps.support",
    "apps.skill_practice",
    "apps.ai",
]

# ─── Middleware ───────────────────────────────────────────────────────────────
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "utils.middleware.RequestLoggingMiddleware",
]

ROOT_URLCONF = "english_study.urls"
WSGI_APPLICATION = "english_study.wsgi.application"
ASGI_APPLICATION = "english_study.asgi.application"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ]
        },
    }
]

# ─── Database ─────────────────────────────────────────────────────────────────
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": config("DB_NAME", default="english_study_db"),
        "USER": config("DB_USER", default="postgres"),
        "PASSWORD": config("DB_PASSWORD", default="postgres"),
        "HOST": config("DB_HOST", default="localhost"),
        "PORT": config("DB_PORT", default="5432"),
        "OPTIONS": {
            # Force PostgreSQL server-side timezone
            "options": "-c timezone=Asia/Ho_Chi_Minh",
        },
        "CONN_MAX_AGE": 60,
    }
}

# ─── Auth ─────────────────────────────────────────────────────────────────────
AUTH_USER_MODEL = "users.User"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {"min_length": 8},
    },
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.Argon2PasswordHasher",  # Primary: Argon2id
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",  # Fallback
]

# ─── Timezone / i18n ──────────────────────────────────────────────────────────
LANGUAGE_CODE = "vi"
TIME_ZONE = "Asia/Ho_Chi_Minh"  # UTC+7, không dịch chuyển DST
USE_I18N = True
USE_TZ = True  # All DateTimeField stored as UTC, displayed in VN time

# ─── Static & Media ───────────────────────────────────────────────────────────
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ─── Cache (Redis) ────────────────────────────────────────────────────────────
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": config("REDIS_URL", default="redis://localhost:6379/1"),
        "OPTIONS": {"CLIENT_CLASS": "django_redis.client.DefaultClient"},
        "KEY_PREFIX": "es_",
        "TIMEOUT": 300,
    }
}
SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default"

# ─── DRF ──────────────────────────────────────────────────────────────────────
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "utils.auth.CookieJWTAuthentication",  # Layer 2: HttpOnly cookie JWT
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_RENDERER_CLASSES": [
        "utils.renderers.VNNumberJSONRenderer",  # VN thousand-separator numbers
    ],
    "DEFAULT_PAGINATION_CLASS": "utils.pagination.StandardPagination",
    "PAGE_SIZE": 20,
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ],
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "anon": "30/min",
        "user": "300/min",
        "login": "5/min",        # Layer 5: Rate limiting on sensitive endpoints
        "submission": "20/min",
        "ai_grading": "10/min",
        "support_public_request": "3/hour",
    },
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "EXCEPTION_HANDLER": "utils.exceptions.custom_exception_handler",
}

# ─── JWT ──────────────────────────────────────────────────────────────────────
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=30),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,   # Layer 1: JTI blacklist on rotation
    "UPDATE_LAST_LOGIN": True,
    "ALGORITHM": "HS256",
    "SIGNING_KEY": config("JWT_SECRET_KEY", default=SECRET_KEY),
    "AUTH_HEADER_TYPES": ("Bearer",),
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
    "TOKEN_TYPE_CLAIM": "token_type",
    "JTI_CLAIM": "jti",
    # Custom serializer: embeds role + account_type into token
    "TOKEN_OBTAIN_SERIALIZER": "apps.users.serializers.CustomTokenObtainPairSerializer",
}

# ─── JWT Cookie config (Layer 2: HttpOnly) ────────────────────────────────────
JWT_COOKIE_NAME = "es_access"
JWT_REFRESH_COOKIE_NAME = "es_refresh"
JWT_COOKIE_SECURE = config("JWT_COOKIE_SECURE", default=False, cast=bool)
JWT_COOKIE_HTTPONLY = True
JWT_COOKIE_SAMESITE = "Lax"
JWT_COOKIE_MAX_AGE = 60 * 30          # 30 minutes
JWT_REFRESH_COOKIE_MAX_AGE = 60 * 60 * 24 * 7  # 7 days

# ─── CORS ─────────────────────────────────────────────────────────────────────
CORS_ALLOWED_ORIGINS = config(
    "CORS_ORIGINS", default="http://localhost:5173"
).split(",")
CORS_ALLOW_CREDENTIALS = True
CORS_EXPOSE_HEADERS = ["X-Total-Count", "X-CSRF-Token"]

# ─── CSRF ─────────────────────────────────────────────────────────────────────
CSRF_COOKIE_HTTPONLY = False  # Frontend JS must read the token
CSRF_COOKIE_SECURE = config("CSRF_COOKIE_SECURE", default=False, cast=bool)
CSRF_COOKIE_SAMESITE = "Lax"

# ─── Celery ───────────────────────────────────────────────────────────────────
CELERY_BROKER_URL = config("REDIS_URL", default="redis://localhost:6379/0")
CELERY_RESULT_BACKEND = config("REDIS_URL", default="redis://localhost:6379/0")
CELERY_TIMEZONE = "Asia/Ho_Chi_Minh"
CELERY_ENABLE_UTC = True
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_ACKS_LATE = True
CELERY_TASK_SOFT_TIME_LIMIT = 120   # 2 min: graceful shutdown
CELERY_TASK_TIME_LIMIT = 180        # 3 min: hard kill

# Celery Beat periodic tasks
# CELERY_ENABLE_UTC=True → 8 AM ICT (UTC+7) = 01:00 UTC
from celery.schedules import crontab  # noqa: E402
CELERY_BEAT_SCHEDULE = {
    # PRD 5.8 Smart Notification — runs every hour, fires per user at their preferred ICT hour
    "flashcard-due-notify-hourly": {
        "task": "vocabulary.check_due_cards_and_notify",
        "schedule": crontab(minute=0),  # top of every hour
    },
}

# ─── AWS S3 ───────────────────────────────────────────────────────────────────
AWS_ACCESS_KEY_ID = config("AWS_ACCESS_KEY_ID", default="")
AWS_SECRET_ACCESS_KEY = config("AWS_SECRET_ACCESS_KEY", default="")
AWS_STORAGE_BUCKET_NAME = config("AWS_STORAGE_BUCKET_NAME", default="english-study-media")
AWS_S3_REGION_NAME = config("AWS_S3_REGION_NAME", default="ap-southeast-1")
AWS_PRESIGNED_URL_EXPIRY = 3600  # 1 hour — layer 1 media access control

# ─── AI Services ──────────────────────────────────────────────────────────────
OPENAI_API_KEY = config("OPENAI_API_KEY", default="")
OPENAI_WHISPER_MODEL = "whisper-1"
OPENAI_GRADING_MODEL = "gpt-4o"
AI_GRADING_TIMEOUT = 90

AI_BASE_URL = config("AI_BASE_URL", default="http://localhost:11434/v1")
AI_MODEL = config("AI_MODEL", default="qwen3.5-9b")

# ─── Logging ──────────────────────────────────────────────────────────────────
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{asctime} [{levelname:8}] {name} | {message}",
            "style": "{",
            "datefmt": "%d/%m/%Y %H:%M:%S",
        },
        "grading": {
            "format": "{asctime} [GRADING ] {name} | {message}",
            "style": "{",
            "datefmt": "%d/%m/%Y %H:%M:%S",
        },
        "auth": {
            "format": "{asctime} [AUTH    ] {name} | {message}",
            "style": "{",
            "datefmt": "%d/%m/%Y %H:%M:%S",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
        "grading_file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": str(BASE_DIR / "logs" / "grading.log"),
            "maxBytes": 1024 * 1024 * 10,  # 10 MB
            "backupCount": 5,
            "formatter": "grading",
        },
        "auth_file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": str(BASE_DIR / "logs" / "auth.log"),
            "maxBytes": 1024 * 1024 * 5,
            "backupCount": 3,
            "formatter": "auth",
        },
    },
    "loggers": {
        "django": {"handlers": ["console"], "level": "WARNING", "propagate": False},
        "django.request": {"handlers": ["console"], "level": "ERROR", "propagate": False},
        # Custom namespaced loggers
        "es.grading": {
            "handlers": ["console", "grading_file"],
            "level": "DEBUG",
            "propagate": False,
        },
        "es.auth": {
            "handlers": ["console", "auth_file"],
            "level": "DEBUG",
            "propagate": False,
        },
        "es.progress": {"handlers": ["console"], "level": "DEBUG", "propagate": False},
        "es.payments": {"handlers": ["console"], "level": "DEBUG", "propagate": False},
        "es.curriculum": {"handlers": ["console"], "level": "DEBUG", "propagate": False},
    },
}

# ─── Email ───────────────────────────────────────────────────────────────────
EMAIL_HOST          = config("EMAIL_HOST",          default="smtp.gmail.com")
EMAIL_PORT          = config("EMAIL_PORT",          default=587, cast=int)
EMAIL_USE_TLS       = config("EMAIL_USE_TLS",       default=True, cast=bool)
EMAIL_HOST_USER     = config("EMAIL_HOST_USER",     default="")
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD", default="")
DEFAULT_FROM_EMAIL  = config("DEFAULT_FROM_EMAIL",  default="English Study <noreply@english-study.vn>")
SERVER_EMAIL        = DEFAULT_FROM_EMAIL
FRONTEND_URL        = config("FRONTEND_URL",        default="http://localhost:5173")

# ─── VNPay ───────────────────────────────────────────────────────────────────
VNPAY_TMN_CODE      = config("VNPAY_TMN_CODE",      default="")
VNPAY_HASH_SECRET   = config("VNPAY_HASH_SECRET",   default="")
VNPAY_PAYMENT_URL   = config("VNPAY_PAYMENT_URL",   default="https://sandbox.vnpayment.vn/paymentv2/vpcpay.html")
VNPAY_RETURN_URL    = config("VNPAY_RETURN_URL",     default="http://localhost:5173/payment/success")

# ─── Stripe ──────────────────────────────────────────────────────────────────
STRIPE_SECRET_KEY       = config("STRIPE_SECRET_KEY",       default="")
STRIPE_PUBLISHABLE_KEY  = config("STRIPE_PUBLISHABLE_KEY",  default="")
STRIPE_WEBHOOK_SECRET   = config("STRIPE_WEBHOOK_SECRET",   default="")

# ─── Certificate ─────────────────────────────────────────────────────────────
CERTIFICATE_PDF_S3_PREFIX = config("CERTIFICATE_PDF_S3_PREFIX", default="certificates/")

# Extra public holidays injected via env (YYYY-MM-DD, comma-separated)
_extra_holidays     = config("PUBLIC_HOLIDAYS_EXTRA", default="")
PUBLIC_HOLIDAYS_EXTRA: list[str] = [d.strip() for d in _extra_holidays.split(",") if d.strip()]

# ─── API Docs ─────────────────────────────────────────────────────────────────
SPECTACULAR_SETTINGS = {
    "TITLE": "English Study LMS API",
    "DESCRIPTION": (
        "Backend API for English Study LMS (A1–C1). "
        "Múi giờ: Asia/Ho_Chi_Minh. Định dạng số: vi-VN."
    ),
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
}
