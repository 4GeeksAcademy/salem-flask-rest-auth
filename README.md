# Star Wars Flask REST API

Flask REST API for managing Star Wars characters, planets, and vehicles with JWT authentication and admin interface. Features a clean, modular code structure with minimal redundancy.

## Features

- **Modular Architecture**: Clean separation of concerns with dedicated modules
- **JWT Authentication**: Secure API endpoints with JWT tokens
- **Admin Interface**: Built-in admin panel for data management
- **API Documentation**: Interactive Swagger UI documentation
- **Pagination**: Efficient data retrieval with pagination support
- **Environment Variables**: Easy configuration through environment variables
- **Database Agnostic**: Works with SQLite by default, compatible with PostgreSQL

## Quick Start

### Full Stack Application

```bash
# One-line setup (after dependencies are installed)
./devOps/start_fullstack.sh
```

### Complete Setup

```bash
git clone https://github.com/4GeeksAcademy/salem-flask-rest-auth.git
cd salem-flask-rest-auth

# Install dependencies
cd backend && pipenv install && cd ..
cd frontend && npm install && cd ..

# Initialize database and add data
./devOps/quick_db.sh init
./devOps/quick_db.sh add-data
./devOps/quick_db.sh create-users

# Start both frontend and backend
./devOps/start_fullstack.sh
```

## Prerequisites

- Python 3.7+ (use `python3` command on macOS)
- pipenv (`pip3 install pipenv` on macOS)
- Git
- Node.js & npm

**Note:** This repository includes fixed scripts that work with the actual project structure and use `pipenv` for Python environment management. On macOS, install pipenv using `pip3 install pipenv`.

## Installation

