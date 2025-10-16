import os
from pathlib import Path
from celery.schedules import crontab
from django.utils.translation import gettext_lazy as _


BASE_DIR = Path(__file__).resolve().parent.parent

LOG_DIR = os.path.join(BASE_DIR, 'logs')
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-2bg7z8rbm#$kaptr%*5nkb4ofmivf5!$sc!x&2qj$co2e9ihon'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
ALLOWED_HOSTS = ['127.0.0.1']


CELERY_BROKER_URL = 'memory://'
CELERY_RESULT_BACKEND = 'cache+memory://'
CELERY_TASK_ALWAYS_EAGER = True  # Задачи выполняются синхронно
CELERY_TASK_EAGER_PROPAGATES = True


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'django_filters',
    'news',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google', # Google провайдер
    'allauth.socialaccount.providers.yandex', # Yandex провайдер
    'django_celery_beat',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
#    'allauth.account.middleware.AccountMiddleware', # Allauth middleware
]

ROOT_URLCONF = 'newsportal.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request', # Обязательно для allauth
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'news.context_processors.user_groups',
            ],
        },
    },
]

WSGI_APPLICATION = 'newsportal.wsgi.application'

AUTHENTICATION_BACKENDS = [
    # Нужен для входа в админку Django
    'django.contrib.auth.backends.ModelBackend',
    # Специфичные методы аутентификации allauth
    'allauth.account.auth_backends.AuthenticationBackend',
]

# Настройки сайта
SITE_ID = 1

# Настройки allauth
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_USERNAME_REQUIRED = True
ACCOUNT_AUTHENTICATION_METHOD = 'username_email'
ACCOUNT_EMAIL_VERIFICATION = 'optional'  # или 'mandatory', 'none'


LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/'
ACCOUNT_LOGOUT_REDIRECT_URL = '/'
ACCOUNT_LOGOUT_ON_GET = False  # Должно быть False для безопасности
ACCOUNT_SESSION_REMEMBER = True

# Настройки CSRF
CSRF_COOKIE_SECURE = False  # True для production с HTTPS
CSRF_COOKIE_HTTPONLY = False
CSRF_USE_SESSIONS = False

# ВРЕМЕННО
CSRF_TRUSTED_ORIGINS = [
    'http://localhost:8000',
    'http://127.0.0.1:8000',
]

# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
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

USE_I18N = True
USE_L10N = True
USE_TZ = True

LANGUAGE_CODE = 'ru'
TIME_ZONE = 'Europe/Moscow'

LOCALE_PATHS = [
    os.path.join(BASE_DIR, 'locale')
]

LANGUAGE_CODE = 'ru'  # или 'en-us'

LANGUAGES = [
    ('ru', 'Russian'),
    ('en', 'English'),
]

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]
STATIC_ROOT = BASE_DIR / 'staticfiles'


# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

SOCIALACCOUNT_PROVIDERS = {
    'yandex': {
        'SCOPE': ['login:email', 'login:info', 'login:avatar'],
        'AUTH_PARAMS': {'access_type': 'online'},
        'METHOD': 'oauth2',
    },
    'google': {
        'SCOPE': ['profile', 'email'],
        'AUTH_PARAMS': {'access_type': 'online'},
    }
}

ADMINS = [
    ('Admin Name', 'admin@example.com'),
]

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend' # Для тестирования - письма в консоль

#EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
#EMAIL_HOST = 'smtp.yandex.ru'
#EMAIL_PORT = 587
#EMAIL_USE_TLS = True
#EMAIL_HOST_USER = 'email_login' #не буду указывать настоящие данные, т.к. не безопасно
#EMAIL_HOST_PASSWORD = 'app_password'
#DEFAULT_FROM_EMAIL = 'News Portal <email@yandex.ru>'
#SERVER_EMAIL = 'email@yandex.ru'

# Дополнительные настройки allauth для email
ACCOUNT_EMAIL_SUBJECT_PREFIX = '[News Portal] '
ACCOUNT_EMAIL_VERIFICATION = 'optional'  # или 'mandatory' для обязательной верификации


