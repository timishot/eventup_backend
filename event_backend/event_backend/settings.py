import os
from datetime import timedelta

import dj_database_url
from pathlib import Path




from django.conf.global_settings import AUTH_USER_MODEL, ALLOWED_HOSTS


BASE_DIR = Path(__file__).resolve().parent.parent




# SECRET_KEY = os.environ.get('SECRET_KEY')
SECRET_KEY = os.environ.get('SECRET_KEY', "timishot")


DEBUG = os.environ.get("DEBUG", "False").lower() == "true"
# DEBUG = bool(os.environ.get("DEBUG", default=True))

ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "localhost").split(" ")
# ALLOWED_HOSTS = os.environ.get("DJANGO_ALLOWED_HOSTS", "localhost").split(" ")
AUTH_USER_MODEL = 'useraccount.User'


SITE_ID = 1

WEBSITE_URL = 'http://localhost:8000'

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=60),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": False,
    "BLACKLIST_AFTER_ROTATION": False,
    "UPDATE_LAST_LOGIN": True,
    "SIGNING_KEY": os.environ.get("SECRET_KEY", "timishot"),
    "ALGORITHM": "HS256",
}

ACCOUNT_USER_MODEL_USERNAME_FIELD = "username"
ACCOUNT_USERNAME_REQUIRED = True
ACCOUNT_SIGNUP_FIELDS = ['email*', 'password1*', 'password2*', 'username']
ACCOUNT_AUTHENTICATION_METHOD = 'email'

ACCOUNT_EMAIL_VERIFICATION = "none"


REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
}



CORS_ALLOWED_ORIGINS = [ 'http://127.0.0.1:8000', 'http://localhost:8000',  'http://localhost:3000',  "https://eventup-backend.onrender.com", "https://eventup-frontend.vercel.app" ]
CORS_ALLOW_CREDENTIALS = True

REST_AUTH = {
    "USE_JWT": True,
    "JWT_AUTH_HTTPONLY": False,
}
# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework.authtoken',

    'allauth',
    'allauth.account',
    'allauth.socialaccount',

    'channels',

    'dj_rest_auth',
    'dj_rest_auth.registration',

    'corsheaders',

    'useraccount',
    'event',
    'category',
    'order',
    'poll',
    'qns',
    'relationship',



]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'allauth.account.middleware.AccountMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

]

ROOT_URLCONF = 'event_backend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'event_backend.wsgi.application'
ASGI_APPLICATION = "event_backend.asgi.application"

# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

if os.getenv("DATABASE_URLS"):
    DATABASES = {
        "default": dj_database_url.parse(os.environ.get("DATABASE_URLS"))
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': os.environ.get("SQL_ENGINE", "django.db.backends.postgresql"),
            'NAME': os.environ.get("SQL_DATABASE", "event_db"),
            'USER': os.environ.get("SQL_USER", "postgresuser"),
            'PASSWORD': os.environ.get("SQL_PASSWORD", "postgres"),
            'HOST': os.environ.get("SQL_HOST", "localhost"),
            'PORT': os.environ.get("SQL_PORT", "5432"),
        }
    }

# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/



# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [os.environ.get("REDIS_HOST", "redis")],
        },
    },
}

STATIC_URL = 'static/'
MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'
