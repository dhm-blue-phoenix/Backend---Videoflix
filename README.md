# Videoflix API Backend

Welcome to the backend of the Videoflix platform! This Django-based API provides the server logic for a modern video streaming application. It handles user authentication, automated video processing into HLS formats (HTTP Live Streaming), and secure media delivery through RESTful endpoints.

## Requirements

- **Docker** and **docker-compose** (or Podman/podman-compose) installed.
- **Python:** 3.10+ (if running locally without Docker).

Check your Docker version:
```bash
docker --version
```

## Quick Start

1. Clone the repository and navigate to the folder:

   ```bash
   git clone https://github.com/your-username/Backend---Videoflix.git
   cd Backend---Videoflix
   ```

2. Create a `.env` file in the root directory based on `.env.template`:

   ```bash
   cp .env.template .env
   ```
   *Update the `.env` file with your specific environment configurations (e.g., `SECRET_KEY`, `FRONTEND_URL`, `BACKEND_URL`).*

   > **Note:** Never commit your `.env` file to version control. It is listed in `.gitignore` by default.

3. Start the application using Docker Compose:

   ```bash
   docker-compose up --build -d
   ```
   *(Use `podman-compose` if you are using Podman).*

4. Apply migrations and create a superuser (run inside the web container):

   ```bash
   docker-compose exec web python manage.py migrate
   docker-compose exec web python manage.py createsuperuser
   ```

   The API will be available at `http://localhost:8000/`.
   Mailhog (for capturing emails) is available at `http://localhost:8025/`.

## API Endpoints

### Authentication

- `POST /api/register/` - Register a new user (sends activation email).
- `GET /api/activate/<uidb64>/<token>/` - Activate user account via email token.
- `POST /api/login/` - Authenticate and receive JWT tokens (stored in HttpOnly cookies).
- `POST /api/logout/` - Logout user and invalidate tokens.
- `POST /api/token/refresh/` - Request a new access token using a valid refresh cookie.
- `POST /api/password_reset/` - Request a password reset email.
- `POST /api/password_confirm/<uidb64>/<token>/` - Confirm new password.

### Video

- `GET /api/video/` - List all available videos with metadata (title, thumbnail, category).
- `GET /api/video/<int:movie_id>/<str:resolution>/index.m3u8` - Get HLS master playlist for a specific resolution.
- `GET /api/video/<int:movie_id>/<str:resolution>/<str:segment>/` - Get an individual HLS video segment (`.ts`).

## Running Tests

To run the automated test suite, execute the following command inside your running container:

```bash
docker-compose exec web python manage.py test app_auth app_video
```

This will run all tests across the authentication and video modules to ensure stability and 100% compliance with project requirements.

## Project Structure

```
./
├── core/                 # Main Django project configuration
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── app_auth/             # User registration, JWT cookies, email activation
│   ├── models.py         # Custom User model
│   ├── tasks.py          # Email sending logic
│   ├── api/
│   │   ├── views.py
│   │   ├── serializers.py
│   │   ├── utils.py
│   │   └── urls.py
├── app_video/            # Video management and HLS processing
│   ├── models.py         # Video model and metadata
│   ├── tasks.py          # Background FFmpeg processing (Django RQ)
│   ├── api/
│   │   ├── views.py
│   │   ├── serializers.py
│   │   ├── utils.py
│   │   └── urls.py
├── media/                # Storage for original videos, thumbnails, and HLS segments
├── docker-compose.yml    # Docker services configuration (db, redis, web, mailhog)
├── backend.Dockerfile    # Docker image definition for the Django app
└── manage.py
```

## Authentication

The API uses **JWT Token-based authentication via HttpOnly Cookies** for enhanced security. 
After registering and activating the account, the `/api/login/` endpoint will set `access_token` and `refresh_token` cookies. These cookies are automatically attached to subsequent requests by the browser, meaning the frontend does not need to handle tokens manually.

## Background Processing

Heavy tasks such as HLS video conversion (480p, 720p, 1080p) and thumbnail extraction are handled asynchronously. When a new video is uploaded, the system utilizes **Redis** and **Django RQ** to spawn background worker processes. This keeps the API responsive even during intensive FFmpeg operations.

## Custom Docker Modifications

Compared to the standard `docker-compose` and Dockerfile templates provided by the Developer Akademie, the following project-specific enhancements were made:

- **`backend.Dockerfile`**: Added `jpeg-dev` and `zlib-dev` to the `.build-deps` layer to support image processing (required for Pillow and thumbnail generation).
- **`docker-compose.yml`**: 
  - Added the `:Z` flag to all volume mounts (`:Z`) to ensure strict SELinux compatibility when running with Podman on Linux.
  - Integrated a `mailhog` service to capture and test outbound emails (like activation and password resets) locally.
- **`backend.entrypoint.sh`**: Appended `--timeout 300` to the `gunicorn` command to prevent worker timeouts during extensive I/O or background processing handoffs.

## Technologies Used

- **Django 5.x** - Web framework
- **Django REST Framework** - REST API framework
- **Simple JWT** - JSON Web Token authentication
- **PostgreSQL** - Relational database
- **Redis & Django RQ** - Background task queueing
- **FFmpeg** - Video conversion and HLS segmentation
- **Docker / Podman** - Containerization
- **Mailhog** - Local email testing