CELERY_BEAT_SCHEDULE = {
    'send-weekly-digest': {
        'task': 'news.tasks.send_weekly_digest',
        'schedule': crontab(day_of_week=1, hour=8, minute=0),  # Понедельник 8:00
    },
}


# Добавляем кэш-бэкенд (для теста)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}

# Или для Redis (для прода)
#CACHES = {
#    'default': {
#        'BACKEND': 'django_redis.cache.RedisCache',
#        'LOCATION': 'redis://127.0.0.1:6379/1',
#        'OPTIONS': {
#            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
#        },
#         'KEY_PREFIX': 'newsportal'
#    }
#}

CACHE_MIDDLEWARE_SECONDS = 30

# Настройки логирования
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'console_debug': {
            'format': '{asctime} - {levelname} - {message}',
            'style': '{',
        },
        'console_warning': {
            'format': '{asctime} - {levelname} - {pathname} - {message}',
            'style': '{',
        },
        'console_error': {
            'format': '{asctime} - {levelname} - {pathname} - {message}\n{exc_info}',
            'style': '{',
        },
        'general_file': {
            'format': '{asctime} - {levelname} - {module} - {message}',
            'style': '{',
        },
        'errors_file': {
            'format': '{asctime} - {levelname} - {message}\n{pathname}\n{exc_info}',
            'style': '{',
        },
        'security_file': {
            'format': '{asctime} - {levelname} - {module} - {message}',
            'style': '{',
        },
        'email': {
            'format': '{asctime} - {levelname} - {message}\n{pathname}',
            'style': '{',
        },
    },
    'filters': {
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
    },
    'handlers': {
        # Консоль - только при DEBUG=True
        'console_debug': {
            'level': 'DEBUG',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
            'formatter': 'console_debug',
        },
        'console_warning': {
            'level': 'WARNING',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
            'formatter': 'console_warning',
        },
        'console_error': {
            'level': 'ERROR',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
            'formatter': 'console_error',
        },
        # Файл general.log - только при DEBUG=False
        'general_file': {
            'level': 'INFO',
            'filters': ['require_debug_false'],
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'general.log'),
            'formatter': 'general_file',
        },
        # Файл errors.log
        'errors_file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'errors.log'),
            'formatter': 'errors_file',
        },
        # Файл security.log
        'security_file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'security.log'),
            'formatter': 'security_file',
        },
        # Email - только при DEBUG=False
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler',
            'formatter': 'email',
            'include_html': False,
        },
    },
    'loggers': {
        # Основной логгер django - в консоль
        'django': {
            'handlers': ['console_debug', 'console_warning', 'console_error'],
            'level': 'DEBUG',
            'propagate': False,
        },
        # Общий логгер для general.log
        'django': {
            'handlers': ['general_file'],
            'level': 'INFO',
            'propagate': False,
        },
        # Логгеры для errors.log
        'django.request': {
            'handlers': ['errors_file', 'mail_admins'],
            'level': 'ERROR',
            'propagate': False,
        },
        'django.server': {
            'handlers': ['errors_file', 'mail_admins'],
            'level': 'ERROR',
            'propagate': False,
        },
        'django.template': {
            'handlers': ['errors_file'],
            'level': 'ERROR',
            'propagate': False,
        },
        'django.db.backends': {
            'handlers': ['errors_file'],
            'level': 'ERROR',
            'propagate': False,
        },
        # Логгер для security.log
        'django.security': {
            'handlers': ['security_file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
    'root': {
        'handlers': ['console_debug', 'console_warning', 'console_error'],
        'level': 'DEBUG',
    },
}

# Временная проверка логирования
if DEBUG:
    print("=== DEBUG MODE ===")
    print("Сообщения в general.log не будут записываться при DEBUG=True")
else:
    print("=== PRODUCTION MODE ===")
    print("Сообщения будут записываться в general.log")