# Project Structure

```
satellite-orbit-tracker/
│
├── backend/
│   ├── app/
│   │   ├── __init__.py                # Package init
│   │   ├── main.py                    # FastAPI app entry point, middleware, router registration
│   │   │
│   │   ├── api/                       # API route handlers (controllers)
│   │   │   ├── __init__.py
│   │   │   ├── satellites.py          # GET /satellites, GET /satellites/{id}, POST /refresh
│   │   │   ├── position.py           # GET /satellites/{id}/position, GET .../ground-track
│   │   │   ├── passes.py             # GET /satellites/{id}/passes
│   │   │   └── websocket.py          # WS /ws/positions — live streaming
│   │   │
│   │   ├── core/                      # Application infrastructure
│   │   │   ├── __init__.py
│   │   │   ├── config.py             # Settings class (loads from .env)
│   │   │   └── database.py           # SQLAlchemy engine, session factory, Base class
│   │   │
│   │   ├── models/                    # Data layer
│   │   │   ├── __init__.py
│   │   │   ├── satellite.py          # SQLAlchemy ORM models (Satellite, TLE tables)
│   │   │   └── schemas.py            # Pydantic schemas (API request/response models)
│   │   │
│   │   ├── services/                  # Business logic (the interesting space stuff)
│   │   │   ├── __init__.py
│   │   │   ├── tle_fetcher.py        # Fetch + parse TLE data from CelesTrak
│   │   │   ├── propagator.py         # SGP4 wrapper + coordinate transforms
│   │   │   └── pass_predictor.py     # Pass prediction algorithm (AOS/TCA/LOS)
│   │   │
│   │   └── utils/                     # Helper functions
│   │       ├── __init__.py
│   │       ├── coordinates.py        # ECI→ECEF→Geodetic conversion functions
│   │       └── time_utils.py         # Julian date, epoch parsing, UTC helpers
│   │
│   └── tests/
│       ├── __init__.py
│       ├── conftest.py               # Shared fixtures (test DB, sample TLEs)
│       ├── test_propagator.py        # Validate SGP4 output against known positions
│       ├── test_pass_predictor.py    # Validate pass times against reference
│       ├── test_tle_fetcher.py       # Test TLE parsing
│       └── test_api.py              # Integration tests for all endpoints
│
├── frontend/
│   ├── public/
│   │   └── index.html                # HTML entry point
│   │
│   ├── src/
│   │   ├── main.js                   # App initialization, Cesium viewer setup
│   │   ├── style.css                 # Global styles + control panel layout
│   │   │
│   │   ├── components/               # UI components
│   │   │   ├── Globe.js              # Cesium viewer init, camera, layers
│   │   │   ├── SatelliteManager.js   # Add/remove satellite entities on globe
│   │   │   ├── OrbitRenderer.js      # Draw ground track polylines
│   │   │   ├── PassTable.js          # Upcoming passes table UI
│   │   │   ├── GroundStation.js      # Ground station placement + visualization
│   │   │   └── Controls.js           # Satellite picker, time controls, filters
│   │   │
│   │   ├── services/                 # Data layer
│   │   │   ├── api.js                # REST API client (fetch wrappers)
│   │   │   └── websocket.js          # WebSocket connection + reconnection logic
│   │   │
│   │   └── utils/
│   │       └── formatting.js         # Date formatting, coordinate display helpers
│   │
│   ├── package.json
│   └── vite.config.js                # Vite config with Cesium plugin
│
├── scripts/
│   ├── fetch_tle.py                  # Standalone script: fetch and print TLEs (useful for testing)
│   └── seed_db.py                    # Seed database with initial satellite catalog
│
├── data/
│   └── sample_tles.txt               # Sample TLE data for offline development/testing
│
├── docs/
│   ├── orbital-mechanics.md          # Your notes on orbital mechanics (shows domain knowledge)
│   ├── api-reference.md              # Full API documentation
│   └── deployment.md                 # How to deploy (Docker, cloud)
│
├── .github/
│   └── workflows/
│       └── ci.yml                    # GitHub Actions: lint → test → build
│
├── .env.example                      # Template for environment variables
├── .gitignore
├── docker-compose.yml                # Run full stack with one command
├── Dockerfile                        # Backend container
├── requirements.txt                  # Python dependencies (pinned versions)
├── pyproject.toml                    # Python project metadata + tool config (ruff, mypy, pytest)
└── README.md                         # Project description and how it works
```

---

## Directory Responsibilities

| Directory | What goes here |
|-----------|---------------|
| `backend/app/api/` | HTTP route handlers. Thin layer — validates input, calls services, returns response. |
| `backend/app/core/` | Infrastructure: config loading, database setup. Things that don't change often. |
| `backend/app/models/` | Database table definitions (SQLAlchemy) and API data shapes (Pydantic). |
| `backend/app/services/` | **The core logic.** Orbit propagation, TLE fetching, pass prediction. This is where the space engineering lives. |
| `backend/app/utils/` | Pure helper functions (coordinate math, time conversion). Stateless, easy to unit test. |
| `backend/tests/` | All backend tests. Mirror the `app/` structure. |
| `frontend/src/components/` | UI building blocks. Each manages one visual concern (globe, pass table, controls). |
| `frontend/src/services/` | Communication with backend (REST + WebSocket clients). |
| `scripts/` | One-off utilities for development (fetch TLEs, seed data). Not part of the running app. |
| `docs/` | Additional documentation that shows domain understanding. |

---

## File Naming Conventions

- Python: `snake_case.py`
- JavaScript: `PascalCase.js` for components, `camelCase.js` for utilities/services
- Config files: standard names (`pyproject.toml`, `vite.config.js`, `.env.example`)
- Markdown docs: `UPPER-CASE.md` for root-level, `lower-case.md` for /docs
