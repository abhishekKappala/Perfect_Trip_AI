import requests
import streamlit as st

# Nominatim's usage policy requires an identifying User-Agent
HEADERS = {"User-Agent": "PerfectTripAI/1.0 (github.com/abhishekKappala/Perfect_Trip_AI)"}

# Public Overpass servers, tried in order (the main one often refuses requests)
OVERPASS_SERVERS = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
    "https://overpass.private.coffee/api/interpreter",
]

# User interest -> OpenStreetMap tags (key, value)
INTEREST_TAG = {
    "Nature": [("leisure", "park"), ("leisure", "nature_reserve"),
               ("natural", "waterfall"), ("natural", "peak")],
    "Adventure": [("tourism", "attraction"), ("leisure", "nature_reserve"),
                  ("natural", "peak")],
    "Food": [("amenity", "restaurant"), ("amenity", "cafe")],
    "History": [("historic", "monument"), ("historic", "archaeological_site"),
                ("historic", "fort"), ("tourism", "museum")],
    "Photography": [("tourism", "viewpoint"), ("tourism", "attraction")],
    "Nightlife": [("amenity", "bar"), ("amenity", "pub"), ("amenity", "nightclub")],
    "Shopping": [("shop", "mall"), ("shop", "department_store"), ("amenity", "marketplace")],
    "Spiritual": [("amenity", "place_of_worship")],
}

# Accommodation type -> OpenStreetMap tags
ACCOMMODATION_TAG = {
    "Hotel": [("tourism", "hotel")],
    "Luxury": [("tourism", "hotel")],
    "Budget Hotel": [("tourism", "hostel"), ("tourism", "guest_house"), ("tourism", "motel")],
    "AirBnB": [("tourism", "apartment"), ("tourism", "guest_house")],  # Airbnb listings aren't in OSM
}


# ---------- Geocoding (place name -> coordinates) ----------

@st.cache_data(ttl=86400, show_spinner=False)
def _geocode(place):
    response = requests.get(
        "https://nominatim.openstreetmap.org/search",
        params={"q": place, "format": "json", "limit": 1},
        headers=HEADERS, timeout=15,
    )
    response.raise_for_status()          # errors are raised, so they are never cached
    results = response.json()
    if not results:
        return None
    return float(results[0]["lat"]), float(results[0]["lon"])


def geocode_location(place):
    try:
        result = _geocode(place.strip())
    except (requests.exceptions.RequestException, ValueError):
        st.warning("Location service is busy right now. Please try again in a minute.")
        return None, None
    return result if result else (None, None)


# ---------- Overpass (find places near a point) ----------

@st.cache_data(ttl=3600, show_spinner=False)
def _run_overpass(query):
    for server in OVERPASS_SERVERS:
        try:
            response = requests.post(server, data={"data": query}, headers=HEADERS, timeout=40)
            if response.status_code == 200:
                return response.json().get("elements", [])
        except (requests.exceptions.RequestException, ValueError):
            continue                     # try the next server
    raise ConnectionError("All Overpass servers failed")   # raised -> not cached


def _search_places(lat, lon, tag_pairs, radius, limit=80):
    lat, lon = round(lat, 4), round(lon, 4)    # stable values -> better caching
    parts = "\n".join(f'nwr["{k}"="{v}"](around:{radius},{lat},{lon});' for k, v in tag_pairs)
    query = f"[out:json][timeout:25];\n(\n{parts}\n);\nout center {limit};"

    try:
        elements = _run_overpass(query)
    except ConnectionError:
        return []

    places, seen = [], set()
    for element in elements:
        tags = element.get("tags", {})
        name = tags.get("name:en") or tags.get("name")
        if not name or name in seen:
            continue
        seen.add(name)

        # nodes have lat/lon directly; ways/relations have a "center"
        point = element if element.get("type") == "node" else element.get("center", {})
        if point.get("lat") is None or point.get("lon") is None:
            continue

        category = next((tags[k] for k in ("tourism", "historic", "amenity", "leisure", "natural", "shop")
                         if k in tags), "place")
        places.append({
            "name": name,
            "lat": point["lat"],
            "lon": point["lon"],
            "category": category.replace("_", " "),
            "stars": tags.get("stars", ""),
        })
    return places


def fetch_nearby_attractions(lat, lon, interests, min_results=5):
    """Search 5 km, then 10 km, then 20 km until enough places are found."""
    tag_pairs = []
    for interest in interests:
        tag_pairs += INTEREST_TAG.get(interest, [])
    if not tag_pairs:
        tag_pairs = [("tourism", "attraction")]        # default when no interest chosen

    attractions, radius = [], 5000
    for radius in [5000, 10000, 20000]:
        attractions = _search_places(lat, lon, tag_pairs, radius)
        if len(attractions) >= min_results:
            break
    return attractions, radius


def fetch_hotels(lat, lon, accommodation, min_results=3):
    """Find places to stay matching the chosen accommodation type."""
    tag_pairs = ACCOMMODATION_TAG.get(accommodation, [("tourism", "hotel")])

    hotels, radius = [], 3000
    for radius in [3000, 7000, 15000]:
        hotels = _search_places(lat, lon, tag_pairs, radius, limit=60)
        if len(hotels) >= min_results:
            break

    if accommodation == "Luxury":                      # higher star ratings first
        def stars(h):
            try:
                return float(str(h["stars"]).rstrip("S"))
            except ValueError:
                return 0
        hotels.sort(key=stars, reverse=True)
    return hotels[:15], radius
