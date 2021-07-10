import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '2yoc2zy&ptn^+vwc0#9_^ovb6j$6+liv6h@)(h@_urjxqaxf%f'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# ALLOWED_HOSTS = ['192.168.18.5','0.0.0.0']
# ALLOWED_HOSTS = ['172.16.1.2','0.0.0.0']
# ALLOWED_HOSTS = ['192.168.2.100','0.0.0.0']

# ALLOWED_HOSTS = ['127.0.0.1','192.168.18.139','172.20.10.4','192.168.2.148','172.20.10.4']

ALLOWED_HOSTS = ['191.238.216.168','0.0.0.0','vendas.greenish.com.br','ubt-timur.internal.cloudapp.net']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'core',
    'params',
    'account',
    'crispy_forms',
    'corsheaders',
    'rest_framework',
    'rest_framework.authtoken',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

MIDDLEWARE_CLASSES = (
    'django_user_agents.middleware.UserAgentMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.BrokenLinkEmailsMiddleware',
    'django.middleware.common.CommonMiddleware',
)

ROOT_URLCONF = 'ecomb2b.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR,"templates")],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',  # <-- And here
    ]
}

AUTH_USER_MODEL = 'account.Account'

WSGI_APPLICATION = 'ecomb2b.wsgi.application'

DATA_UPLOAD_MAX_MEMORY_SIZE = 26214400


# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11211',
        'OPTIONS': {
            'server_max_value_length': 1024 * 1024 * 12,
        }
    }
}

USER_AGENTS_CACHE = 'default'

# Password validation
# https://docs.djangoproject.com/en/2.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/2.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'America/Fortaleza'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/

STATIC_URL = '/static/'


STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
]

# STATIC_ROOT = os.path.join(BASE_DIR, "static")

CRISPY_TEMPLATE_PACK = 'bootstrap4'

SESSION_COOKIE_SAMESITE = None

CORS_ORIGIN_ALLOW_ALL = True # If this is used then `CORS_ORIGIN_WHITELIST` will not have any effect
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True
# CORS_ALLOWED_ORIGINS  = [
#     'http://localhost:3000',
#     'http://127.0.0.1:3000'
# ] # If this is used, then not need to use `CORS_ORIGIN_ALLOW_ALL = True`
# CORS_ORIGIN_REGEX_WHITELIST = [
#     'http://localhost:3000',
#     'http://127.0.0.1:3000'
# ]

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'email-ssl.com.br'
EMAIL_PORT = 465
EMAIL_HOST_USER = 'b2b@grupoondas.com.br'
EMAIL_HOST_PASSWORD = 'Ondas@#2021'
EMAIL_USE_TLS = False
EMAIL_USE_SSL = True
