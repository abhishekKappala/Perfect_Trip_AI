import streamlit as st 
import pandas as pd
import pydeck as pdk
from ai_module import generate_itinerary
from map_utils import geocode_location, fetch_nearby_attractions
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
    page_title="Perfect_Trip_AI",
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
            '''<p style = "text-align : center; font-family : Times New Roman; font-size : 60px;"><b>Yatra Saarthi</b></p>''',
            unsafe_allow_html=True
        )
st.markdown('''<p style= "text-align : center; font-size: 22px; font-family : Aparajita;margin-left: 5%; margin-right : 5%;padding-bottom:20px;">
            Plan smarter journeys with AI — generate personalized, 
            budget-friendly student itineraries powered by 
            real-time location data and interactive maps.
            <br>This is currently a demo version - it is limited to 3 uses per session.</p><br>
            ''',unsafe_allow_html=True)

if "itinerary" not in st.session_state:
    st.session_state.itinerary = None

if "travel_details" not in st.session_state:
    st.session_state.travel_details = None

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
    with st.spinner("Finding Nearby Locations") :
        attractions, used_radius = fetch_nearby_attractions(lat, lon,interests)
    st.success(f"Found {len(attractions)} locations within {used_radius/1000} km")

    #adding attractions to travel details
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
        "nearby_attractions" : attractions
    }

    st.session_state.travel_details = travel_details

    st.divider()
    st.markdown(
            '''<h2 style = "text-align : center;">Nearby Locations</h2>''',
            unsafe_allow_html=True
        )
    st.markdown("\n")
    left, right = st.columns([2, 1])
    with left:
        locations = pd.DataFrame(attractions)
        if not locations.empty:

            layer = pdk.Layer(
                "ScatterplotLayer",
                data=locations,
                get_position='[lon, lat]',
                get_color='[255, 0, 0, 160]',
                get_radius=120,
                pickable=True,
            )

            view_state = pdk.ViewState(
                latitude=locations["lat"].mean(),
                longitude=locations["lon"].mean(),
                zoom=12,
            )

            tooltip = {
                "html": "<b>{name}</b>",
                "style": {"color": "white"}
            }

            deck = pdk.Deck(
                layers=[layer],
                initial_view_state=view_state,
                tooltip=tooltip
            )

            st.pydeck_chart(deck)

    with right:
        st.markdown("\n")
        st.subheader("List of nearby attractions")
        for place in attractions[:10]:
            st.write("->   ",place["name"])

    # Displaying itinerary
    with st.spinner("Generating your travel plan ..."):
        itinerary = generate_itinerary(travel_details)
        if itinerary:
            st.session_state.itinerary = itinerary
            st.session_state.usage_count += 1

if st.session_state.itinerary : 
    st.markdown(
            '''<h2 style = "text-align : center;">Your Day wise itinerary</h2>''',
            unsafe_allow_html=True
        )

    left, center, right = st.columns([1,3,1])
    with center : 
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