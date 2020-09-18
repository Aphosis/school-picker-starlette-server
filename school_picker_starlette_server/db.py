from databases import Database, DatabaseURL
from starlette.config import Config

from .config import config


def create_db(config: Config) -> Database:
    url = config("DATABASE_URL", cast=DatabaseURL)
    database = Database(url)
    return database


database = create_db(config)
