# 🛰️ Satellite Orbit Tracker

## What is this project?

A real-time satellite tracking and pass prediction web application. It fetches orbital data (TLE — Two-Line Elements) from public sources, propagates satellite positions using the SGP4 algorithm, predicts when satellites will be visible from a given location, and visualizes everything on an interactive 3D globe.

---

## How it works — End to end

```
┌─────────────────────────────────────────────────────────────────────┐
│                         DATA FLOW                                    │
│                                                                      │
│  1. FETCH                                                            │
│     CelesTrak / Space-Track.org ──► TLE Fetcher Service              │
│         (public APIs providing orbital data updated daily)           │
│                                          │                           │
│  2. STORE                                ▼                           │
│                                    SQLite Database                    │
│         (satellites table + TLE history table)                       │
│                                          │                           │
│  3. PROPAGATE                            ▼                           │
│                                    SGP4 Propagator                   │
│         (takes TLE + timestamp → outputs satellite position)         │
│                                          │                           │
│  4. SERVE                                ▼                           │
│                                    REST API (FastAPI)                 │
│         GET /satellites — list tracked objects                       │
│         GET /satellites/{id}/position — current lat/lon/alt          │
│         GET /satellites/{id}/passes — predict passes over location   │
│         WS  /ws/positions — live position stream                     │
│                                          │                           │
│  5. VISUALIZE                            ▼                           │
│                                    Frontend (CesiumJS)               │
│         3D globe with satellite dots, orbit lines, pass arcs         │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Key Concepts You Need to Understand

### TLE (Two-Line Element Set)
A standardized text format encoding the orbital parameters of an Earth-orbiting object. Published by NORAD and distributed via CelesTrak. Example for the ISS:

```
ISS (ZARYA)
1 25544U 98067A   24001.50000000  .00016717  00000-0  10270-3 0  9025
2 25544  51.6400 208.9163 0006703 315.8370  44.2262 15.49560532484182
```

TLEs go stale — they degrade in accuracy after 1-2 days, so they must be refreshed regularly.

### SGP4 (Simplified General Perturbations 4)
The standard algorithm that takes TLE data and a target time, then computes the satellite's position and velocity. It accounts for Earth's oblateness, atmospheric drag, and gravitational perturbations. There are well-tested Python libraries that implement this (you don't code SGP4 from scratch).

### Coordinate Systems
- **ECI (TEME frame):** What SGP4 outputs — X/Y/Z in km relative to Earth's center. Doesn't rotate with Earth.
- **ECEF (ITRS frame):** X/Y/Z that rotates with Earth. Needed as an intermediate step.
- **Geodetic:** Latitude/Longitude/Altitude — what you show on a map.

The conversion chain: `SGP4 output (TEME) → ITRS → Geodetic (lat/lon/alt)`

### Pass Prediction
A "pass" is when a satellite rises above the local horizon from an observer's viewpoint. You compute this by:
1. Propagating the satellite position every few seconds
2. Calculating its elevation angle from the observer
3. Finding when elevation crosses a threshold (typically 10°)
4. Recording AOS (Acquisition of Signal / rise), TCA (max elevation), LOS (Loss of Signal / set)

### Ground Track
The path traced on Earth's surface directly below the satellite. For LEO satellites (like ISS), this is a sinusoidal curve that shifts west with each orbit due to Earth's rotation.

---

## Architecture Overview

The app is split into a **Python backend** (data + computation) and a **JavaScript frontend** (visualization):

```
┌─────────────────────────────────┐     ┌─────────────────────────────┐
│          BACKEND (Python)        │     │     FRONTEND (JavaScript)    │
│                                  │     │                              │
│  ┌──────────────────────────┐   │     │  ┌────────────────────────┐ │
│  │ TLE Fetcher Service      │   │     │  │ CesiumJS 3D Globe      │ │
│  │ - fetches from CelesTrak │   │     │  │ - satellite entities   │ │
│  │ - scheduled refresh      │   │     │  │ - orbit polylines      │ │
│  └──────────┬───────────────┘   │     │  │ - ground station pins  │ │
│             │                    │     │  └────────────┬───────────┘ │
│             ▼                    │     │               │             │
│  ┌──────────────────────────┐   │     │  ┌────────────▼───────────┐ │
│  │ SQLite Database           │   │     │  │ API Client             │ │
│  │ - satellites table        │   │     │  │ - REST calls           │ │
│  │ - TLE history table       │   │     │  │ - WebSocket connection │ │
│  └──────────┬───────────────┘   │     │  └────────────────────────┘ │
│             │                    │     │                              │
│             ▼                    │     │  ┌────────────────────────┐ │
│  ┌──────────────────────────┐   │◄────┤  │ UI Controls            │ │
│  │ SGP4 Propagator          │   │REST │  │ - satellite picker     │ │
│  │ - position at time T     │   │ +   │  │ - ground station input │ │
│  │ - coordinate conversion  │   │ WS  │  │ - pass table           │ │
│  └──────────┬───────────────┘   │     │  │ - time controls        │ │
│             │                    │     │  └────────────────────────┘ │
│             ▼                    │     │                              │
│  ┌──────────────────────────┐   │     └─────────────────────────────┘
│  │ Pass Predictor           │   │
│  │ - AOS / TCA / LOS times  │   │
│  │ - visibility check       │   │
│  └──────────┬───────────────┘   │
│             │                    │
│             ▼                    │
│  ┌──────────────────────────┐   │
│  │ FastAPI REST + WebSocket  │   │
│  │ - /api/satellites         │   │
│  │ - /api/.../position       │   │
│  │ - /api/.../passes         │   │
│  │ - /ws/positions           │   │
│  └──────────────────────────┘   │
│                                  │
└─────────────────────────────────┘
```

---

## Features to Implement

1. **Satellite catalog browsing** — List satellites by category (ISS, Starlink, weather, GPS, etc.)
2. **Real-time position** — Show where any satellite is right now, updating every second
3. **Orbit visualization** — Draw the full ground track for 1-2 orbits ahead
4. **Ground station placement** — User sets their location (or uses GPS)
5. **Pass predictions** — Table of upcoming passes with times, elevation, direction
6. **WebSocket streaming** — Live position updates pushed to the frontend
7. **Day/night overlay** — Show Earth's terminator line for context on visibility

---

## Space Industry Skills This Demonstrates

| Skill | Why it matters |
|-------|---------------|
| Orbital mechanics (SGP4, Keplerian elements) | Core knowledge for any satellite operations role |
| TLE data handling and catalog management | Used daily in space situational awareness |
| Pass prediction algorithms | Ground station scheduling, contact planning |
| Coordinate transforms (ECI ↔ ECEF ↔ Geodetic) | Fundamental to GNC and mission analysis |
| Real-time data streaming (WebSocket) | Satellite telemetry and mission control systems |
| REST API design | Ground segment software architecture |
| 3D geospatial visualization | Situational awareness tools used at ESA/NASA |

---

## Learning Resources

- **Orbital Mechanics for Engineering Students** (Howard Curtis) — textbook covering Keplerian orbits, SGP4, perturbations
- **CelesTrak columns by T.S. Kelso** (celestrak.org) — practical articles on TLE usage, SGP4, pass prediction
- **Revisiting Spacetrack Report #3** (Vallado et al., 2006) — the definitive SGP4 reference paper
- **Astropy documentation** — coordinate transforms, time systems
- **CesiumJS tutorials** — 3D globe rendering
