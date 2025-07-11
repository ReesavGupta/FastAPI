# User Authentication System (FastAPI)

A secure user authentication system with JWT tokens and role-based access control, built with FastAPI, SQLAlchemy, and SQLite.

## Features
- User registration with password hashing (bcrypt)
- JWT authentication (30 min expiry)
- Role-based access control (admin/user)
- Admin endpoints for user management
- Password strength validation

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
2. **Run the server:**
   ```bash
   uvicorn main:app --reload
   ```

## API Endpoints

### Auth
- `POST /auth/register` — Register a new user
- `POST /auth/login` — Login and get JWT token
- `GET /auth/me` — Get current user info (JWT required)

### Admin Endpoints (require admin role)
- `GET /users` — List all users
- `PUT /users/{user_id}/role` — Change user role (body: `{ "role": "admin"|"user" }`)
- `DELETE /users/{user_id}` — Delete a user

## JWT Usage
- Pass the token in the `Authorization: Bearer <token>` header for protected routes.

## Notes
- Default DB: SQLite (`users.db`)
- Change `SECRET_KEY` in `auth.py` for production.
- Passwords must be at least 8 characters and contain a special character. 