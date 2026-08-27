import httpx
from datetime import datetime, timedelta, timezone
from dataclasses import dataclass

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

@dataclass
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

    async def fetch_by_category(self, category: str) -> list[ParsedTLE]:
        if category not in CATEGORIES:
            return []
        params = {
            'GROUP': category,
            'FORMAT': "3le"
        }
        url = f"{self.base_url}"
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()

        text = response.text.strip()

        return self.parse3le(text)


    @staticmethod
    def parse3le(text: str) -> list[ParsedTLE]:
        if not text or "No GP data found" in text:
            return []

        lines = text.strip().splitlines()
        tles: list[ParsedTLE] = []
        for i in range(0, len(lines), 3):
            # extract name and lines
            name = lines[i].strip()
            line1 = lines[i+1]
            line2 = lines[i+2]

            # extract tle values
            norad_id = int(line1[2:7])
            # epoch needs to be proccessed
            epoch = TLEFetcher._parse_epoch(line1[18:32].strip())
            incl = float(line2[8:16].strip())
            raan = float(line2[17:25].strip())
            eccentricity = float("0." + line2[26:33].strip())
            arg_perigee = float(line2[34:42].strip())
            mean_anomaly = float(line2[43:51].strip())
            mean_motion = float(line2[52:63].strip())
            intl_des = line1[9:17].strip()
            tles.append(
                ParsedTLE(
                    name=name,
                    norad_id=norad_id,
                    line1=line1,
                    line2=line2,
                    epoch=epoch,
                    inclination=incl,
                    raan=raan,
                    eccentricity=eccentricity,
                    arg_perigee=arg_perigee,
                    mean_anomaly=mean_anomaly,
                    mean_motion=mean_motion,
                    international_designator=intl_des,
                )
            )
        return tles

    @staticmethod
    def _parse_epoch(epoch_str: str) -> datetime:
        year_2digit = int(epoch_str[:2])
        day_of_year = float(epoch_str[2:])
        if year_2digit >= 57:
            year = 1900 + year_2digit
        else:
            year = 2000 + year_2digit
        epoch = datetime(year, 1, 1, tzinfo=timezone.utc) + timedelta(days=day_of_year - 1)

        return epoch