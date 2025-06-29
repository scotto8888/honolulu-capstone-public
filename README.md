## Honolulu 311 Service Request Map

This project is a Flask-based web application that displays public 311 service requests on an interactive map. It allows users to view, search, and filter 311 service requests by service type, description, and date range, with request details displayed via interactive Leaflet map popups. The data is updated daily from the City of Honolulu 311 API using a scheduled ingestion script. Project is meant to be compatible with Railway.

---

## Features

- **Live Search Filters** for:
  - Service Type
  - Description (partial text match)
  - Date range
- **Interactive Leaflet Map**
  - Popups display service type, status, description, and request ID
  - Map automatically updates from GeoJSON API
- **Automated Daily Data Ingestion**
  - Cron job fetches new 311 data daily from the Honolulu API
  - Tracks insertions, status updates, and skipped unchanged records
  - Supports logging for transparency
- **REST API Endpoint**
  - /api/requests serves valid GeoJSON format for frontend map
  - Returns enhanced data with SourceRequestID and Description
- **Status Change Tracking**
  - When a service request’s status changes, the change is logged with a timestamp
- **Modular and Deployable**
  - Flask backend with PostgreSQL database
  - Deployment-ready on Railway
  - Ingestion logic split into a standalone service for scheduled execution

---

## Project Structure

```text
honolulu-capstone/
├── app/                         
│   ├── __init__.py              # Initializes Flask app
│   ├── routes.py		 # Flask routes and API
│   ├── db_connect.py            # App-specific DB connection
│   ├── static/js/map.js         # Leaflet map logic
│   └── templates/
│       └── index.html		 # HTML page for the Map
│
├── ingestion/                   
│   ├── ingest_311_data.py       # Fetches and inserts 311 data, logs status changes
│   ├── db_connect.py            # Minimal DB connection for ingestion
│   └── requirements.txt         # Minimal dependencies for ingestion
|
├── scripts/
│   ├── initialize_schema.py     # Creates tables/schema
│   └── test_connection.py       # Verifies DB connection
|
├── run.py                       # Flask app entry point
├── requirements.txt             # Full app dependencies
├── Procfile                     # Gunicorn start config for Railway
├── .env.example                 # Environment variable template
└── .gitignore                   # File exclusions
```

---
## Getting Started

- **1. Clone the Repo**

        git clone https://github.com/yourusername/honolulu-capstone.git
        cd honolulu-capstone


- **2. Create a Virtual Environment**

        python -m venv venv
        venv\Scripts\activate   # or source venv/bin/activate on Mac/Linux


- **3. Install Dependencies**

        pip install -r requirements.txt


- **4. Set Up Environment Variables**
    **Create a .env file based on the .env.example template:**

        DATABASE_URL=postgresql://username:password@host:port/dbname
        FLASK_ENV=development


- **5. Initialize the Database**

        python scripts/initialize_schema.py


- **6. Ingest initial data**
        python ingestion/ingest_311_data.py


- **7. Run the App (for initial testing)**

        python run.py

    **Then open your browser to: http://localhost:5000**

---

## Deployment (Railway Frontend + API)
**Required steps:**
- **1. Create a new Railway project and link this repo**

- **2. Set the following Environment Variables in Railway:**
  - DATABASE_URL (your PostgreSQL connection string)
  - FLASK_ENV=production

- **3. Confirm your Procfile contains:**
        web: gunicorn run:app

- **4. Ensure run.py is at the root and uses create_app()**

- **5. Public networking**
  - Make sure the Railway service is listening on the correct public port
  - Railway typically maps external traffic to port 8080, but this can vary
  - You can verify or re-establish your domain via:
    - Select the Github deployed Flask app Railway service > Settings > Networking > Public Networking
    - If needed, delete and re-add the domain to refresh its routing

## Deployment (Ingestion Cron Job)

- **1. In Railway, create a **new service** from the same repo**
- **2. In the new service:**
   - Set the Root Directory to `ingestion`
   - Set the Start Command to:
     
        python ingest_311_data.py
     
   - Add the same `DATABASE_URL` variable.
   - No need to set FLASK_ENV
**3. In this Service's Settings > Cron Schedule, set:**
   
        0 10 * * *  (for daily ingestion at 10AM UTC)
   
**4. Optionally, trigger the job manually to test ingestion**