# AI-Powered Smart Tourism and Intelligent Travel Management System

An intelligent tourism web platform exclusively crafted for **Kerala, India ("God's Own Country")**, covering all 14 districts:
1. Thiruvananthapuram
2. Kollam
3. Pathanamthitta
4. Alappuzha
5. Kottayam
6. Idukki
7. Ernakulam
8. Thrissur
9. Palakkad
10. Malappuram
11. Kozhikode
12. Wayanad
13. Kannur
14. Kasaragod

---

## 🚀 Technology Stack

- **Backend:** Python 3.13, Django 6.1.3
- **Database:** PostgreSQL 18 (using modern `psycopg` v3 adapter)
- **Frontend:** HTML5, CSS3, JavaScript, Bootstrap 5, Bootstrap Icons, Google Fonts
- **Maps & Geospatial:** Leaflet.js, OpenStreetMap tiles, Browser Geolocation API
- **Image Processing:** Pillow
- **AI & Analytics (Upcoming):** Pandas, NumPy, Scikit-learn
- **Visualizations (Upcoming):** Chart.js

---

## 📌 Development Progress & Completed Phases

### ✅ Phase 1: Django Project Setup & PostgreSQL Integration
- **PostgreSQL Connection:** Configured Django to connect directly to PostgreSQL 18 database `smart_tourism_db`.
- **Environment Management:** Utilized `python-dotenv` with `.env` and `.env.example` to ensure no sensitive credentials or secret keys are hardcoded in source code.
- **Directory Structure:** Configured `static/`, `staticfiles/`, `media/`, and `templates/`.
- **Core Public Portal:**
  - Built the `core` app with responsive landing page (`/`) and About page (`/about/`).
  - Kerala nature & emerald green visual design.
  - Interactive coverage of all 14 districts and 6 core tourism categories (Hill Stations, Beaches, Backwaters, Waterfalls, Wildlife Sanctuaries, Heritage & Culture).
- **Admin Setup:** Configured Django administration portal at `/admin/`.

---

### ✅ Phase 2.1: Tourist Registration, Login & Authentication
- **User Roles:** Enforced strict role-based separation between public tourists and staff/superusers (tourist signups strictly set `is_staff=False` and `is_superuser=False`).
- **TouristProfile Model:** Linked via `OneToOneField` with Django's `User` model, featuring phone number, profile image, address, and Kerala district preferences.
- **Registration Form & Page (`/accounts/register/`):**
  - Full Name, unique Username, unique Email, Phone Number, Password, and Confirm Password.
  - Full validation suite including Django's built-in password security validators.
- **Login Form & Page (`/accounts/login/`):**
  - Custom `EmailOrUsernameBackend` allowing tourists to log in using either their username or email address.
  - "Remember me" session duration management.
- **Tourist Dashboard (`/accounts/dashboard/`):**
  - Protected route requiring authentication (`@login_required`).
  - Personalized welcome banner with the tourist's name.
  - Profile details display (email, phone, district, member since).
  - Quick action modules for *Explore Kerala*, *Plan Your Trip*, *GPS Nearby Discovery*, and *My Trips*.
- **Comprehensive Automated Tests (`accounts/tests.py`):**
  - 16 automated unit tests verifying successful registration, duplicate username rejection, duplicate email rejection, password mismatch validation, dual-login (username/email), invalid credentials rejection, dashboard access control, logout, unauthenticated redirect protection, GPS coordinate saving/updating, range boundary validation, and data preservation. All 16 tests passing.

---

### ✅ Phase 2.2: Tourist GPS Location & Interactive Leaflet Map
- **Interactive Map Integration:** Integrated Leaflet.js with OpenStreetMap tiles centered on Kerala without requiring any proprietary Google Maps API keys.
- **Location Picker (`/accounts/profile/edit/`):**
  - Interactive clickable Kerala map.
  - Draggable location marker dynamically updating coordinate fields.
  - "Use My Current Location" button leveraging the browser Geolocation API (`navigator.geolocation`) with user permission checks.
  - Graceful fallback for manual map picking if location permission is denied.
  - Reverse geocoding via OpenStreetMap Nominatim with respectful error handling.
  - Clear/reset location control.
- **Server-Side Coordinate Validation:** Strict validation of latitude (-90° to +90°) and longitude (-180° to +180°) ranges on Django server before database persistence.
- **Tourist Dashboard Enhancements:** Displays live coordinates badge, landmark name, and interactive mini Leaflet preview map.

---

## 🛠️ Project Structure

```text
SmartTourism/
├── accounts/                  # Tourist authentication & profile app
│   ├── migrations/            # TouristProfile database migrations
│   ├── admin.py               # Django Admin registration for profiles
│   ├── backends.py            # Username or Email auth backend
│   ├── forms.py               # Tourist registration & login forms
│   ├── models.py              # TouristProfile (OneToOne with User)
│   ├── tests.py               # 9 automated auth unit tests
│   ├── urls.py                # Accounts routing
│   └── views.py               # Register, Login, Logout, Dashboard views
├── config/                    # Django project core configuration
│   ├── asgi.py
│   ├── settings.py            # PostgreSQL, Auth, and Static settings
│   ├── urls.py                # Root URL dispatcher
│   └── wsgi.py
├── core/                      # Public portal application
│   ├── urls.py                # Home & About routing
│   └── views.py               # Landing page views
├── static/                    # Custom CSS, JS, and brand assets
├── media/                     # User-uploaded images & destination media
├── templates/                 # Reusable Bootstrap 5 templates
│   ├── base.html              # Base layout with navbar, alerts & footer
│   ├── home.html              # Kerala tourism showcase & 14 districts
│   ├── about.html             # System architecture & stack info
│   └── accounts/
│       ├── register.html      # Tourist signup interface
│       ├── login.html         # Tourist login interface
│       └── dashboard.html     # Protected tourist dashboard
├── .env.example               # Environment variables template
├── .gitignore                 # Security ignore rules
├── manage.py
└── requirements.txt           # Python dependencies
```

---

## ⚙️ Setup and Installation Instructions

### 1. Clone the repository
```bash
git clone https://github.com/Suryakrishnakv/AI-Powered-Smart-Tourism-System.git
cd AI-Powered-Smart-Tourism-System
```

### 2. Create and activate a virtual environment
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# Linux / macOS
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Create a `.env` file in the project root:
```ini
DJANGO_SECRET_KEY=your-secret-key-here
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost,testserver

# PostgreSQL Database Configuration
DB_NAME=smart_tourism_db
DB_USER=postgres
DB_PASSWORD=your_postgres_password
DB_HOST=localhost
DB_PORT=5432
```

### 5. Run Migrations & Start Server
```bash
python manage.py migrate
python manage.py runserver
```

Visit `http://127.0.0.1:8000/` in your browser.

---

## 🧪 Running Automated Tests
```bash
python manage.py test accounts
```
