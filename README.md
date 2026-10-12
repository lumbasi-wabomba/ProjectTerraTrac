# Project TerraTrac

TerraTrac is a forest monitoring platform that combines satellite NDVI analysis and community reporting to help track afforestation and deforestation activity.

## Features

- User registration, login, logout, and token-based authentication
- Forest area management
- NDVI calculation using Google Earth Engine (Sentinel-2 imagery)
- NDVI record storage per forest area
- Alerts for detected or reported changes
- Community reports linked to alerts
- Alert verification workflow
- React frontend with a login UI starter

## Tech Stack

- **Backend:** Django, Django REST Framework
- **Frontend:** React + Vite
- **Database:** MySQL
- **Geospatial/Remote Sensing:** Google Earth Engine Python API

## Repository Structure

- `/config` - Django project configuration
- `/terratrac` - Core backend app (models, serializers, views, routes, NDVI logic)
- `/templates` - Django HTML templates
- `/frontend` - React frontend

## Prerequisites

- Python 3.10+
- Node.js 18+
- MySQL 8+
- Google Earth Engine access/project configured for the account running the backend

## Backend Setup

1. Create and activate a virtual environment.
2. Install dependencies (example):
   - `pip install django djangorestframework django-filter mysqlclient earthengine-api`
3. Configure database and Django settings in:
   - `/home/runner/work/ProjectTerraTrac/ProjectTerraTrac/config/settings.py`
4. Run migrations:
   - `python manage.py migrate`
5. Start the backend server:
   - `python manage.py runserver`

## Frontend Setup

1. Go to frontend:
   - `cd /home/runner/work/ProjectTerraTrac/ProjectTerraTrac/frontend`
2. Install dependencies:
   - `npm install`
3. Start development server:
   - `npm run dev`

## API Endpoints (Base URL: `/`)

### Auth
- `POST /register/`
- `POST /login/`
- `POST /logout/`

### NDVI
- `POST /ndvi_calc/`

### REST Resources
- `/users/`
- `/forest-areas/`
- `/ndvi-records/`
- `/alerts/`
- `/community-reports/`

## Notes

- The backend currently uses token authentication for protected endpoints.
- Staff permissions are required for some management operations (for example, creating forest areas).

