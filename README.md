# Aircraft Production System

## About
This project is an aircraft production management system that handles the manufacturing and assembly process of various UAV models including TB2, TB3, AKINCI, and KIZILELMA.

## Features
- Personnel authentication and team management
- Part management (CRUD operations) for different teams
- Team-specific part production restrictions
- Aircraft assembly management
- Inventory tracking and warnings
- Production history tracking

## Technical Stack
- Backend: Python, Django, Django REST Framework
- Database: PostgreSQL
- Frontend: HTML, CSS, JavaScript, Bootstrap
- Additional: Docker, Swagger

## Setup Instructions

1. Clone the repository:
```bash
git clone <repository-url>
cd UAV-Rental-Project
```

2. Create and activate virtual environment:
```bash
python3.9 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
```
Then edit `.env` file with your settings:
- Generate a new SECRET_KEY
- Set your database credentials
- Configure email settings (optional)
- Adjust other settings as needed

5. Set up PostgreSQL database:
- Create a new database named 'name_db'
- Update database credentials in .env if needed

6. Set up static files:
```bash
chmod +x setup_static.sh  # Make script executable
./setup_static.sh        # This will download Bootstrap and jQuery
```

7. Run database migrations:
```bash
python manage.py migrate
```

8. Create a superuser:
```bash
python manage.py createsuperuser
```

9. Run the development server:
```bash
python manage.py runserver
```

The application will be available at `http://localhost:8000`

## Project Structure
```
UAV-Rental-Project/
├── aircraft_production/    # Main project settings
├── apps/                   # Django applications
│   ├── accounts/          # User management
│   ├── assembly/          # Assembly process
│   ├── parts/             # Parts management
│   └── teams/             # Team management
├── static/                # Static files
│   ├── css/              # Custom CSS
│   ├── js/               # Custom JavaScript
│   └── vendor/           # Third-party libraries (auto-downloaded)
├── templates/            # HTML templates
└── manage.py            # Django management script
```

## Development

- Custom CSS and JS files are version controlled
- Third-party libraries (Bootstrap, jQuery) are downloaded during setup
- Use `setup_static.sh` to set up required static files after cloning

## Contributing
1. Create a feature branch
2. Make your changes
3. Submit a pull request

## License
This project is licensed under the MIT License.