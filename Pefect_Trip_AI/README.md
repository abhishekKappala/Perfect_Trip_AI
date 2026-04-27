#  Yatra Saarthi – AI Student Travel Planner

Yatra Saarthi is an AI-powered travel planning web application designed specifically for students.  
It generates personalized, budget-friendly itineraries using Large Language Models, real-time location data, and interactive maps.

🚀 Live Demo: https://yatra-saarthi-01.streamlit.app

---

## Features

-  AI-powered itinerary generation using Groq LLM
-  Real-time nearby attractions using OpenStreetMap (Overpass API)
-  Interactive map visualization with PyDeck
-  Automatic budget breakdown and cost estimation
-  Downloadable day-wise travel plan in PDF format
-  Secure API key management using Streamlit Secrets
-  Session-based usage limiting for demo control

---

##  How It Works

1. User enters:
   - Destination
   - Duration
   - Budget
   - Interests
   - Accommodation type

2. The system:
   - Geocodes the destination
   - Fetches nearby attractions using OpenStreetMap APIs
   - Sends structured prompt to Groq LLM
   - Receives JSON itinerary response
   - Displays formatted itinerary with budget breakdown
   - Generates downloadable PDF

---

## 🛠 Tech Stack

| Technology | Purpose |
|------------|----------|
| Streamlit | Web application framework |
| Groq API (LLM) | AI itinerary generation |
| OpenStreetMap + Overpass API | Nearby attractions data |
| PyDeck | Interactive maps |
| ReportLab | PDF generation |
| Pandas | Data handling |

Dependencies (from `requirements.txt`):

---

## 📂 Project Structure

```
AI-Travel-Planner/
│
├── app.py                # Main Streamlit application
├── ai_module.py          # Groq LLM integration logic
├── map_utils.py          # OpenStreetMap & Overpass API utilities
├── pdf_generator.py      # PDF generation using ReportLab
├── requirements.txt      # Project dependencies
└── .streamlit/
    └── config.toml       # Theme configuration (optional)
```

---

## ⚙️ Local Setup Instructions

### 1️) Clone the Repository

```bash
git clone https://github.com/your-username/AI-Travel-Planner.git
cd AI-Travel-Planner
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
