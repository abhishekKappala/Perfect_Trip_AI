import streamlit as st 
import pandas as pd
import pydeck as pdk
from ai_module import generate_itinerary
from map_utils import geocode_location, fetch_nearby_attractions, fetch_hotels
from pdf_generator import generate_pdf

#Validate user input
def vaildate_input(destination, interest):
    if not (destination):
        st.error("Please enter a destination")
        st.stop()

    if not (interest):
        st.warning("Select at least one interest for better reccomendation")


#Count the number of usage for Demo Version
if "usage_count" not in st.session_state :
    st.session_state.usage_count = 0

st.set_page_config(
    page_title="Perfect Trip AI",
    layout="wide"
)

#Global Styling
st.markdown('''
            <style>
                .stApp{
                    background: linear-gradient(11deg, rgba(0, 0, 0, 1) 0%, rgba(4, 36, 105, 1) 50%, rgba(5, 3, 0, 1) 100%);
                }
                div[data-testid="stForm"] {
                    background: rgba(255, 255, 255, 0.1);
                    padding: 30px;
                    border-radius: 15px;
                    backdrop-filter: blur(10px);
                    }
                
                /* Target text_input & number_input */
                div[data-baseweb="input"] > div {
                    background-color: #1e293b;  
                    border-radius: 10px;
                }
                
                div[data-testid="stForm"] div[data-baseweb="select"] > div {
                    background-color: #1e293b;   /* Change color here */
                    border-radius: 10px;
                    color: white;
                }
                
                /* Multiselect input background */
                div[data-testid="stForm"] div[data-baseweb="select"] > div {
                    background-color: #1e293b ;
                }

                /* Multiselect selected tags */
                div[data-testid="stForm"] div[data-baseweb="tag"] {
                    background-color: #334155;
                    color: white;
                    border-radius: 8px;
                }
                

            </style>
            ''', unsafe_allow_html=True)

#Title of the page
st.markdown(
            '''<p style = "text-align : center; font-family : Times New Roman; font-size : 60px;"><b>Perfect Trip AI</b></p>''',
            unsafe_allow_html=True
        )
st.markdown('''<p style= "text-align : center; font-size: 22px; font-family : Aparajita;margin-left: 5%; margin-right : 5%;padding-bottom:20px;">
            Experience intelligent travel planning with AI—generate personalized itineraries, optimize your budget, and explore destinations through real-time insights and interactive maps.
            <b>Demo Version:</b> Experience 3 Plan Generations per Session.
            ''',unsafe_allow_html=True)

if "itinerary" not in st.session_state:
    st.session_state.itinerary = None

if "travel_details" not in st.session_state:
    st.session_state.travel_details = None

if "map_data" not in st.session_state:
    st.session_state.map_data = None

left, center, right = st.columns([1,2,1])

with center : 
    with st.form("my_form"):
        destination = st.text_input("Destination")
        duration = st.number_input("Duration of trip (in days) ",min_value=1)
        budget = st.number_input("Total Budget (in INR)",min_value=1000,step=500)
        people = st.number_input("Number of People in Group",min_value=1)
        interests = st.multiselect("Select you interests ",
                                ["Adventure",
                                "Nature",
                                "Food",
                                "History",
                                "Nightlife",
                                "Shopping",
                                "Spiritual",
                                "Photography"])

        accomodation = st.selectbox("Accomodation Type",
                                    [
                                        "Hotel",
                                        "AirBnB",
                                        "Budget Hotel",
                                        "Luxury"
                                    ])
        
        submitted = st.form_submit_button("Generate Travel Plan",use_container_width=True)

def render_map(m):
    st.divider()
    st.markdown('''<h2 style = "text-align : center;">Nearby Places & Stays</h2>''', unsafe_allow_html=True)

    attractions, hotels = m["attractions"], m["hotels"]
    if not attractions and not hotels:
        st.info("The map data service is busy right now, so only your destination is shown. Try again in a minute.")
    else:
        st.caption(f"Found {len(attractions)} attractions within {m['attraction_radius']/1000:g} km "
                   f"and {len(hotels)} stays within {m['hotel_radius']/1000:g} km")

    rows = [{"name": m["destination"], "lat": m["lat"], "lon": m["lon"], "kind": "Destination",
             "color": [0, 200, 120, 230], "size": 9}]
    rows += [{"name": a["name"], "lat": a["lat"], "lon": a["lon"], "kind": a["category"].title(),
              "color": [255, 70, 70, 200], "size": 6} for a in attractions]
    rows += [{"name": h["name"], "lat": h["lat"], "lon": h["lon"],
              "kind": f"Stay ({h['category']})" + (f" - {h['stars']} star" if h["stars"] else ""),
              "color": [60, 140, 255, 220], "size": 7} for h in hotels]
    points = pd.DataFrame(rows)

    left, right = st.columns([2, 1])
    with left:
        layer = pdk.Layer(
            "ScatterplotLayer",
            data=points,
            get_position="[lon, lat]",
            get_fill_color="color",
            get_radius="size * 12",
            radius_min_pixels=5,
            pickable=True,
        )
        view_state = pdk.ViewState(latitude=m["lat"], longitude=m["lon"], zoom=12)
        tooltip = {"html": "<b>{name}</b><br/>{kind}", "style": {"color": "white"}}
        st.pydeck_chart(pdk.Deck(layers=[layer], initial_view_state=view_state, tooltip=tooltip))
        st.caption("🟢 Destination   🔴 Attractions   🔵 Places to stay")

    with right:
        st.subheader(f"🏨 Places to stay ({m['accomodation']})")
        if hotels:
            for h in hotels[:8]:
                st.write("->  ", h["name"] + (f" ({h['stars']}★)" if h["stars"] else ""))
        else:
            st.write("No listed stays found nearby.")

        st.subheader("📍 Nearby attractions")
        for a in attractions[:10]:
            st.write("->  ", a["name"])



