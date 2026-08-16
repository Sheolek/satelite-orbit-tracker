import requests
from datetime import datetime

CATEGORIES = [
    "stations",   # Space stations (ISS, Tiangong, etc.)
    "visual",     # Visually brightest satellites (for naked-eye observation)
    "weather",    # Weather/meteorological satellites
    "noaa",       # NOAA-operated satellites
    "gps-ops",    # GPS operational constellation
    "galileo",    # EU Galileo navigation constellation
    "starlink",   # SpaceX Starlink internet satellites (~5000+)
    "active",     # All active satellites (~8000+)
    "analyst",    # Analyst-tracked objects
]

class ParsedTLE:
    """Parsed TLE data with metadata.

    Contains both the raw TLE lines (needed for SGP4 propagation) and
    extracted orbital elements (useful for database queries and display).

    Attributes:
        name: Satellite name from line 0 of 3LE format.
        norad_id: NORAD catalog number (unique identifier for the space object).
        line1: Raw TLE line 1 (69 characters, starts with "1 ").
        line2: Raw TLE line 2 (69 characters, starts with "2 ").
        epoch: UTC datetime when these orbital elements are most accurate.
        inclination: Orbital plane tilt relative to equator (degrees, 0-180).
                    0° = equatorial, 90° = polar, >90° = retrograde.
        raan: Right Ascension of Ascending Node (degrees, 0-360).
              Defines where the orbit crosses the equator going northward.
        eccentricity: Orbit shape (0 = circular, approaching 1 = very elliptical).
        arg_perigee: Argument of perigee (degrees, 0-360).
                    Defines orientation of the ellipse within the orbital plane.
        mean_anomaly: Position along orbit at epoch (degrees, 0-360).
        mean_motion: Number of complete orbits per day (revolutions/day).
                    ISS ≈ 15.5 (one orbit every ~92 minutes).
        international_designator: Launch identifier (e.g., "98067A" for ISS).
    """
    name: str
    norad_id: int
    line1: str
    line2: str
    epoch: datetime
    inclination: float
    raan: float
    eccentricity: float
    arg_perigee: float
    mean_anomaly: float
    mean_motion: float
    international_designator: str

class TLEFetcher:
    base_url = "https://celestrak.org/NORAD/elements/gp.php"

    # TODO add default values
    def __init__(self, base_url: str | None = None, timeout: float | None = None) -> None:
        self.base_url = base_url
        self.timeout = timeout

    def fetch_by_category(self, category: str) -> list[ParsedTLE]:
        if category not in CATEGORIES:
            return []
        params = {
            'GROUP': category,
            'FORMAT': "3le"
        }
        response = requests.get(self.getEndpoint, params=params)
        print(response)
        return self.parseResponse(response)

    def parseResponse(self, response: requests.Response):
        if response.status_code != 200:
            return [response.status_code, []]
        print(response.text)
        tleData = self.parseTleBody(response.text)
        return [response.status_code, tleData]

    def parseTleBody(self, tleBody):
        lines = tleBody.strip().splitlines()
        tleProcessedData = []
        for i in range(0, len(lines), 3):
            name = lines[i].strip()
            line1 = lines[i+1]
            line2 = lines[i+2]
            id = line1[2:7]
            epoch = line1[18:32]
            tleProcessedData.append([name, line1, line2, id, epoch])
        return tleProcessedData