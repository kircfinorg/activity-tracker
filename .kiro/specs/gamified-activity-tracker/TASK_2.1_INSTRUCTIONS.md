# Task 2.1: Set up Firebase Project and Enable Google Authentication

## Overview
This task requires manual configuration in the Firebase Console. Follow these steps to complete the setup.

## Prerequisites
- Google account
- Access to [Firebase Console](https://console.firebase.google.com/)

## Steps to Complete

### 1. Create Firebase Project (5 minutes)

1. Navigate to [Firebase Console](https://console.firebase.google.com/)
2. Click **"Add project"** or **"Create a project"**
3. Enter project name: `gamified-activity-tracker` (or your preferred name)
4. (Optional) Enable/disable Google Analytics based on your preference
5. Click **"Create project"** and wait for setup to complete
6. Click **"Continue"** when the project is ready

### 2. Enable Google OAuth Provider (3 minutes)

1. In your Firebase project dashboard, click **"Authentication"** in the left sidebar
2. Click **"Get started"** (if this is your first time using Authentication)
3. Navigate to the **"Sign-in method"** tab at the top
4. In the list of providers, find and click on **"Google"**
5. Toggle the **"Enable"** switch to **ON**
6. Set the **"Project support email"** (required) - use your email address
7. Click **"Save"**

✅ **Verification**: You should see "Google" listed as "Enabled" in the Sign-in method tab

### 3. Configure Authorized Domains (2 minutes)

1. Still in **Authentication**, click on the **"Settings"** tab
2. Scroll down to the **"Authorized domains"** section
3. Verify that `localhost` is already in the list (it should be by default)
4. For production deployment (later), you'll add your production domain here

✅ **Verification**: `localhost` should be listed in Authorized domains

### 4. Get Firebase Web App Configuration (5 minutes)

1. Click the **gear icon** (⚙️) next to "Project Overview" in the left sidebar
2. Select **"Project settings"**
3. Scroll down to **"Your apps"** section
4. Click the **Web icon** (`</>`) to add a web app
5. Enter app nickname: `gamified-activity-tracker-web`
6. (Optional) Check "Also set up Firebase Hosting" if desired
7. Click **"Register app"**
8. **Copy the `firebaseConfig` object** - you'll need these values next

### 5. Configure Frontend Environment Variables (3 minutes)

1. Open your terminal and navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Copy the example environment file:
   ```bash
   cp .env.local.example .env.local
   ```

3. Open `.env.local` and fill in the values from the Firebase config you copied:
   ```env
   NEXT_PUBLIC_FIREBASE_API_KEY=your_api_key_here
   NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=your_project_id.firebaseapp.com
   NEXT_PUBLIC_FIREBASE_PROJECT_ID=your_project_id
   NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=your_project_id.appspot.com
   NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=your_sender_id
   NEXT_PUBLIC_FIREBASE_APP_ID=your_app_id
   NEXT_PUBLIC_API_URL=http://localhost:8000
   ```

✅ **Verification**: `.env.local` file exists in `frontend/` with all values filled in

### 6. Set Up Firebase Admin SDK for Backend (5 minutes)

1. In Firebase Console, go to **Project Settings** (gear icon)
2. Click on the **"Service accounts"** tab
3. Click **"Generate new private key"** button
4. Click **"Generate key"** in the confirmation dialog
5. A JSON file will download - **keep this file secure!**
6. Move the downloaded file to your backend directory and rename it:
   ```bash
   mv ~/Downloads/gamified-activity-tracker-*.json backend/serviceAccountKey.json
   ```

7. Create backend environment file:
   ```bash
   cd backend
   cp .env.example .env
   ```

8. Open `backend/.env` and update with your project ID:
   ```env
   FIREBASE_CREDENTIALS_PATH=./serviceAccountKey.json
   FIREBASE_PROJECT_ID=your_project_id_here
   ALLOWED_ORIGINS=http://localhost:3000
   API_HOST=0.0.0.0
   API_PORT=8000
   ENVIRONMENT=development
   ```

✅ **Verification**: 
- `serviceAccountKey.json` exists in `backend/`
- `.env` file exists in `backend/` with correct project ID

### 7. Set Up Firestore Database (3 minutes)

1. In Firebase Console, click **"Firestore Database"** in the left sidebar
2. Click **"Create database"**
3. Select **"Start in production mode"** (we'll add security rules later)
4. Choose a Cloud Firestore location (select one closest to your users)
5. Click **"Enable"** and wait for the database to be created

✅ **Verification**: Firestore Database is created and shows an empty database

## Security Checklist

Before proceeding, verify:

- [ ] `serviceAccountKey.json` is listed in `backend/.gitignore`
- [ ] `.env` is listed in `backend/.gitignore`
- [ ] `.env.local` is listed in `frontend/.gitignore`
- [ ] You have NOT committed any credentials to version control

## Task Completion Checklist

Mark this task as complete when:

- [x] Firebase project is created
- [x] Google OAuth provider is enabled in Authentication
- [x] `localhost` is in Authorized domains
- [x] Frontend `.env.local` file is configured with Firebase credentials
- [x] Backend `.env` file is configured with project ID
- [x] Backend `serviceAccountKey.json` file exists
- [x] Firestore Database is created

## Next Steps

After completing this task:
- Task 2.2: Implement Firebase configuration in frontend ✓ (config files ready)
- Task 2.3: Implement Firebase Admin SDK in backend ✓ (credentials ready)
- Task 2.4: Write property test for authentication token validation

## Troubleshooting

**Issue**: Can't find "Add project" button
- **Solution**: Make sure you're signed in to Firebase Console with your Google account

**Issue**: Google provider not showing in Sign-in methods
- **Solution**: Make sure you clicked "Get started" in the Authentication section first

**Issue**: Downloaded service account key has a long filename
- **Solution**: That's normal - just rename it to `serviceAccountKey.json` when moving it

## Need Help?

Refer to the comprehensive guide in `FIREBASE_SETUP.md` for more detailed instructions and troubleshooting.

---

**Estimated Time**: 20-25 minutes
**Difficulty**: Easy (mostly point-and-click in Firebase Console)
