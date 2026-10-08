from groq import Groq
import streamlit as st
import json


def _num(x):
    try:
        return int(float(str(x).replace(",", "").replace("INR", "").strip()))
    except (ValueError, TypeError):
        return 0

def normalize_itinerary(data, destination=""):
    """Force the model's JSON into the shape app.py / pdf_generator.py expect."""
    days = data.get("days") or data.get("itinerary") or []
    if isinstance(days, dict):
        days = list(days.values())

    clean_days = []
    for i, day in enumerate(days, start=1):
        if not isinstance(day, dict):
            continue
        acts = day.get("activities", [])
        if isinstance(acts, dict):
            acts = [{"time": k, **v} if isinstance(v, dict) else {"time": k, "activity": str(v)}
                    for k, v in acts.items()]
        clean_acts = []
        for a in acts:
            if isinstance(a, str):
                a = {"activity": a}
            if not isinstance(a, dict):
                continue
            clean_acts.append({
                "time": a.get("time", ""),
                "activity": a.get("activity", ""),
                "location": a.get("location", ""),
                "estimated_cost": _num(a.get("estimated_cost", 0)),
                "food_recommendation": a.get("food_recommendation", "-"),
                "transport_suggestion": a.get("transport_suggestion", "-"),
            })
        clean_days.append({
            "day": day.get("day", i),
            "activities": clean_acts,
            "daily_estimated_total": _num(day.get("daily_estimated_total",
                                          sum(a["estimated_cost"] for a in clean_acts))),
        })
    data["days"] = clean_days

    b = data.get("budget_breakdown") or {}
    data["budget_breakdown"] = {k: _num(b.get(k, 0)) for k in
        ["accommodation_total", "food_total", "transport_total", "activities_total", "miscellaneous"]}

    tips = data.get("travel_tips", [])
    data["travel_tips"] = [tips] if isinstance(tips, str) else list(tips)

    summary = data.get("trip_summary") or {}
    summary.setdefault("destination", destination)
    data["trip_summary"] = summary
    return data

def generate_itinerary(travel_details):
    try:
        api_key = st.secrets["GROQ_API_KEY"]
    except st.errors.StreamlitSecretNotFoundError:
        st.warning("⚠️ API key not found.")
        st.info("Please add your own API key in `.streamlit/secrets.toml` to use the AI itinerary generator.")
        st.stop()
    except KeyError:
        st.warning("⚠️ GROQ_API_KEY not found in secrets.")
        st.info("To generate your itinerary, please add `GROQ_API_KEY` in `.streamlit/secrets.toml`.")
        st.stop()

    client = Groq(api_key=api_key)

    prompt = f"""
    Create a {travel_details["duration"]} day itinerary for a group of {travel_details["people"]} people.
    Plan as a professional travel planner specializing in budget-friendly trips. Plan according to the time of the day - morning, afternoon, and evening.
    For each time (morning, afternoon or evening) add the estimated cost for the activity.  
    Moreover add a few tips at the end to make the trip more enjoyable. 

    Destination: {travel_details["destination"]}
    Total budget: INR {travel_details["budget"]}
    Budget per day: INR {travel_details["budget_per_day"]}
    Budget per person: INR {travel_details["budget_per_person"]}
    Interested activities: {travel_details["interests"]}
    Accommodation: {travel_details["accomodation"]}

    IMPORTANT:
    - Return ONLY valid JSON
    - No markdown
    - No explanation text
    - Do NOT use backticks
    - Do NOT add text before or after JSON

    JSON Format -
    Return JSON strictly in this format:

    {{
    "trip_summary": {{
        "destination": "string",
        "duration_days": number,
        "total_budget": number,
        "budget_per_day": number,
        "budget_per_person": number
    }},
    "days": [
        {{
        "day": 1,
        "activities": [
            {{
            "time": "Morning / Afternoon / Evening / Night",
            "activity": "Detailed description of activity",
            "location": "Place name",
            "estimated_cost": number,
            "food_recommendation": "Food or restaurant suggestion",
            "transport_suggestion": "How to reach / travel suggestion"
            }}
        ],
        "daily_estimated_total": number
        }}
    ],
    "budget_breakdown": {{
        "accommodation_total": number,
        "food_total": number,
        "transport_total": number,
        "activities_total": number,
        "miscellaneous": number
    }},
    "travel_tips": [
        "Tip 1",
        "Tip 2"
    ]
    }}
    """

    MODEL = st.secrets.get("GROQ_MODEL", "openai/gpt-oss-120b")

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "You are a travel planning assistant. Reply only with JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.6,
            response_format={"type": "json_object"},
        )

        content = response.choices[0].message.content
        return normalize_itinerary(json.loads(content), travel_details["destination"])
    
    except json.JSONDecodeError:
        st.error("AI JSON Decoding Failed !. Please try again")
        return None
    
    except Exception as e:
        st.error(f"Groq API error : {str(e)}")
        return None
