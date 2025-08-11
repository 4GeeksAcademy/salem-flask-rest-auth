# Star Wars Flask REST API

Flask REST API for managing Star Wars characters, planets, and vehicles with JWT authentication and a secure admin interface. Clean, minimal, and production-ready.

## Features

- JWT Authentication (Flask-JWT-Extended)
- Admin panel (Flask-Admin, protected by Flask-Security)
- User/Role management (Flask-Security)
- SQLite or PostgreSQL support
- bcrypt password hashing
- CORS for frontend integration

## Quick Start

```bash
git clone https://github.com/4GeeksAcademy/salem-flask-rest-auth.git
cd salem-flask-rest-auth

# Backend setup
cd backend
pipenv install
pipenv run flask db upgrade

# Frontend setup
cd ../frontend
npm install

# Start both (from project root)
./devOps/start_fullstack.sh
```

## Creating an Admin User

To access `/admin`, you need a user with the `admin` role. In a Python shell:

```python
from app import create_app
from models import db, User, Role
from flask_security import SQLAlchemyUserDatastore
app = create_app()
app.app_context().push()
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
admin_role = user_datastore.find_or_create_role('admin')
user = user_datastore.create_user(email='admin@example.com', password='yourpassword', fs_uniquifier='uniqueid')
user_datastore.add_role_to_user(user, admin_role)
db.session.commit()
```

## Usage

- Frontend: http://localhost:3001
- Backend API: http://127.0.0.1:3000
- Admin: http://127.0.0.1:3000/admin/ (login required, admin role required)

## Test Credentials

| Email              | Password | Role  |
| ------------------ | -------- | ----- |
| admin@starwars.com | admin123 | admin |

## API Endpoints (examples)

- `POST /api/login` - User login
- `POST /api/register` - User registration
- `GET /api/profile` - Get current user (JWT required)
- `GET /api/people` - List characters
- `GET /api/planets` - List planets
- `GET /api/vehicles` - List vehicles
- `GET /api/users/favorites` - Get user favorites (JWT required)
- `POST /api/favorites` - Add favorite (JWT required)
- `DELETE /api/favorites/<favorite_id>` - Remove favorite (JWT required)

## API Documentation (Swagger/OpenAPI)

You can view and test the API interactively using Swagger UI:

- [Swagger UI (local)](http://127.0.0.1:3000/api/docs) _(if enabled in backend)_
- [Frontend App](http://localhost:3001)

If you want to add or customize the OpenAPI spec, you can use a tool like [flasgger](https://github.com/flasgger/flasgger) or [flask-swagger-ui](https://github.com/swagger-api/swagger-ui) in your backend.

## Database Schema (main tables)

- User: id, email, password, is_active, fs_uniquifier, roles
- Role: id, name, description
- People: id, name, gender, birth_year, image_url
- Planet: id, name, climate, population, image_url
- Vehicle: id, name, model, manufacturer, image_url
- Favorite: id, user_id, people_id, planet_id, vehicle_id

## Features

- JWT Authentication (Flask-JWT-Extended)
- Flask-Security for user/admin management
- Flask-Admin (admin panel)
- SQLite/PostgreSQL
- bcrypt password hashing

salem-flask-rest-auth/

## Project Structure

```
salem-flask-rest-auth/
├── backend/
│   ├── app.py
│   ├── models.py
│   ├── routes.py
│   ├── admin.py
│   ├── migrations/
│   └── instance/
├── frontend/
│   ├── src/
│   └── package.json
├── devOps/
│   ├── quick_db.sh
│   └── start_fullstack.sh
└── README.md
```

## Troubleshooting

- If you see "unable to open database file":
  - Make sure you're in the project root
  - Create the `instance/` directory: `mkdir -p backend/instance`
- If you see migration errors (table exists, missing revision, etc):
  - Reset migrations and DB (dev only):
    ```bash
    rm -rf backend/migrations
    rm backend/app.db
    cd backend
    pipenv run flask db init
    pipenv run flask db migrate -m "Initial migration"
    pipenv run flask db upgrade
    ```
- If you see `ValueError: User model must contain fs_uniquifier as of 4.0.0`:
  - Add `fs_uniquifier` to your User model and re-run migrations.

3. **Port conflicts**: Backend uses 3000, frontend uses 3001
4. **Migration errors**: Use `./devOps/quick_db.sh reset` to start fresh
5. **Python command**: On macOS, use `python3` instead of `python` for all commands

````



```

```
````
