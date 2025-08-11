## API Route Tree

```
/ (root) [GET] (HTML welcome)
├── api/
│   ├── profile                   [GET]   (JWT required)
│   ├── people
│   │   ├──                       [GET]   (List all people)
│   │   └── <person_id>           [GET]   (Get person by ID)
│   ├── planets
│   │   ├──                       [GET]   (List all planets)
│   │   └── <planet_id>           [GET]   (Get planet by ID)
│   ├── vehicles
│   │   ├──                       [GET]   (List all vehicles)
│   │   └── <vehicle_id>          [GET]   (Get vehicle by ID)
│   └── favorites
│       ├──                       [GET]   (JWT required, list user's favorites)
│       ├──                       [POST]  (JWT required, add favorite)
│       └── <favorite_id>         [DELETE] (JWT required, delete favorite)
├── api/docs/                     [GET]   (Swagger UI)
├── admin/                        [GET]   (Admin panel, login required)
```

## app.py Structure

```
app.py
├── create_app()
│   ├── Loads config from env
│   ├── Initializes extensions (db, migrate, jwt, cors, swagger, security)
│   ├── Registers admin and API routes
│   ├── Defines root route (HTML welcome)
│   ├── Handles API errors (JSON for /api/*)
│   └── Optionally checks DB connection on startup
└── if __name__ == "__main__": runs app on port 3000
```

## Frontend React Structure (minimal)

```
frontend/
├── src/
│   ├── main.jsx           # App entry point
│   ├── routes.jsx         # React Router routes
│   ├── store.js           # State management
│   ├── components/
│   │   ├── CardContainer.jsx
│   │   ├── Cards.jsx
│   │   ├── Login.jsx
│   │   └── Navbar.jsx
│   ├── pages/
│   │   ├── CardView.jsx
│   │   ├── Home.jsx
│   │   └── Layout.jsx
│   ├── hooks/
│   │   └── useGlobalReducer.jsx
│   ├── data/
│   │   └── starWarsData.jsx
│   └── styles/
│       ├── border-themes.css
│       ├── custom-borders.css
│       └── global.css
├── package.json
└── vite.config.js
```

# Star Wars Flask REST API

Minimal Flask REST API for Star Wars data with JWT authentication, admin panel, and React frontend.

## Prerequisites

- Python 3.10+ and pipenv
- Node.js and npm



# Install backend dependencies
cd backend
pipenv install
pipenv shell   # Activate the virtual environment

# Install frontend dependencies
cd ../frontend
npm install

# Go back to project root
cd ..

python3 devOps/quick_db.py reset         # Sets up DB and migrations (does NOT add sample data or users)
python3 devOps/quick_db.py add-data      # (NEW) Adds Star Wars sample data
python3 devOps/quick_db.py create-users  # (NEW) Adds default admin and test users
python3 devOps/start_fullstack.py        # Starts backend and frontend
```

## Testing the API

Run the smoke test script to check all main endpoints:

```bash
export JWT_TOKEN=your_token_here
python3 devOps/api_smoke_test.py
```

## Admin Access

Default admin user:

| Email              | Password | Role  |
| ------------------ | -------- | ----- |
| admin@starwars.com | admin123 | admin |

Go to [http://127.0.0.1:3000/admin/](http://127.0.0.1:3000/admin/) and log in.

## API Docs

- Swagger UI: [http://127.0.0.1:3000/api/docs](http://127.0.0.1:3000/api/docs)
- Frontend:   [http://localhost:3001](http://localhost:3001)

## Project Structure

```
salem-flask-rest-auth/
├── backend/
├── frontend/
└── devOps/
```

## Troubleshooting

- Use `python3 devOps/quick_db.py reset` to reset DB and migrations
- Use `python3` for all backend commands on macOS
- Backend: port 3000, Frontend: port 3001

```

```
````
