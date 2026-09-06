from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "Satellite Orbit Tracker"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # Database connection string.
    # Uses aiosqlite for async SQLite access. In production, this could be
    # changed to asyncpg for PostgreSQL: "postgresql+asyncpg://user:pass@host/db"
    DATABASE_URL: str = "sqlite+aiosqlite:///./satellites.db"

    # CORS (Cross-Origin Resource Sharing) origins.
    # These are the frontend URLs allowed to make API requests.
    # In production, this should be restricted to the actual frontend domain.
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:8000"]

    # CelesTrak API configuration.
    # CelesTrak is the primary public source for NORAD Two-Line Element sets.
    # The GP (General Perturbations) endpoint provides TLEs in various formats.
    CELESTRAK_BASE_URL: str = "https://celestrak.org/NORAD/elements/gp.php"
    CELESTRAK_TIMEOUT: float = 30.0  # HTTP request timeout in seconds

    # Propagation defaults.
    # These control how many points are computed when generating a ground track.
    # 90 steps at 60s each = 90 minutes, which is roughly one ISS orbit.
    DEFAULT_PROPAGATION_STEPS: int = 90
    DEFAULT_STEP_SECONDS: float = 60.0  # Time between consecutive propagation points

    # Pass prediction configuration.
    # PASS_ELEVATION_THRESHOLD: Minimum elevation angle (degrees) above the horizon
    #   for a satellite to be considered "visible" from a ground station.
    #   5° is a common default that accounts for terrain and atmospheric effects.
    # PASS_PREDICTION_HOURS: How far ahead to predict passes (default: 24 hours).
    # PASS_TIME_STEP_SECONDS: Coarse scan resolution for detecting passes.
    #   30s is a good balance between speed and not missing short passes.
    PASS_ELEVATION_THRESHOLD: float = 5.0  # degrees above horizon
    PASS_PREDICTION_HOURS: float = 24.0
    PASS_TIME_STEP_SECONDS: float = 30.0

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Singleton settings instance used throughout the application.
# Import this directly: `from app.core.config import settings`
settings = Settings()