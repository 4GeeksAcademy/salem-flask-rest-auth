# Star Wars Flask REST API

Flask REST API for managing Star Wars characters, planets, and vehicles with JWT authentication and admin interface.

## Quick Start

### Full Stack Application

```bash
cd backend && pipenv run fullstack
```

### Complete Setup

```bash
git clone https://github.com/4GeeksAcademy/salem-flask-rest-auth.git
cd salem-flask-rest-auth
cd backend && pipenv install && cd ..
cd frontend && npm install && cd ..
cd backend && pipenv run ../devOps/quick_db.sh init
pipenv run ../devOps/quick_db.sh add-data
pipenv run ../devOps/quick_db.sh create-users
pipenv run ../devOps/start_fullstack.sh
```

## Prerequisites

- Python 3.7+
- pipenv (`pip install pipenv`)
- Git
- Node.js & npm

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
cd backend
pipenv run ../devOps/quick_db.sh init
pipenv run ../devOps/quick_db.sh add-data
pipenv run ../devOps/quick_db.sh create-users
```

### 4. Start Application

```bash
# Full stack
pipenv run ../devOps/start_fullstack.sh

# Or backend only
pipenv run python app.py
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

## Database Management

```bash
# From backend directory
pipenv run ../devOps/quick_db.sh              # Interactive menu
pipenv run ../devOps/quick_db.sh add-data     # Add sample data
pipenv run ../devOps/quick_db.sh create-users # Create test users
pipenv run ../devOps/quick_db.sh backup       # Backup database
````

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
