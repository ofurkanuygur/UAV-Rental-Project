# 🛩 Aircraft Production System

<div align="center">

![Python](https://img.shields.io/badge/python-3.9-blue.svg)
![Django](https://img.shields.io/badge/django-4.2.0-green.svg)
![PostgreSQL](https://img.shields.io/badge/postgresql-13-blue.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

</div>

## 📋 About

A comprehensive aircraft production management system designed for manufacturing and assembly processes of various UAV models including TB2, TB3, AKINCI, and KIZILELMA. The system provides end-to-end management of the production lifecycle, from component manufacturing to final assembly.

## 🚀 Features

### Core Functionality
- 👥 **Personnel Management**
  - User authentication and authorization
  - Team-based access control
  - Role-based permissions

- 🔧 **Part Management**
  - CRUD operations for parts
  - Team-specific part production restrictions
  - Part tracking and inventory management

- 🏭 **Production Management**
  - Aircraft assembly workflow
  - Quality control checkpoints
  - Production history tracking

### Technical Features
- 🔐 **Security**
  - JWT Authentication
  - Role-based access control
  - Secure password handling

- 📊 **API Documentation**
  - Swagger/OpenAPI integration
  - API versioning
  - Comprehensive endpoint documentation

## 🛠 Tech Stack

### Backend
- **Framework:** Django 4.2.0
- **API:** Django REST Framework 3.14.0
- **Authentication:** JWT (djangorestframework-simplejwt)
- **Database:** PostgreSQL 13
- **Documentation:** drf-yasg (Swagger/OpenAPI)

### Frontend
- **Framework:** Bootstrap 5
- **JavaScript:** Vanilla JS
- **Icons:** Font Awesome
- **Styling:** Custom CSS

### DevOps
- **Containerization:** Docker
- **Version Control:** Git
- **CI/CD:** GitHub Actions (planned)
- **Deployment:** Nginx, Gunicorn

## 🚀 Getting Started

### Prerequisites
- Python 3.9+
- PostgreSQL 13+
- pip (Python package manager)
- virtualenv

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd UAV-Rental-Project
```

2. **Set up virtual environment**
```bash
python3.9 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Environment Setup**
```bash
cp .env.example .env
# Edit .env with your settings
```

5. **Database Setup**
```bash
# Create database
createdb aircraft_db

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

6. **Static Files**
```bash
# Make setup script executable
chmod +x setup_static.sh

# Run setup script
./setup_static.sh
```

7. **Run Development Server**
```bash
python manage.py runserver
```

Visit `http://localhost:8000` in your browser.

## 🐳 Docker Setup

1. **Build and Run**
```bash
docker-compose -f docker/docker-compose.yml up --build
```

2. **Run Migrations**
```bash
docker-compose -f docker/docker-compose.yml exec web python manage.py migrate
```

3. **Create Superuser**
```bash
docker-compose -f docker/docker-compose.yml exec web python manage.py createsuperuser
```

## 📁 Project Structure
```
UAV-Rental-Project/
├── aircraft_production/    # Main project settings
├── apps/                   # Django applications
│   ├── accounts/          # User management
│   ├── assembly/          # Assembly process
│   ├── parts/             # Parts management
│   └── teams/             # Team management
├── static/                # Static files
├── templates/             # HTML templates
└── docker/               # Docker configuration
```

## 🔒 Security Features
- SSL/TLS encryption (in production)
- CSRF protection
- XSS prevention
- Secure password hashing
- Session security


## 📝 API Documentation
- Swagger UI: `/swagger/`
- ReDoc: `/redoc/`
- OpenAPI Schema: `/swagger.json`
