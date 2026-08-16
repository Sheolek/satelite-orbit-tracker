# Technologies

## Backend

| Technology | Version | Purpose |
|-----------|---------|---------|
| **Python** | 3.11+ | Primary backend language. Strong scientific computing ecosystem, dominant in space industry tooling. |
| **FastAPI** | 0.111+ | Async web framework for the REST API. Auto-generates OpenAPI docs, supports WebSockets natively, excellent performance. |
| **uvicorn** | 0.30+ | ASGI server to run FastAPI. Handles async requests and WebSocket connections. |
| **sgp4** | 2.23+ | Python implementation of the SGP4/SDP4 orbit propagation algorithm. Takes TLE data + time → satellite position/velocity in ECI frame. This is the core computation engine. |
| **astropy** | 6.1+ | Astronomical calculations library. Used for: coordinate frame transforms (TEME→ITRS→geodetic), time system conversions (UTC, TT, Julian dates), and unit handling. |
| **numpy** | 1.26+ | Numerical computing. Vector math for coordinate transforms, efficient array operations for batch propagation. |
| **scipy** | 1.14+ | Scientific computing. Used in pass prediction (root finding for horizon crossings), and potentially for orbit fitting. |
| **SQLAlchemy** | 2.0+ | ORM for database access. Async mode with aiosqlite. Manages satellite catalog and TLE history. |
| **aiosqlite** | 0.20+ | Async SQLite driver. Lets SQLAlchemy work non-blocking with FastAPI's async architecture. |
| **SQLite** | (built-in) | Lightweight file-based database. No server needed. Stores satellite metadata and TLE records. Can upgrade to PostgreSQL later. |
| **httpx** | 0.27+ | Async HTTP client for fetching TLE data from CelesTrak/Space-Track. Replaces requests with async support. |
| **APScheduler** | 3.10+ | Job scheduler. Runs TLE refresh every N hours automatically in the background. |
| **Pydantic** | 2.7+ | Data validation and serialization. Defines API request/response schemas with automatic type checking. |
| **pydantic-settings** | 2.3+ | Loads app configuration from `.env` files and environment variables with type safety. |
| **python-dateutil** | 2.9+ | Date/time parsing and manipulation utilities. |
| **websockets** | 12.0+ | WebSocket protocol support (comes with uvicorn[standard]). Powers real-time position streaming. |

## Frontend

| Technology | Version | Purpose |
|-----------|---------|---------|
| **CesiumJS** | 1.119+ | 3D globe visualization library. Space-grade accuracy, used by NASA and ESA for mission visualization. Renders Earth with terrain, satellite entities, orbit polylines, and ground station markers. |
| **Vite** | 5.3+ | Fast build tool and dev server. Hot module replacement for quick development. Bundles CesiumJS assets efficiently. |
| **Vanilla JavaScript (ES modules)** | — | No heavy framework needed. The UI is primarily the Cesium globe + some control panels. Keeps the project focused on space concepts rather than frontend framework boilerplate. |
| **CSS** | — | Styling for control panels, pass table, satellite list overlay. |

## Testing

| Technology | Purpose |
|-----------|---------|
| **pytest** | Python test framework. Unit tests for propagator accuracy, pass predictor, API endpoints. |
| **pytest-asyncio** | Async test support for testing FastAPI endpoints and async services. |
| **pytest-cov** | Code coverage reporting. |
| **httpx** (test client) | FastAPI's recommended test client for integration tests. |

## Code Quality

| Technology | Purpose |
|-----------|---------|
| **ruff** | Fast Python linter + formatter (replaces flake8, isort, black). |
| **mypy** | Static type checking. Catches type errors before runtime. |
| **ESLint** | JavaScript linting. |
| **Prettier** | JavaScript/CSS formatting. |

## DevOps

| Technology | Purpose |
|-----------|---------|
| **Docker** | Containerization for reproducible builds and easy deployment. |
| **Docker Compose** | Run backend + frontend together locally with one command. |
| **GitHub Actions** | CI/CD pipeline: lint → test → build → deploy on every push. |
| **pre-commit** | Git hooks for automatic linting/formatting before commits. |

## Data Sources

| Source | URL | Details |
|--------|-----|---------|
| **CelesTrak** | celestrak.org | Free TLE data, no authentication for basic access. Provides categorized satellite lists (stations, weather, starlink, etc.). Updated several times daily. |
| **Space-Track.org** | space-track.org | Official US Space Command TLE catalog. Requires free account registration. Has more comprehensive data and historical TLEs. |

---

## Why these choices?

- **Python backend** — Industry standard for space engineering tools. ESA, NASA, and most space companies use Python for mission analysis, orbit determination, and ground segment software.
- **FastAPI over Flask/Django** — Async-native (important for WebSocket streaming), automatic API docs, modern Python typing.
- **sgp4 + astropy** — The exact same tools used professionally. Not a toy implementation.
- **CesiumJS over Leaflet/Mapbox** — True 3D globe (not just a flat map projection). Cesium is used by AGI (now Ansys), NASA, and space operators for actual mission visualization.
- **SQLite over PostgreSQL** — Zero setup friction. The dataset is small enough. Easy to upgrade later.
- **Vanilla JS over React/Vue** — The frontend logic is minimal (render globe, call API, display table). A framework would be overkill and distract from the space engineering focus.
