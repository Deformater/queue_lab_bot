from decouple import config


TOKEN = config('TOKEN', cast=str)

DB_USER=config('DB_USER', cast=str)
DB_NAME=config('DB_NAME', cast=str)
DB_PASS=config('DB_PASS', cast=str)
DB_HOST=config('DB_HOST', cast=str)
DB_PORT=config('DB_PORT', cast=int)

TORTOISE_ORM = {
    "connections": {"default": f"postgres://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"},
    "apps": {
        "models": {
            "models": ["data.models", "aerich.models"],
            "default_connection": "default",
        },
    },
    "use_tz": True
}
