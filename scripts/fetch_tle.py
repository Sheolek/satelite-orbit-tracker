import httpx
import asyncio
from pathlib import Path

CELESTRAK_BASE_URL = "https://celestrak.org"

# Available satellite categories on CelesTrak.
# Each category groups satellites by mission type or operator.
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

async def fetch_category_tle(client, category):
    url = f"{CELESTRAK_BASE_URL}/NORAD/elements/gp.php"
    params = {"GROUP": category, "FORMAT": "3le"}
    response = await client.get(url, params=params)
    response.raise_for_status()
    return response.text

def save_results_to_file(results, output_path):
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        f.write(results)
    print(f"Results saved to {path}")

async def main():
    outpu_path = "results.txt"
    async with httpx.AsyncClient(timeout=30.0) as client:
        result = await fetch_category_tle(client, category=CATEGORIES[0])
        save_results_to_file(result, outpu_path)