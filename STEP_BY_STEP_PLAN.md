# Step-by-Step Implementation Plan

Total estimated time: **5-6 weeks** (working evenings/weekends, ~10-15 hrs/week)

---

## Phase 1: Project Setup + TLE Fetching (Week 1)

### Step 1.1 — Initialize the project
- Create the directory structure (see PROJECT_STRUCTURE.md)
- Set up Python virtual environment: `python -m venv venv`
- Install initial dependencies: `pip install fastapi uvicorn sgp4 httpx`
- Create `pyproject.toml` with project metadata and tool configs (ruff, mypy, pytest)
- Create `.gitignore`, `.env.example`
- Initialize git repo, make first commit

### Step 1.2 — Implement TLE fetcher service
**File:** `backend/app/services/tle_fetcher.py`

What to implement:
1. Async function that sends GET request to CelesTrak: `https://celestrak.org/NORAD/elements/gp.php?GROUP=stations&FORMAT=tle`
2. Parse the 3-line response format (satellite name + line1 + line2, repeating)
3. Extract NORAD ID from line 2 (columns 3-7)
4. Extract epoch from line 1 (columns 19-32) and convert to datetime
5. Return list of dicts: `{name, line1, line2, norad_id, epoch}`

Test it standalone:
```python
# scripts/fetch_tle.py
import asyncio
from app.services.tle_fetcher import TLEFetcher

async def main():
    fetcher = TLEFetcher()
    tles = await fetcher.fetch_category("stations")
    for tle in tles[:5]:
        print(f"{tle['name']} (NORAD {tle['norad_id']})")
    await fetcher.close()

asyncio.run(main())
```

### Step 1.3 — Database setup
**Files:** `backend/app/core/database.py`, `backend/app/models/satellite.py`

1. Define `Satellite` table: id, norad_id, name, category, international_designator, timestamps
2. Define `TLE` table: id, satellite_id (FK), line1, line2, epoch, orbital params (inclination, eccentricity, mean_motion, etc.)
3. Create async engine and session factory
4. Write a `seed_db.py` script that fetches TLEs and populates the database

### Step 1.4 — Basic FastAPI app with health check
**File:** `backend/app/main.py`

1. Create FastAPI instance with title/description
2. Add CORS middleware
3. Add `/health` endpoint
4. Register placeholder routers
5. Verify it runs: `uvicorn backend.app.main:app --reload`

**Milestone:** You can fetch TLE data, store it, and the API server starts. ✓

---

## Phase 2: SGP4 Propagation + Position API (Week 2)

### Step 2.1 — Implement the propagator service
**File:** `backend/app/services/propagator.py`

Core implementation:
```python
from sgp4.api import Satrec, WGS72
from astropy.time import Time
from astropy.coordinates import TEME, ITRS, CartesianRepresentation
from astropy import units as u

# 1. Parse TLE into Satrec object
satellite = Satrec.twoline2rv(line1, line2, WGS72)

# 2. Propagate to a specific time (Julian date)
jd, fr = jday(year, month, day, hour, minute, second)
error_code, position, velocity = satellite.sgp4(jd, fr)
# position = (x, y, z) in km (TEME frame)
# velocity = (vx, vy, vz) in km/s

# 3. Convert TEME → ITRS → Geodetic
t = Time(datetime_utc, scale='utc')
teme = TEME(CartesianRepresentation(x*u.km, y*u.km, z*u.km), obstime=t)
itrs = teme.transform_to(ITRS(obstime=t))
location = itrs.earth_location
lat = location.lat.deg
lon = location.lon.deg
alt = location.height.to(u.km).value
```

### Step 2.2 — Write propagator tests
**File:** `backend/tests/test_propagator.py`

- Use a known ISS TLE + known timestamp → compare output to a reference position
- CelesTrak provides verification data you can use
- Test that coordinate conversion produces sensible values (lat in -90..90, lon in -180..180)
- Test error handling for invalid/expired TLEs

