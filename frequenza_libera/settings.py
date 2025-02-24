"""
Django settings for frequenza_libera project.

Generated by 'django-admin startproject' using Django 4.2.3.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""
import os
import environ
import dj_database_url

env = environ.Env(
    # set casting, default value
    DEBUG=(bool, False)
)

# Set the project base directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Take environment variables from .env file
environ.Env.read_env(os.path.join(BASE_DIR, ".env"))

# False if not in os.environ because of casting above
DEBUG = env("DEBUG")

# SECURITY SETTINGS (if DEBUG is True, these settings are ignored)
# This is a list of host/domain names that the application can serve.
# Django will only accept HTTP requests whose Host header matches an entry in this list.
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["localhost"])
# When Django's CSRF middleware checks incoming POST requests,
# it ensures that the request comes from one of these trusted origins (including the protocol, such as "https://")
CSRF_TRUSTED_ORIGINS = env.list(
    "CSRF_TRUSTED_ORIGINS", default=["http://localhost", "https://localhost"]
)
# CORS settings
CORS_ALLOW_ALL_ORIGINS: bool = env.bool("CORS_ALLOW_ALL_ORIGINS", default=False)

if not CORS_ALLOW_ALL_ORIGINS:
    CORS_ALLOWED_ORIGINS: list[str] = env.list(
        "CORS_ALLOWED_ORIGINS", default=["http://localhost:3000"]
    )
else:
    CORS_ALLOWED_ORIGINS = []

SECURE_SSL_REDIRECT: bool = env.bool("SECURE_SSL_REDIRECT", default=True)
SESSION_COOKIE_SECURE: bool = env.bool("SESSION_COOKIE_SECURE", default=True)
CSRF_COOKIE_SECURE: bool = env.bool("CSRF_COOKIE_SECURE", default=True)

# Application definition
INSTALLED_APPS = [
    "corsheaders",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "podcast.apps.PodcastConfig",
    "podcaster.apps.PodcasterConfig",
    "podcast_collection.apps.PodcastCollectionConfig",
]

STORAGES = {
    "default": {
        "BACKEND": "django_s3_storage.storage.S3Storage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

# Static files (CSS, JavaScript, Images)
STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")


MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "frequenza_libera.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "frequenza_libera.wsgi.application"

postgres_dict_config = {
    "ENGINE": "django.db.backends.postgresql",
    "NAME": env("PGDATABASE"),
    "USER": env("PGUSER"),
    "PASSWORD": env("PGPASSWORD"),
    "HOST": env("PGHOST"),
    "PORT": env("PGPORT"),
    "CONN_HEALTH_CHECKS": True,
    "OPTIONS": {"sslmode": "require"},
}

# Database
DATABASES = {
    "default": dj_database_url.config(
        default=env("DATABASE_URL"), conn_max_age=600, ssl_require=True
    ),
}
FILE_UPLOAD_MAX_MEMORY_SIZE = 262144000
DATA_UPLOAD_MAX_MEMORY_SIZE = 262144000
DATA_UPLOAD_MAX_NUMBER_FIELDS = 10240
# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# Internationalization
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# Default primary key field type
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Project settings
# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env("DJANGO_SECRET_KEY")

AWS_REGION = env("AWS_REGION", default="eu-north-1")
AWS_ACCESS_KEY_ID = env("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = env("AWS_SECRET_ACCESS_KEY")
AWS_S3_BUCKET_NAME = env("AWS_S3_BUCKET_NAME")
AUDIO_UPLOAD_FOLDER = "MP3_PODCAST/"
COVER_UPLOAD_FOLDER = "podcast_covers/"
PODCAST_LIMIT = env.int("PODCAST_LIMIT", default=1000)
EMAIL = env("EMAIL", default="rfl.radiofrequenzalibera@gmail.com")
