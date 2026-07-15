import os
from dotenv import load_dotenv

load_dotenv()


class PlatformSettings:
    # ── JWT ──────────────────────────────────────────────────────────────────
    SECRET_KEY: str = os.getenv("JWT_SECRET_KEY") or os.getenv("SECRET_KEY") or "platform-secret-key-change-me"
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))
    COOKIE_SECURE: bool = os.getenv("COOKIE_SECURE", "false").lower() == "true"
    INACTIVITY_MINUTES: int = int(os.getenv("INACTIVITY_MINUTES", "30"))

    # ── Database (platform) ─────────────────────────────────────────────────
    PLATFORM_DB_HOST: str = os.getenv("PLATFORM_DB_HOST") or os.getenv("DB_HOST", "localhost")
    PLATFORM_DB_PORT: int = int(os.getenv("PLATFORM_DB_PORT") or os.getenv("DB_PORT", "5432"))
    PLATFORM_DB_NAME: str = os.getenv("PLATFORM_DB_NAME", "platform")
    PLATFORM_DB_USER: str = os.getenv("PLATFORM_DB_USER") or os.getenv("DB_USER", "postgres")
    PLATFORM_DB_PASSWORD: str = os.getenv("PLATFORM_DB_PASSWORD") or os.getenv("DB_PASSWORD", "postgres123")
    PLATFORM_DB_ENGINE: str = os.getenv("PLATFORM_DB_ENGINE", "postgres")

    # ── Password policy ─────────────────────────────────────────────────────
    PASSWORD_MIN_LENGTH: int = int(os.getenv("PASSWORD_MIN_LENGTH", "4"))
    MAX_LOGIN_ATTEMPTS: int = int(os.getenv("MAX_LOGIN_ATTEMPTS", "5"))
    BLOCK_MINUTES: int = int(os.getenv("BLOCK_MINUTES", "15"))

    # ── SMTP ─────────────────────────────────────────────────────────────────
    SMTP_HOST: str = os.getenv("SMTP_HOST", "")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USER: str = os.getenv("SMTP_USER", "")
    SMTP_PASS: str = os.getenv("SMTP_PASS", "")

    # ── Environment ──────────────────────────────────────────────────────────
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")

    @property
    def database_url(self) -> str:
        if self.PLATFORM_DB_ENGINE == "postgres":
            return (
                f"postgresql+psycopg2://{self.PLATFORM_DB_USER}:{self.PLATFORM_DB_PASSWORD}"
                f"@{self.PLATFORM_DB_HOST}:{self.PLATFORM_DB_PORT}/{self.PLATFORM_DB_NAME}"
            )
        return f"sqlite:///./platform.db"


settings = PlatformSettings()
