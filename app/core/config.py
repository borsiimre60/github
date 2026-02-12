import os


class Settings:
    app_name: str = "SzakiSzerviz PRO CORE"
    database_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg2://postgres:postgres@localhost:5432/szakiszerviz",
    )


settings = Settings()
