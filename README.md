# Happsay Backend

REST API for [Happsay](https://happsay.vercel.app), a to-do app for planning tasks with deadlines. It handles accounts, JWT authentication, password resets by email, and each user's task list.

The web client lives in [Happsay](https://github.com/Aguynamedkent7/Happsay).

## Tech stack

- Python 3.12, Django 5.1, Django REST Framework
- JWT auth with `djangorestframework-simplejwt` (refresh tokens are blacklisted on logout)
- PostgreSQL (hosted on Supabase) in production, any `DATABASE_URL` locally
- Deployed as a serverless function on Vercel, with WhiteNoise serving static files

## Getting started

### Prerequisites

- Python 3.12
- A database URL (PostgreSQL, or SQLite for local development)

### Setup

```bash
git clone https://github.com/seodowa/happsay-backend.git
cd happsay-backend
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Create a `.env` file in the project root (see [Configuration](#configuration)), then:

```bash
python manage.py migrate
python manage.py runserver 127.0.0.1:8000
```

The API is now available at `http://127.0.0.1:8000/`. Use `127.0.0.1` rather than `localhost`, since `localhost` is only allowed when `DEBUG=True`.

## Configuration

All settings come from environment variables (or `.env` outside Vercel).

| Variable | Required | Description |
|---|---|---|
| `DJANGO_SECRET_KEY` | Yes | Django secret key. |
| `DATABASE_URL` | Yes | Database connection string, e.g. `postgres://user:pass@host:5432/db` or `sqlite:////absolute/path/db.sqlite3`. |
| `EMAIL_USER` | Yes | Gmail address used to send password reset emails. |
| `EMAIL_PASSWORD` | Yes | App password for `EMAIL_USER`. |
| `DEBUG` | No | `True` for local development. Defaults to `False`. |

Example `.env` for local development:

```env
DJANGO_SECRET_KEY=change-me
DEBUG=True
DATABASE_URL=sqlite:////absolute/path/to/happsay-backend/db.sqlite3
EMAIL_USER=you@example.com
EMAIL_PASSWORD=your-app-password
```

Allowed CORS origins are set in `CORS_ALLOWED_ORIGINS` in `happsay_backend/settings.py`: the production frontend plus `localhost:5173` and `localhost:5175` for development.

## API reference

Authenticated endpoints expect an access token in the `Authorization: Bearer <access>` header. Access tokens last 5 minutes and refresh tokens 7 days.

| Method | Path | Auth | Description |
|---|---|---|---|
| `POST` | `/register/` | — | Create an account. |
| `POST` | `/login/` | — | Log in and receive access and refresh tokens. |
| `POST` | `/token/refresh/` | — | Exchange a refresh token for a new access token. |
| `POST` | `/logout/` | Bearer | Blacklist the refresh token. |
| `POST` | `/validate-token/` | — | Check whether a token is still valid. |
| `POST` | `/password-reset/` | — | Email a password reset link. |
| `POST` | `/reset-password/<token>/` | — | Set a new password using the emailed token. |
| `GET` | `/users/<id>/` | Bearer | Get a user's profile. |
| `PATCH` | `/users/<id>/` | Bearer | Update username, email or password. Blank username or password fields are left unchanged. |
| `GET` | `/todolist/` | Bearer | List the current user's tasks. Filter with `?is_done=true` or `?is_archived=true`. |
| `POST` | `/todolist/` | Bearer | Create a task. |
| `GET` / `PATCH` / `DELETE` | `/todolist/<id>/` | Bearer | Read, update or delete one task. |

### Register

```http
POST /register/
Content-Type: application/json

{ "username": "jane", "email": "jane@example.com", "password": "secret", "confirm_password": "secret" }
```

Returns `201 Created` with `{ "message": "User registered successfully!" }`, or `400` with field errors.

### Log in

```http
POST /login/
Content-Type: application/json

{ "username": "jane", "password": "secret" }
```

```json
{
  "user": { "id": 1, "username": "jane", "email": "jane@example.com" },
  "refresh": "<refresh token>",
  "access": "<access token>"
}
```

### Refresh and log out

```http
POST /token/refresh/
{ "refresh": "<refresh token>" }
```

```http
POST /logout/
Authorization: Bearer <access token>
{ "refresh_token": "<refresh token>" }
```

### Password reset

```http
POST /password-reset/
{ "email": "jane@example.com" }
```

The user receives a link to `https://happsay.vercel.app/reset-password/<token>`. The frontend then calls:

```http
POST /reset-password/<token>/
{ "password": "new-secret", "confirm_password": "new-secret" }
```

### Tasks

A task looks like this:

```json
{
  "id": 1,
  "title": "Submit lab report",
  "content": "Export the ERD as PDF",
  "is_done": false,
  "is_archived": false,
  "deadline": "2026-09-29"
}
```

`title`, `content` and `deadline` (`YYYY-MM-DD`) are required when creating a task. Use `PATCH /todolist/<id>/` with any subset of fields to update it, for example `{ "is_done": true }`.

## Project structure

```
happsay_backend/     Django project: settings, root URLs, WSGI
happsay_app/         Models, serializers and API views
vercel_wsgi.py       Vercel entry point
.github/workflows/   Scheduled ping that keeps the Supabase database active
```

## Deployment

The API deploys to Vercel from `main` using `vercel.json`, which routes every request to `vercel_wsgi.py`. Set the environment variables above in the Vercel project.

The production database is on Supabase's free tier, which pauses after a period of inactivity. The **Keep Supabase Alive** workflow pings it every Monday and Thursday; it needs the `SUPABASE_URL` and `SUPABASE_ANON_KEY` repository secrets. A `Procfile` is also included for Gunicorn-based hosts.

## License

[MIT](LICENSE)
