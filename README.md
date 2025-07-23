# Client Sync Project

A Django project configured to use both PostgreSQL and MongoDB databases.

## Prerequisites

- Docker and Docker Compose
- Python 3.8+
- pip

## Setup Instructions

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 2. Start the Databases

Start PostgreSQL and MongoDB using Docker Compose:

```bash
docker-compose up -d
```

This will start:
- PostgreSQL on port 5432
- MongoDB on port 27017
- Mongo Express (MongoDB admin interface) on port 8081

### 3. Configure Environment Variables

Copy the configuration file and modify as needed:

```bash
cp config.env .env
```

Edit `.env` file with your preferred settings.

### 4. Run Django Migrations

```bash
python manage.py migrate
```

### 5. Create a Superuser (Optional)

```bash
python manage.py createsuperuser
```

### 6. Run the Development Server

```bash
python manage.py runserver
```

## Database Access

- **PostgreSQL**: `localhost:5432`
  - Database: `client_sync_db`
  - Username: `client_sync_user`
  - Password: `client_sync_password`

- **MongoDB**: `localhost:27017`
  - Database: `client_sync_mongo`
  - Username: `client_sync_user`
  - Password: `client_sync_password`

- **Mongo Express**: `http://localhost:8081`
  - Username: `admin`
  - Password: `admin123`

## Stopping the Databases

```bash
docker-compose down
```

To remove volumes as well:

```bash
docker-compose down -v
```

## Project Structure

- `client_sync/` - Django project settings
- `docker-compose.yml` - Database containers configuration
- `requirements.txt` - Python dependencies
- `config.env` - Environment variables template 