### Step 2.3 — Position API endpoint
**File:** `backend/app/api/position.py`

Endpoints:
- `GET /api/satellites/{norad_id}/position` — returns current lat/lon/alt/velocity
- `GET /api/satellites/{norad_id}/position?timestamp=2024-01-15T12:00:00Z` — position at specific time
- `GET /api/satellites/{norad_id}/ground-track?duration_minutes=90&step_seconds=30` — full orbit path

### Step 2.4 — Satellite listing endpoint
**File:** `backend/app/api/satellites.py`

- `GET /api/satellites` — list all with filtering by category, search by name
- `GET /api/satellites/{norad_id}` — single satellite details + latest TLE epoch

**Milestone:** API returns real satellite positions. You can verify against heavens-above.com. ✓

---

## Phase 3: Pass Prediction (Week 3)

### Step 3.1 — Implement pass predictor
**File:** `backend/app/services/pass_predictor.py`

Algorithm (brute-force, then optimize):
1. Define observer location as geodetic coordinates
2. Loop through time in small steps (e.g., every 30 seconds over next N days)
3. At each step:
   - Propagate satellite position (lat/lon/alt)
   - Calculate elevation angle from observer to satellite:
     ```
     elevation = arctan2(alt_above_horizon, slant_distance_horizontal)
     ```
   - Actually: use the topocentric coordinate transform (observer-centric frame)
4. Detect when elevation crosses threshold (10°) — that's AOS (rising) and LOS (setting)
5. Find maximum elevation between AOS and LOS — that's TCA
6. Record pass: {aos_time, aos_azimuth, tca_time, tca_elevation, tca_azimuth, los_time, los_azimuth, duration}

Better approach using astropy:
```python
from astropy.coordinates import EarthLocation, AltAz

observer = EarthLocation(lat=lat*u.deg, lon=lon*u.deg, height=alt*u.m)
# For each propagated satellite position, transform to observer's AltAz frame
# altitude > 0 means above horizon, altitude > 10 means visible pass
```

