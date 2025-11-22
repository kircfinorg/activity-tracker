# Backend Setup and Configuration

This is the backend service for the Gamified Activity & Reward Tracker application, built with FastAPI and Firebase.

## Prerequisites

- Python 3.11+ (tested with Python 3.13)
- Firebase project with Firestore and Authentication enabled
- Firebase service account key (JSON file)

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables:
```bash
cp .env.example .env
```

3. Edit `.env` and configure:
```env
FIREBASE_CREDENTIALS_PATH=./serviceAccountKey.json
FIREBASE_PROJECT_ID=your_project_id
ALLOWED_ORIGINS=http://localhost:3000
API_HOST=0.0.0.0
API_PORT=8000
ENVIRONMENT=development
```

4. Place your Firebase service account key in the backend directory as `serviceAccountKey.json`

## Running the Server

### Development Mode
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Production Mode
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

## API Documentation

Once the server is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Testing

Run all tests:
```bash
pytest
```

Run with coverage:
```bash
pytest --cov=. --cov-report=html
```

Run specific test file:
```bash
pytest tests/test_auth_middleware.py -v
```

**Note**: Tests require Firebase credentials or will use mocked Firebase services.

## Project Structure

```
backend/
├── main.py                 # FastAPI application entry point
├── config.py              # Configuration settings
├── requirements.txt       # Python dependencies
├── middleware/
│   ├── __init__.py
│   └── auth.py           # Authentication middleware
├── services/
│   ├── __init__.py
│   └── firebase_service.py  # Firebase Admin SDK wrapper
├── models/               # Pydantic data models
├── routers/             # API route handlers
└── tests/               # Unit and integration tests
```

## Authentication Flow

1. **Token Verification**: All protected endpoints require a valid Firebase ID token in the `Authorization` header as `Bearer <token>`

2. **Role-Based Access Control**: Endpoints can require specific roles (parent/child) using the `require_parent` or `require_child` dependencies

3. **Family Membership**: The service verifies users can only access data from their own family group

## Key Features Implemented

### Authentication Middleware (`middleware/auth.py`)

- `verify_token()`: Validates Firebase ID tokens
- `get_current_user()`: Extracts user info from token
- `require_role()`: Enforces role-based access control
- `require_parent()`: Dependency for parent-only endpoints
- `require_child()`: Dependency for child-only endpoints

### Firebase Service (`services/firebase_service.py`)

- Singleton pattern for Firebase Admin SDK
- Automatic initialization with service account or default credentials
- Firestore database access
- Firebase Authentication access
- Family membership verification helper

## Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `FIREBASE_CREDENTIALS_PATH` | Path to service account JSON | Yes* | None |
| `FIREBASE_PROJECT_ID` | Firebase project ID | Yes | None |
| `ALLOWED_ORIGINS` | CORS allowed origins (comma-separated) | No | http://localhost:3000 |
| `API_HOST` | Server host | No | 0.0.0.0 |
| `API_PORT` | Server port | No | 8000 |
| `ENVIRONMENT` | Environment (development/production) | No | development |

*Not required if using default credentials (e.g., on Cloud Run)

## Security Considerations

- Never commit `serviceAccountKey.json` to version control
- Never commit `.env` files with real credentials
- Use environment variables or secret management in production
- The `.gitignore` file excludes these sensitive files

## Logging

The application uses Python's built-in logging module:
- INFO level: Normal operations, successful authentications
- WARNING level: Invalid tokens, authorization failures
- ERROR level: System errors, Firebase connection issues

Logs include:
- Timestamp
- Logger name
- Log level
- Message

## Health Check

The `/health` endpoint provides service status:
```bash
curl http://localhost:8000/health
```

Response:
```json
{
  "status": "healthy",
  "firebase": "connected"
}
```

## Troubleshooting

### "Failed to initialize Firebase"
- Check that `FIREBASE_CREDENTIALS_PATH` points to a valid service account key
- Verify the JSON file is not corrupted
- Ensure the service account has necessary permissions

### "Invalid authentication token"
- Token may be expired (tokens expire after 1 hour)
- Token may be from wrong Firebase project
- Check that frontend is using correct Firebase config

### "This action requires 'parent' role"
- User doesn't have the required role in Firestore
- Check user document in `users` collection has correct `role` field

### CORS errors
- Add your frontend URL to `ALLOWED_ORIGINS` in `.env`
- Restart the server after changing environment variables

## Next Steps

After completing this setup:
1. Implement API endpoints in `routers/` directory
2. Create Pydantic models in `models/` directory
3. Write tests for new endpoints
4. Deploy to production environment
