from decouple import config


TOKEN = config("TOKEN", cast=str)

DB_USER = config("DB_USER", cast=str)
DB_NAME = config("DB_NAME", cast=str)
DB_PASS = config("DB_PASS", cast=str)
DB_HOST = config("DB_HOST", cast=str)
DB_PORT = config("DB_PORT", cast=int)

TORTOISE_ORM = {
    "connections": {
        "default": f"postgres://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    },
    "apps": {
        "models": {
            "models": ["data.models", "aerich.models"],
            "default_connection": "default",
        },
    },
    "use_tz": True,
}

DB_HOST_DEV = config("DB_HOST_DEV", cast=str)
DB_PORT_DEV = config("DB_PORT_DEV", cast=int)

TORTOISE_ORM_DEV = {
    "connections": {
        "default": f"postgres://{DB_USER}:{DB_PASS}@{DB_HOST_DEV}:{DB_PORT_DEV}/{DB_NAME}"
    },
    "apps": {
        "models": {
            "models": ["data.models", "aerich.models"],
            "default_connection": "default",
        },
    },
    "use_tz": True,
}

REDIS_HOST = config("REDIS_HOST", cast=str)
REDIS_PORT = config("REDIS_PORT", cast=int)
REDIS_PASSWORD = config("REDIS_PASSWORD", cast=str)

ADMIN_ID = config("ADMIN_ID", cast=int)

LABS_NAMES_LIST = ["ОПД", "ПРОГА", "ИНФА", "БД", "ВЕБ", "ЯПЫ"]
