"""Central, environment-driven configuration.

Every knob can be overridden with an environment variable or a local ``.env`` file
(see ``.env.example``), so the same suite can run locally, in Docker and in CI unchanged.
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(ROOT_DIR / ".env")


def _env_str(name: str, default: str) -> str:
    return os.getenv(name, default).strip()


def _env_int(name: str, default: int) -> int:
    return int(os.getenv(name, str(default)))


def _env_bool(name: str, default: bool = False) -> bool:
    return os.getenv(name, str(default)).strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Settings:
    base_url: str
    default_timeout_ms: int
    navigation_timeout_ms: int
    expect_timeout_ms: int
    slow_mo_ms: int
    viewport_width: int
    viewport_height: int
    locale: str
    timezone_id: str
    allow_registration: bool
    test_user_email: str | None
    test_user_password: str | None
    pacing_seconds: float
    reports_dir: Path

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(
            base_url=_env_str("BASE_URL", "https://sauce-demo.myshopify.com").rstrip("/"),
            default_timeout_ms=_env_int("DEFAULT_TIMEOUT_MS", 15_000),
            navigation_timeout_ms=_env_int("NAVIGATION_TIMEOUT_MS", 30_000),
            expect_timeout_ms=_env_int("EXPECT_TIMEOUT_MS", 8_000),
            slow_mo_ms=_env_int("SLOW_MO_MS", 0),
            viewport_width=_env_int("VIEWPORT_WIDTH", 1280),
            viewport_height=_env_int("VIEWPORT_HEIGHT", 800),
            locale=_env_str("LOCALE", "en-GB"),
            timezone_id=_env_str("TIMEZONE_ID", "Asia/Manila"),
            allow_registration=_env_bool("ALLOW_REGISTRATION", False),
            test_user_email=os.getenv("TEST_USER_EMAIL") or None,
            test_user_password=os.getenv("TEST_USER_PASSWORD") or None,
            pacing_seconds=float(os.getenv("PACING_SECONDS", "1.0")),
            reports_dir=ROOT_DIR / "reports",
        )


settings = Settings.from_env()