- **Git** - [Download Git](https://git-scm.com/downloads)

### 1. Clone Repository

```bash
git clone https://github.com/4GeeksAcademy/salem-flask-rest-auth.git
cd salem-flask-rest-auth
```

### 2. Install Dependencies

```bash
# Backend
cd backend
pipenv install

# Frontend
cd ../frontend
npm install
cd ..
```

### 3. Setup Database

```bash
# From project root directory
./devOps/quick_db.sh init
./devOps/quick_db.sh add-data
./devOps/quick_db.sh create-users
```

### 4. Start Application

```bash
# Full stack (recommended)
./devOps/start_fullstack.sh

# Or backend only
cd backend && pipenv run python3 app.py
```

## Usage

### Access Points

- Frontend: http://localhost:3001
- Backend API: http://127.0.0.1:3000
- Admin Interface: http://127.0.0.1:3000/admin/

### Test Credentials

| Email              | Password    | Character      |
| ------------------ | ----------- | -------------- |
| luke@jedi.com      | usetheforce | Luke Skywalker |
| leia@rebellion.com | rebel123    | Princess Leia  |
| vader@empire.com   | darkside    | Darth Vader    |
| admin@starwars.com | admin123    | Admin Account  |

## API Endpoints

### Authentication

- `POST /api/auth/login` - User login
- `POST /api/auth/register` - User registration
- `GET /api/auth/me` - Get current user
- `POST /api/auth/logout` - User logout

### Data

- `GET /api/people` - List characters
- `GET /api/people/<id>` - Get character
- `GET /api/planets` - List planets
- `GET /api/planets/<id>` - Get planet
- `GET /api/vehicles` - List vehicles
- `GET /api/vehicles/<id>` - Get vehicle

### Favorites (Protected)

- `GET /api/users/favorites` - Get user favorites
- `POST /api/favorite/people/<id>` - Toggle character favorite
- `POST /api/favorite/planet/<id>` - Toggle planet favorite
- `POST /api/favorite/vehicle/<id>` - Toggle vehicle favorite

## Database Schema

- **User**: `id`, `email`, `password` (bcrypt), `is_active`
- **People**: `id`, `name`, `gender`, `birth_year`, `image_url`
- **Planet**: `id`, `name`, `climate`, `population`, `image_url`
- **Vehicle**: `id`, `name`, `model`, `manufacturer`, `image_url`
- **Favorite**: `id`, `user_id`, `people_id`, `planet_id`, `vehicle_id`

## Features

- JWT Authentication with Flask-JWT-Extended
- SQLite database with Flask-SQLAlchemy
- Admin interface with Flask-Admin
- CORS enabled for frontend integration
- bcrypt password hashing

## Project Structure

### Production Security Recommendations

1. Set JWT token expiration times
2. Use environment variables for JWT secrets
3. Implement token refresh functionality
4. Add rate limiting
5. Use HTTPS in production
6. Implement proper CORS policies

## 📁 Project Structure

```
salem-flask-rest-auth/
├── backend/
│   ├── app.py              # Main Flask application (JWT configured)
│   ├── models.py           # Database models (User with bcrypt)
│   ├── routes.py           # API endpoints (JWT protected)
│   ├── jwt_utils.py        # JWT authentication utilities
│   ├── admin.py            # Admin interface setup
```

salem-flask-rest-auth/
├── backend/ # Python Flask Application
│ ├── app.py, models.py, routes.py, etc.
│ ├── Pipfile & Pipfile.lock
│ ├── requirements.txt
│ ├── models_diagram.png
│ ├── migrations/
│ └── instance/
├── frontend/ # React Application  
│ ├── src/
│ ├── index.html
│ └── package.json
├── devOps/ # Development & Operations
│ ├── quick_db.sh
│ ├── start_fullstack.sh
│ └── backups/
├── .venv/
└── README.md

````

## Troubleshooting

### macOS-Specific Notes

On macOS, use `python3` instead of `python` for all commands:

```bash
# For installing pipenv
pip3 install pipenv

# For running scripts
pipenv run python3 app.py

# When manually running Python files
python3 add_data.py
```

### Setup Issues

**Database Connection Errors:**
```bash
# If you see "unable to open database file"
# 1. Ensure you're in project root directory
# 2. Create instance directory if missing:
mkdir -p instance

# 3. Check database path in backend/app.py matches your project path
````

**Script Execution Errors:**

```bash
# If quick_db.sh fails with "Virtual environment not found"
# 1. Make sure you're in project root (not backend directory)
# 2. Ensure backend/Pipfile exists
cd backend && pipenv install && cd ..

# If start_fullstack.sh fails
# 1. Check paths are correct (scripts updated for this structure)
# 2. Ensure package.json exists in frontend/
```

**Migration Errors:**

```bash
# If migrations fail or show "Target database is not up to date"
./devOps/quick_db.sh reset  # This will reset everything
# Then follow normal setup process
```

## Database Management

```bash

```

## Database Management

```bash
# From project root directory (not backend/)
./devOps/quick_db.sh              # Interactive menu
./devOps/quick_db.sh add-data     # Add sample data
./devOps/quick_db.sh create-users # Create test users
./devOps/quick_db.sh backup       # Backup database
```

## Development

### Important Notes

- **Always run database scripts from project root**, not from backend directory
- Database scripts use `pipenv` (not virtual env) and are configured for this project structure
- Frontend is a Vite/React project that runs on port 3001
- Backend Flask API runs on port 3000
- Make sure `instance/` directory exists for SQLite database

### Pipenv Scripts (from backend directory)

```bash
# From backend directory only
pipenv run python3 app.py     # Start backend only
```

### Common Issues & Solutions

1. **Database path errors**: Ensure you're running scripts from project root
2. **Missing package.json**: Frontend package.json is included (Vite/React project)
3. **Port conflicts**: Backend uses 3000, frontend uses 3001
4. **Migration errors**: Use `./devOps/quick_db.sh reset` to start fresh
5. **Python command**: On macOS, use `python3` instead of `python` for all commands

````

## Code Structure

The project follows a modular approach to minimize redundancy and improve maintainability:

```
backend/
├── app.py              # Application factory and core setup
├── routes.py           # API endpoint definitions
├── models.py           # Database models and relationships
├── admin.py            # Admin interface configuration
├── utils.py            # Helper functions and utilities
├── jwt_utils.py        # JWT authentication helpers
├── templates/          # HTML templates for web interfaces
│   └── main/           # Landing page and API documentation
└── static/             # Static assets and API specifications
```

### Key Design Principles

1. **DRY (Don't Repeat Yourself)**: Shared functionality is extracted into helper functions
2. **Separation of Concerns**: Each module has a specific responsibility
3. **Configuration via Environment**: Settings are managed via environment variables
4. **Generic Handlers**: Common patterns use shared code for similar endpoints
5. **Factory Pattern**: Application is created via a factory for flexibility in testing and deployment

## Development

### Pipenv Scripts

```bash
# From backend directory
pipenv run start         # Start backend
pipenv run fullstack     # Start full stack
pipenv run db-init       # Initialize database
pipenv run db-data       # Add sample data
pipenv run db-users      # Create users
```

## License

Educational project for 4Geeks Academy curriculum.
````
