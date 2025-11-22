# Project Structure

This document provides an overview of the project structure created for the Gamified Activity & Reward Tracker.

## Directory Structure

```
activity-tracker/
├── frontend/                    # Next.js React application
│   ├── app/                    # Next.js app directory
│   │   ├── globals.css        # Global styles with Tailwind
│   │   ├── layout.tsx         # Root layout component
│   │   └── page.tsx           # Home page
│   ├── lib/                   # Utility libraries
│   │   ├── api.ts            # API client for backend communication
│   │   └── firebase.ts       # Firebase configuration and initialization
│   ├── types/                 # TypeScript type definitions
│   │   └── index.ts          # Shared types (User, Activity, LogEntry, etc.)
│   ├── .env.local.example    # Environment variables template
│   ├── .eslintrc.json        # ESLint configuration
│   ├── .gitignore            # Git ignore rules for frontend
│   ├── jest.config.js        # Jest testing configuration
│   ├── jest.setup.js         # Jest setup file
│   ├── next.config.js        # Next.js configuration
│   ├── package.json          # Frontend dependencies
│   ├── postcss.config.js     # PostCSS configuration
│   ├── tailwind.config.ts    # Tailwind CSS configuration with theme colors
│   └── tsconfig.json         # TypeScript configuration
│
├── backend/                    # Python FastAPI application
│   ├── middleware/            # Authentication and authorization
│   │   ├── __init__.py
│   │   └── auth.py           # Firebase token verification
│   ├── models/                # Pydantic data models
│   │   ├── __init__.py
│   │   ├── activity.py       # Activity model
│   │   ├── earnings.py       # Earnings model
│   │   ├── family.py         # Family model
│   │   ├── log_entry.py      # LogEntry model
│   │   └── user.py           # User model
│   ├── routers/               # API route handlers (to be implemented)
│   │   └── __init__.py
│   ├── services/              # Business logic services
│   │   ├── __init__.py
│   │   └── firebase_service.py  # Firebase Admin SDK wrapper
│   ├── tests/                 # Test files
│   │   └── __init__.py
│   ├── .env.example          # Environment variables template
│   ├── .gitignore            # Git ignore rules for backend
│   ├── config.py             # Application configuration
│   ├── main.py               # FastAPI application entry point
│   ├── pytest.ini            # Pytest configuration
│   └── requirements.txt      # Python dependencies
│
├── .kiro/                     # Kiro specs and documentation
│   └── specs/
│       └── gamified-activity-tracker/
│           ├── design.md     # Design document
│           ├── requirements.md  # Requirements document
│           └── tasks.md      # Implementation task list
│
├── .gitignore                 # Root git ignore rules
├── README.md                  # Project overview and quick start
├── SETUP.md                   # Detailed setup instructions
├── PROJECT_STRUCTURE.md       # This file
└── setup.sh                   # Automated setup script
```

## Key Files and Their Purpose

### Frontend

- **app/layout.tsx**: Root layout component that wraps all pages
- **app/page.tsx**: Home page component
- **lib/firebase.ts**: Firebase initialization and exports auth/db instances
- **lib/api.ts**: API client with methods for GET, POST, PATCH, DELETE requests
- **types/index.ts**: TypeScript interfaces for User, Activity, LogEntry, Family, Earnings
- **tailwind.config.ts**: Tailwind configuration with custom theme colors for three themes

### Backend

- **main.py**: FastAPI application with CORS middleware and basic routes
- **config.py**: Pydantic settings for environment configuration
- **models/**: Pydantic models matching the design document specifications
- **services/firebase_service.py**: Singleton service for Firebase Admin SDK
- **middleware/auth.py**: JWT token verification middleware

## Dependencies

### Frontend Dependencies

**Core:**
- next: ^14.2.0
- react: ^18.3.0
- react-dom: ^18.3.0
- firebase: ^10.12.0
- lucide-react: ^0.400.0

**Dev Dependencies:**
- typescript: ^5.4.0
- tailwindcss: ^3.4.0
- @testing-library/react: ^15.0.0
- jest: ^29.7.0
- fast-check: ^3.19.0 (property-based testing)

### Backend Dependencies

- fastapi: 0.111.0
- uvicorn[standard]: 0.30.0
- firebase-admin: 6.5.0
- pydantic: 2.7.0
- pytest: 8.2.0
- hypothesis: 6.102.0 (property-based testing)

## Configuration Files

### Frontend Environment Variables (.env.local)

```
NEXT_PUBLIC_FIREBASE_API_KEY=
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=
NEXT_PUBLIC_FIREBASE_PROJECT_ID=
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=
NEXT_PUBLIC_FIREBASE_APP_ID=
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Backend Environment Variables (.env)

```
FIREBASE_CREDENTIALS_PATH=./serviceAccountKey.json
FIREBASE_PROJECT_ID=
ALLOWED_ORIGINS=http://localhost:3000
API_HOST=0.0.0.0
API_PORT=8000
ENVIRONMENT=development
```

## Next Steps

1. Install dependencies (run `./setup.sh` or follow SETUP.md)
2. Configure Firebase project
3. Update environment variables
4. Start implementing features from `.kiro/specs/gamified-activity-tracker/tasks.md`

## Testing Strategy

- **Frontend**: Jest + React Testing Library + fast-check for property-based tests
- **Backend**: pytest + Hypothesis for property-based tests
- Minimum 100 iterations per property test
- Each property test tagged with feature name and property number

## Architecture Notes

- **Frontend**: React with Next.js App Router, TypeScript, Tailwind CSS
- **Backend**: Python FastAPI with async/await support
- **Database**: Firebase Firestore (NoSQL)
- **Authentication**: Firebase Authentication with Google OAuth
- **Real-time**: Firebase listeners for live updates
- **API**: RESTful API with JWT token authentication
