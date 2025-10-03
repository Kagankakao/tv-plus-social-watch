from pydantic import BaseModel
import os


class Settings(BaseModel):
    app_name: str = "tv-plus-watch-party"
    debug: bool = True
    database_url: str | None = None
    db_host: str | None = None
    db_user: str | None = None
    db_password: str | None = None
    db_port: int = 5432
    db_database: str = "postgres"


settings = Settings(
    database_url=os.getenv("DATABASE_URL"),
    db_host=os.getenv("DB_HOST"),
    db_user=os.getenv("DB_USER"),
    db_password=os.getenv("DB_PASSWORD"),
    db_port=int(os.getenv("DB_PORT", "5432")),
    db_database=os.getenv("DB_DATABASE", "postgres"),
)


