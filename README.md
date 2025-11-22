# Gamified Activity & Reward Tracker

A full-stack web application that enables families to track children's productivity and habits by assigning monetary value to specific units of work.

## Project Structure

```
.
├── frontend/          # Next.js React application
│   ├── app/          # Next.js app directory
│   ├── components/   # React components (to be created)
│   ├── lib/          # Utility libraries and Firebase config
│   └── package.json  # Frontend dependencies
│
├── backend/          # Python FastAPI application
│   ├── models/       # Pydantic data models
│   ├── services/     # Business logic services
│   ├── middleware/   # Authentication and authorization
│   ├── routers/      # API route handlers (to be created)
│   ├── tests/        # Test files
│   └── main.py       # FastAPI application entry point
│
└── .kiro/            # Kiro specs and documentation
    └── specs/
        └── gamified-activity-tracker/
            ├── requirements.md
            ├── design.md
            └── tasks.md
```

## Technology Stack

### Frontend
- **Framework**: Next.js 14+ with React 18+
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Icons**: Lucide-React
- **Authentication**: Firebase Authentication
- **Database**: Firebase Firestore
- **Testing**: Jest, React Testing Library, fast-check (property-based testing)

### Backend
- **Framework**: FastAPI
- **Language**: Python 3.11+
- **Authentication**: Firebase Admin SDK
- **Database**: Firebase Firestore
- **Validation**: Pydantic
- **Testing**: pytest, Hypothesis (property-based testing)
- **Server**: Uvicorn

## Setup Instructions

### Prerequisites
- Node.js 18+ and npm/yarn
- Python 3.11+
- Firebase project with Authentication and Firestore enabled

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   # or
   yarn install
   ```

3. Create `.env.local` file from the example:
   ```bash
   cp .env.local.example .env.local
   ```

4. Update `.env.local` with your Firebase configuration

5. Run the development server:
   ```bash
   npm run dev
   # or
   yarn dev
   ```

6. Open [http://localhost:3000](http://localhost:3000) in your browser

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create `.env` file from the example:
   ```bash
   cp .env.example .env
   ```

5. Download your Firebase service account key and save it as `serviceAccountKey.json` in the backend directory

6. Update `.env` with your configuration

7. Run the development server:
   ```bash
   python main.py
   # or
   uvicorn main:app --reload
   ```

8. API will be available at [http://localhost:8000](http://localhost:8000)
9. API documentation at [http://localhost:8000/docs](http://localhost:8000/docs)

## Testing

### Frontend Tests
```bash
cd frontend
npm test
# or
yarn test
```

### Backend Tests
```bash
cd backend
pytest
```

## Features

- **User Authentication**: Google OAuth sign-in with role selection (parent/child)
- **Family Groups**: Create and join families using invite codes
- **Activity Management**: Parents create activities with custom rates
- **Activity Logging**: Children log completed activities
- **Verification System**: Parents verify children's logged activities
- **Earnings Dashboard**: Track daily and weekly earnings
- **Theme System**: Three visual themes (Hacker Terminal, Soft Serenity, Deep Ocean)
- **Responsive Design**: Mobile-first design optimized for all devices
- **Real-time Updates**: Live synchronization across devices

## Development Status

This project is currently in development. See `.kiro/specs/gamified-activity-tracker/tasks.md` for the implementation plan.

## License

Private project - All rights reserved