if submitted:
    #validate input before proceeding further
    vaildate_input(destination, interests)

    #Session stops when the demo usage limit is reached
    if st.session_state.usage_count >= 3:
        st.warning("Demo Usage Limit Reached ! (3 uses)")
        st.stop()

    st.markdown("\n")
    #Geocoding locations
    lat, lon = geocode_location(destination)

      #Error handling
    if (lat is None):
        st.error("Cannot find the location! Please enter a valid location. ")
        st.stop()
    with st.spinner("Finding nearby places and stays ..."):
        attractions, used_radius = fetch_nearby_attractions(lat, lon, interests)
        hotels, hotel_radius = fetch_hotels(lat, lon, accomodation)

    #adding attractions and hotels to travel details
    travel_details = {
        "destination" : destination,
        "duration" : duration,
        "budget" : budget,
        "people" : people,
        "interests" : interests,
        "accomodation" : accomodation,

        #Add additional details to make output better
        "budget_per_day" : int(budget/duration),
        "budget_per_person" : int(budget/people),
        "nearby_attractions" : attractions,
        "nearby_hotels" : hotels
    }

    st.session_state.travel_details = travel_details

    # saved in session_state so the map stays visible after reruns (e.g. PDF download click)
    st.session_state.map_data = {
        "destination": destination, "lat": lat, "lon": lon,
        "attractions": attractions, "attraction_radius": used_radius,
        "hotels": hotels, "hotel_radius": hotel_radius,
        "accomodation": accomodation,
    }
    st.session_state.itinerary = None      # clear the old plan
    render_map(st.session_state.map_data)

    # Displaying itinerary
    with st.spinner("Generating your travel plan ..."):
        itinerary = generate_itinerary(travel_details)
        if itinerary:
            st.session_state.itinerary = itinerary
            st.session_state.usage_count += 1



# on reruns (e.g. clicking Download) keep showing the saved map
if st.session_state.map_data and not submitted:
    render_map(st.session_state.map_data)

if st.session_state.itinerary : 
    st.markdown(
            '''<h2 style = "text-align : center;">Your Day wise itinerary</h2>''',
            unsafe_allow_html=True
        )

    left, center, right = st.columns([1,3,1])
    with center :
        stay = st.session_state.itinerary.get("recommended_stay") or {}
        if stay.get("name"):
            st.success(f"🏨 Recommended stay: **{stay['name']}** ({stay.get('area', '')}) - "
                       f"about INR {stay.get('cost_per_night', 0)} per night. {stay.get('reason', '')}")
        for day in st.session_state.itinerary["days"]:
            with st.expander(f" Day {day['day']}"):
            #Convert all to markdown html
              for activity in day["activities"]:
                  st.markdown(
                  f'''<h3 style = "text-align:center;">{activity["time"]}</h3> ''',
                  unsafe_allow_html=True
                  )
                  st.markdown(f'''<h4 style = "text-align : center;">{activity["activity"]}</h4>''', unsafe_allow_html=True)
                  st.markdown(f'''<div>
                        <ul>
                            <li>Estimated Cost for the activity : INR {activity["estimated_cost"]}</li>
                            <li>Food Recommendation : {activity["food_recommendation"]}</li>
                            <li>Transport Suggestion : {activity["transport_suggestion"]}</li>
                        </ul>
                    </div>
                    ''', 
                  unsafe_allow_html=True)

                  st.markdown("---")
              st.markdown(f'''<h4 style = "text-align : center;">Daily Estimated total = INR {day["daily_estimated_total"]}</h4>''',unsafe_allow_html=True)
        
    with center:
      st.divider()
      #Display budget Card
      st.markdown('''<h2 style = "text-align : center;">Budget Breakdown</h2>''',unsafe_allow_html=True)
      budget = st.session_state.itinerary['budget_breakdown']
      total_cost = budget['accommodation_total']+budget['food_total']+budget['transport_total']+budget['activities_total']+budget['miscellaneous']

      st.markdown(f'''<div>
                        <ul>
                            <li>Accommodation Expenditure : INR {budget['accommodation_total']}</li>
                            <li>Expense on Food  : INR {budget['food_total']}</li>
                            <li>Expense on Transport  : INR {budget['transport_total']}</li>
                            <li>Expense on Activities  : INR {budget['activities_total']}</li>
                            <li>Miscellaneous Expenditure  : INR {budget['miscellaneous']}</li>
                            <li><b>Total Expense : INR {total_cost}</b></li>
                        </ul>
                    </div>
                    ''', 
                  unsafe_allow_html=True)

      pdf_bytes = generate_pdf(st.session_state.itinerary)

      st.markdown("\n")
      if total_cost < st.session_state.travel_details['budget']:
          st.markdown('''<h4 style = "text-align : center;"> All such fun, that too within budget. Enjoy Your Trip </h4>''',unsafe_allow_html=True)
      elif total_cost == st.session_state.travel_details['budget']:
          st.markdown('''<h4 style = "text-align : center;"> Tight Budget but definitely worth to try. Enjoy Your Trip </h4>''',unsafe_allow_html=True)
      else:
          st.markdown('''<h4 style = "text-align : center;"> A little overbudget, but definitely worth it. Enjoy Your Trip  </h4>''',unsafe_allow_html=True)
      

      #Downloading travel plan as pdf
      st.divider()
      st.markdown("### Download Your Travel Plan")
      st.download_button(
          label="📄 Download Travel Plan as PDF",
          data=pdf_bytes,
          file_name=f"{st.session_state.travel_details['destination']}_travel_plan.pdf",
          mime="application/pdf"
      )
