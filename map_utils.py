import requests
import streamlit as st
INTEREST_TAG = {
    "Nature" : [("natural","peak"),
                   ("natural","waterfall"),
                   ("natural","hill")],
    "Adventure" : [("natural","peak"),
                   ("tourism","attraction"),
                   ("leisure","natural_reserve")],
    "Food": [
        ("amenity", "cafe"),
        ("amenity", "restaurant")
    ],
    "History": [
        ("historic", "monument"),
        ("historic","archaeological_site"),
        ("tourism", "museum")
    ],
    "Photography": [
        ("tourism", "viewpoint"),
        ("natural", "peak")
    ],
    "Nightlife": [
        ("amenity", "bar"),
        ("amenity", "pub"),
        ("amenity", "nightclub")
    ],
    "Shopping": [
        ("shop", "mall"),
        ("shop", "supermarket"),
        ("shop", "clothes"),
        ("shop", "department_store")
    ],
    "Spiritual": [
        ("building", "temple"),
        ("building", "church"),
        ("building", "shrine")
    ]
}
HEADERS = {"User-Agent": "PerfectTripAI/1.0 (github.com/abhishekKappala/Perfect_Trip_AI)"}

def geocode_location(place):
    url = "https://nominatim.openstreetmap.org/search"
    parameters = {"q": place, "format": "json", "limit": 1}
    try:
        response = requests.get(url, params=parameters, headers=HEADERS, timeout=15)
        if response.status_code == 200 and response.json():
            data = response.json()[0]
            return float(data["lat"]), float(data["lon"])
    except requests.exceptions.RequestException:
        st.warning("Location service is busy right now. Please try again in a minute.")
    return None, None


def fetch_nearby_attractions(lat, lon, interests, min_results=5):
    
    radii = [5000, 10000, 20000]  # 5km, 10km, 20km

    for radius in radii:
        attractions = fetch_with_radius(lat, lon, interests, radius)
        
        if len(attractions) >= min_results:
            return attractions, radius

    return attractions, radius  # return whatever we got

def fetch_with_radius(lat, lon, interests, radius):
    query_parts = []

    # Build dynamic query based on interests
    for interest in interests:
        if interest in INTEREST_TAG:
            for key, value in INTEREST_TAG[interest]:

                query_parts.append(
                    f'node["{key}"="{value}"](around:{radius},{lat},{lon});'
                )

                query_parts.append(
                    f'way["{key}"="{value}"](around:{radius},{lat},{lon});'
                )

                query_parts.append(
                    f'relation["{key}"="{value}"](around:{radius},{lat},{lon});'
                )

    if not query_parts:
        return []

    query_body = "\n".join(query_parts)

    query = f"""
    [out:json];
    (
        {query_body}
    );
    out center;
    """

    servers = [
        "https://overpass-api.de/api/interpreter",
        "https://overpass.kumi.systems/api/interpreter",
        "https://overpass.private.coffee/api/interpreter",
    ]
    data = None
    for server in servers:
        try:
            response = requests.post(server, data={"data": query}, headers=HEADERS, timeout=40)
            if response.status_code == 200:
                data = response.json()
                break
        except (requests.exceptions.RequestException, ValueError):
            continue  # try the next server

    if data is None:
        return []
    attractions = []
    seen = set()

    for element in data.get("elements", []):
        tags = element.get("tags", {})
        name = tags.get("name")

        if not name:
            continue

        # Remove duplicates
        if name in seen:
            continue
        seen.add(name)

        # Get correct coordinates
        if element["type"] == "node":
            lat_val = element.get("lat")
            lon_val = element.get("lon")
        else:
            center = element.get("center", {})
            lat_val = center.get("lat")
            lon_val = center.get("lon")

        if lat_val is None or lon_val is None:
            continue

        attractions.append({
            "name": name,
            "lat": lat_val,
            "lon": lon_val,
            "tags": tags
        })

    return attractions
