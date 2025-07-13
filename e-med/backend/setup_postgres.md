# PostgreSQL Setup Guide for MediDash

## Prerequisites

1. **Install PostgreSQL** (if not already installed)
   - Windows: Download from https://www.postgresql.org/download/windows/
   - macOS: `brew install postgresql`
   - Ubuntu: `sudo apt-get install postgresql postgresql-contrib`

## Setup Steps

### 1. Start PostgreSQL Service
```bash
# Windows (if installed as service)
# PostgreSQL should start automatically

# macOS
brew services start postgresql

# Ubuntu
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

### 2. Create Database and User
```bash
# Connect to PostgreSQL as superuser
psql -U postgres

# Create database
CREATE DATABASE medidash_db;

# Create user (optional - you can use postgres user)
CREATE USER medidash_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE medidash_db TO medidash_user;

# Exit psql
\q
```

### 3. Update Environment Variables
Edit `.env` file with your PostgreSQL credentials:

```env
# For default postgres user
DATABASE_URL=postgresql://postgres:your_password@localhost:5432/medidash_db

# Or for custom user
DATABASE_URL=postgresql://medidash_user:your_password@localhost:5432/medidash_db
```

### 4. Initialize Database
```bash
# Create tables
python init_db.py

# Or use Alembic for migrations (recommended for production)
alembic init alembic
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

## Alternative: Using Docker

If you prefer Docker, you can run PostgreSQL in a container:

```bash
# Pull PostgreSQL image
docker pull postgres:15

# Run PostgreSQL container
docker run --name medidash-postgres \
  -e POSTGRES_DB=medidash_db \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=password \
  -p 5432:5432 \
  -d postgres:15
```

Then update your `.env`:
```env
DATABASE_URL=postgresql://postgres:password@localhost:5432/medidash_db
```

## Testing Connection

You can test the connection by running:
```bash
python -c "
from app.core.database import engine
from sqlalchemy import text
with engine.connect() as conn:
    result = conn.execute(text('SELECT 1'))
    print('PostgreSQL connection successful!')
"
```

## Troubleshooting

1. **Connection refused**: Make sure PostgreSQL is running
2. **Authentication failed**: Check username/password in DATABASE_URL
3. **Database doesn't exist**: Create the database first
4. **Permission denied**: Make sure user has proper privileges 