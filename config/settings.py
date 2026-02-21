"""
Settings Configuration
======================
Centralised, type-safe configuration via Pydantic Settings.

All values have sensible defaults and can be overridden with environment
variables or a ``.env`` file.  No nested config objects, no magic
``__getattribute__`` — just flat fields.

Usage:
    from config import settings

    settings.base_url        # "https://www.saucedemo.com"
    settings.headless         # True
    settings.default_timeout  # 30000
"""

from functools import lru_cache
from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Single, flat configuration model for the test framework."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── Application Under Test ───────────────────────────────────────────
    base_url: str = Field(
        default="https://www.saucedemo.com",
        description="Base URL for the application under test",
    )

    # ── Test Users ───────────────────────────────────────────────────────
    standard_user: str = "standard_user"
    standard_password: str = "secret_sauce"
    locked_out_user: str = "locked_out_user"
    problem_user: str = "problem_user"
    performance_glitch_user: str = "performance_glitch_user"
    default_password: str = "secret_sauce"

    # ── Browser ──────────────────────────────────────────────────────────
    browser: str = Field(default="chromium", description="chromium | firefox | webkit")
    headless: bool = True
    viewport_width: int = Field(default=1920, ge=320, le=3840)
    viewport_height: int = Field(default=1080, ge=240, le=2160)
    slow_mo: int = Field(default=0, ge=0, le=5000)
    ignore_https_errors: bool = False
    accept_downloads: bool = True
    user_agent: str | None = None

    # ── Timeouts ─────────────────────────────────────────────────────────
    default_timeout: int = Field(
        default=30000, ge=5000, le=120000, description="Default timeout in ms",
    )

    # ── Logging ──────────────────────────────────────────────────────────
    log_level: str = Field(default="INFO")
    log_file_path: str = "logs/test_execution.log"

    # ── Reporting ────────────────────────────────────────────────────────
    report_dir: str = "reports"

    # ── Derived paths ────────────────────────────────────────────────────
    @property
    def project_root(self) -> Path:
        return Path(__file__).parent.parent

    @property
    def reports_dir(self) -> Path:
        return self.project_root / self.report_dir

    @property
    def logs_dir(self) -> Path:
        return self.project_root / Path(self.log_file_path).parent

    # ── Validators ───────────────────────────────────────────────────────
    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        valid = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        upper = v.upper()
        if upper not in valid:
            raise ValueError(f"log_level must be one of {valid}")
        return upper

    def model_post_init(self, __context: object) -> None:
        """Create required directories on startup."""
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        self.reports_dir.mkdir(parents=True, exist_ok=True)


@lru_cache
def get_settings() -> Settings:
    """Singleton settings instance."""
    return Settings()


settings = get_settings()