### Step 3.2 — Optimize pass prediction
- Use coarse step (60s) to find approximate pass windows
- Then use fine step (1s) near AOS/LOS for precise timing
- Use scipy.optimize.brentq for root-finding on elevation = threshold
- Cache results (passes don't change often for a given TLE)

### Step 3.3 — Pass prediction endpoint
**File:** `backend/app/api/passes.py`

- `GET /api/satellites/{norad_id}/passes?lat=52.23&lon=21.01&alt=100&days=7&min_elevation=10`
- Returns list of passes with all AOS/TCA/LOS data
- Include `is_visible` flag (satellite in sunlight + observer in darkness)

### Step 3.4 — Write pass predictor tests
- Compare against known pass data from heavens-above.com or Stellarium
- ISS passes are well-documented and easy to verify
- Test edge cases: polar passes, very low elevation passes, midnight sun scenarios

**Milestone:** You can predict ISS passes over your location and verify against heavens-above.com. ✓

---

## Phase 4: Frontend + Real-time Streaming (Week 4)

### Step 4.1 — Set up Cesium frontend
1. `npm create vite@latest frontend` (vanilla JS template)
2. Install CesiumJS: `npm install cesium`
3. Configure vite-plugin-cesium in `vite.config.js`
4. Create basic globe in `Globe.js`:
   ```javascript
   import { Viewer, Ion } from 'cesium';
   // Note: CesiumJS requires an ion access token for terrain/imagery
   // Get free token at cesium.com/ion
   const viewer = new Viewer('cesiumContainer');
   ```

### Step 4.2 — Display satellites on globe
- Fetch satellite positions from API
- Add Cesium entities (points/billboards) at each lat/lon/alt
- Color-code by category
- Add click handler to show satellite info popup

### Step 4.3 — Draw orbit ground tracks
- Fetch ground track from API (array of lat/lon points)
- Draw as Cesium Polyline (color fades from past→future)
- Update periodically

### Step 4.4 — Implement WebSocket streaming
**Backend:** `backend/app/api/websocket.py`
- Client sends subscription message: `{"subscribe": [25544, 48274]}`
- Server propagates positions every 1 second and pushes to all connected clients
- Handle disconnections gracefully

**Frontend:** `frontend/src/services/websocket.js`
- Connect to `ws://localhost:8000/ws/positions`
- On each message, update satellite entity positions on the globe
- Auto-reconnect on connection loss

### Step 4.5 — Ground station + pass UI
- Click on map (or enter coordinates) to place ground station
- Call pass prediction API for selected satellite + ground station
- Display upcoming passes in a table (time, max elevation, direction, duration)
- Optionally draw pass arc on the globe

### Step 4.6 — UI controls
- Satellite category filter dropdown
- Search box (filter by name/NORAD ID)
- Time controls: pause, speed up (2x, 10x, 100x), set custom time
- Day/night terminator overlay (Cesium has this built-in)

**Milestone:** Full working app — globe shows satellites moving, you can predict passes. ✓

---

## Phase 5: Testing, Polish, DevOps (Week 5-6)

### Step 5.1 — Comprehensive testing
- Unit tests for all services (propagator, pass predictor, TLE parser)
- Integration tests for API endpoints (use FastAPI TestClient)
- Test WebSocket streaming
- Aim for 80%+ code coverage on backend

### Step 5.2 — Scheduled TLE refresh
- Use APScheduler to run TLE fetch every 6 hours
- Add `GET /api/admin/tle-status` endpoint showing TLE freshness
- Log warnings when TLEs are older than 2 days

### Step 5.3 — Dockerize
- `Dockerfile` for backend (multi-stage: install deps → copy app → run uvicorn)
- `docker-compose.yml` with backend + frontend services
- Volume mount for SQLite database persistence

### Step 5.4 — CI/CD pipeline
**File:** `.github/workflows/ci.yml`
- Trigger: push to main, pull requests
- Steps: checkout → setup Python → install deps → lint (ruff) → type check (mypy) → test (pytest) → build frontend

### Step 5.5 — Documentation
- Write `docs/orbital-mechanics.md` explaining the concepts in your own words (shows interviewers you understand it, not just copy-pasted)
- Complete API reference (`docs/api-reference.md`)
- Add deployment guide

### Step 5.6 — Deploy
- Deploy backend to Fly.io or Railway (both have free tiers)
- Deploy frontend to Vercel or Netlify (free)
- Or: deploy full stack via Docker on a cheap VPS (Hetzner, €4/month)
- Add a live demo link to your README

**Milestone:** Project is deployed, tested, documented, and portfolio-ready. ✓

---

## Bonus Extensions (if you want to go further)

| Extension | Why |
|-----------|-----|
| Add collision proximity alerts (conjunction screening) | Shows space situational awareness skills |
| Implement CCSDS telemetry packet format for the position data | Bridges to ground segment protocols |
| Add orbit determination from ground observations | Advanced astrodynamics |
| Multi-user ground station network (like SatNOGS) | Shows systems thinking |
| Predict Iridium flares or ISS visibility brightness | Adds photometry dimension |

---

## Tips for Working Through This

1. **Don't get stuck on math** — the `sgp4` and `astropy` libraries handle the hard math. Focus on understanding what the inputs/outputs mean, not deriving the equations.
2. **Validate constantly** — compare your outputs to heavens-above.com, n2yo.com, or Stellarium. If your ISS position is off by more than ~1° from these sites, something is wrong.
3. **Commit often** — make your git history tell a story. Reviewers (and recruiters) look at commit history.
4. **Write the orbital-mechanics.md as you learn** — it's both a study aid and a portfolio piece.
5. **TLE freshness matters** — if your predictions are wrong, the first thing to check is whether your TLE is stale.
