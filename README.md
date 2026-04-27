# 🌍 Perfect_Trip_AI – Smart Student Travel Planner

**Perfect_Trip_AI** is an intelligent travel planning platform tailored for students who want efficient, low-cost, and personalized trips.  
It leverages modern AI models, live geographic data, and clean visualizations to build structured travel itineraries in seconds.



---

## 🚀 Core Capabilities

- 🤖 AI-driven itinerary creation powered by Groq LLM
- 📍 Dynamic nearby place discovery using OpenStreetMap (Overpass API)
- 🗺️ Interactive geospatial visualization via PyDeck
- 💰 Smart budget estimation with cost breakdown
- 📄 Exportable travel plans in PDF format
- 🔐 Secure API key handling using Streamlit Secrets
- ⏳ Session-based usage restriction for demo control

---

## ⚙️ System Workflow

### 🔹 User Inputs
- Destination location  
- Trip duration  
- Budget constraints  
- Personal interests  
- Preferred accommodation  

### 🔹 Backend Processing
- Convert destination into coordinates (Geocoding)
- Retrieve nearby attractions via OpenStreetMap APIs
- Generate structured prompt for Groq LLM
- Receive itinerary in JSON format
- Format and present the itinerary
- Generate downloadable PDF report

---

## 🧰 Technology Stack

| Tool/Framework | Role |
|----------------|------|
| Streamlit | Frontend + app hosting |
| Groq API (LLM) | AI itinerary engine |
| OpenStreetMap + Overpass API | Location intelligence |
| PyDeck | Map visualization |
| ReportLab | PDF generation |
| Pandas | Data processing |

---

## 📁 Directory Layout



```
Perfect_Trip_AI/
│
├── app.py # Entry point for Streamlit UI
├── ai_module.py # Handles LLM interactions
├── map_utils.py # Location + API utilities
├── pdf_generator.py # PDF creation logic
├── requirements.txt # Python dependencies
└── .streamlit/
└── config.toml # UI configuration (optional)```


---

## 🖥️ Local Installation Guide

### 1. Clone Repository

```bash

cd Perfect_Trip_AI
```

### 2️) Create and Activate Virtual Environment

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Mac/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3️) Install Dependencies

```bash
pip install -r requirements.txt
```

### 4️) Configure API Key

Create a folder named:

```
.streamlit
```

Inside it, create:

```
secrets.toml
```

Add your Groq API key:

```toml
GROQ_API_KEY = "your_actual_groq_api_key"
```

### 5️) Run the Application

```bash
streamlit run app.py
```

The app will open in your browser at:

```
http://localhost:8501
```

---

## ☁️ Deployment (Streamlit Cloud)

1. Push your project to GitHub
2. Go to https://share.streamlit.io
3. Connect your repository
4. Select:
   - Branch: `main`
   - Main file: `app.py`
5. Add your `GROQ_API_KEY` in **App Settings → Secrets**
6. Deploy

Streamlit Cloud will automatically rebuild the app whenever new commits are pushed to the selected branch.

---

##  Demo Usage Limitation

The deployed demo version limits itinerary generation to **3 uses per session** to manage API usage and prevent misuse.

---

##  Future Enhancements

- User authentication & login system
- Trip history storage using database
- Smarter budget optimization engine
- API response caching for faster performance
- Multi-language itinerary generation
- Personalized recommendation engine

---


##  License

This project is licensed under the **MIT License**.

You are free to use, modify, and distribute this project with proper attribution.

See the `LICENSE` file for more details.
