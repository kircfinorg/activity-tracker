# Setup Guide

This guide will help you set up the Gamified Activity & Reward Tracker development environment.

## Prerequisites

Before you begin, ensure you have the following installed:

- **Node.js** 18+ and npm (or yarn)
- **Python** 3.11+
- **Git**
- A **Firebase** project with:
  - Authentication enabled (Google OAuth provider)
  - Firestore database created
  - Service account key downloaded

## Quick Setup

Run the automated setup script:

```bash
chmod +x setup.sh
./setup.sh
```

This will:
1. Check for required dependencies
2. Set up the frontend with Next.js
3. Set up the backend with Python virtual environment
4. Install all dependencies

## Manual Setup

If you prefer to set up manually or the script doesn't work:

### Frontend Setup

1. Navigate to frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   # or
   yarn install
   ```

3. Create environment file:
   ```bash
   cp .env.local.example .env.local
   ```

4. Edit `.env.local` and add your Firebase configuration:
   ```env
   NEXT_PUBLIC_FIREBASE_API_KEY=your_api_key
   NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=your_project.firebaseapp.com
   NEXT_PUBLIC_FIREBASE_PROJECT_ID=your_project_id
   NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=your_project.appspot.com
   NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=your_sender_id
   NEXT_PUBLIC_FIREBASE_APP_ID=your_app_id
   NEXT_PUBLIC_API_URL=http://localhost:8000
   ```

### Backend Setup

1. Navigate to backend directory:
   ```bash
   cd backend
   ```

2. Create virtual environment:
   ```bash
   python3 -m venv venv
   ```

3. Activate virtual environment:
   ```bash
   # On macOS/Linux:
   source venv/bin/activate
   
   # On Windows:
   venv\Scripts\activate
   ```

4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

5. Create environment file:
   ```bash
   cp .env.example .env
   ```

6. Download your Firebase service account key:
   - Go to Firebase Console → Project Settings → Service Accounts
   - Click "Generate New Private Key"
   - Save the file as `serviceAccountKey.json` in the `backend/` directory

7. Edit `.env` and update configuration:
   ```env
   FIREBASE_CREDENTIALS_PATH=./serviceAccountKey.json
   FIREBASE_PROJECT_ID=your_project_id
   ALLOWED_ORIGINS=http://localhost:3000
   ```

## Firebase Configuration

### Enable Google Authentication

1. Go to Firebase Console → Authentication → Sign-in method
2. Enable Google provider
3. Add authorized domains (localhost for development)

### Set Up Firestore

1. Go to Firebase Console → Firestore Database
2. Create database in test mode (for development)
3. Create the following collections (they will be auto-created by the app):
   - `users`
   - `families`
   - `activities`
   - `logs`

### Security Rules (Optional for Development)

For development, you can use test mode. For production, implement proper security rules as specified in the design document.

## Running the Application

### Start the Backend

```bash
cd backend
source venv/bin/activate  # On Windows: venv\Scripts\activate
python main.py
```

The API will be available at: http://localhost:8000
API documentation: http://localhost:8000/docs

### Start the Frontend

In a new terminal:

```bash
cd frontend
npm run dev
# or
yarn dev
```

The application will be available at: http://localhost:3000

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
source venv/bin/activate
pytest
```

## Troubleshooting

### Node.js Not Found

Install Node.js from https://nodejs.org/ (LTS version recommended)

### Python Not Found

Install Python from https://www.python.org/ (version 3.11 or higher)

### Firebase Connection Issues

- Verify your service account key is in the correct location
- Check that your Firebase project ID is correct in `.env`
- Ensure Firestore is enabled in your Firebase project

### CORS Issues

- Verify `ALLOWED_ORIGINS` in backend `.env` includes your frontend URL
- Check that the backend is running before starting the frontend

### Port Already in Use

If port 3000 or 8000 is already in use:

**Frontend:**
```bash
PORT=3001 npm run dev
```

**Backend:**
Edit `backend/.env` and change `API_PORT=8001`

## Next Steps

After setup is complete:

1. Review the requirements document: `.kiro/specs/gamified-activity-tracker/requirements.md`
2. Review the design document: `.kiro/specs/gamified-activity-tracker/design.md`
3. Check the task list: `.kiro/specs/gamified-activity-tracker/tasks.md`
4. Start implementing features according to the task list

## Additional Resources

- [Next.js Documentation](https://nextjs.org/docs)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Firebase Documentation](https://firebase.google.com/docs)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)
