# Firebase Setup Guide

This guide walks you through setting up Firebase for the Gamified Activity & Reward Tracker application.

## Prerequisites

- Google account
- Access to [Firebase Console](https://console.firebase.google.com/)

## Step 1: Create Firebase Project

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Click "Add project" or "Create a project"
3. Enter project name: `gamified-activity-tracker` (or your preferred name)
4. (Optional) Enable Google Analytics if desired
5. Click "Create project" and wait for setup to complete

## Step 2: Enable Google Authentication

1. In your Firebase project, navigate to **Authentication** in the left sidebar
2. Click "Get started" if this is your first time
3. Go to the **Sign-in method** tab
4. Find **Google** in the list of providers
5. Click on **Google** to configure it
6. Toggle the **Enable** switch to ON
7. Set the **Project support email** (required) - use your email address
8. Click **Save**

## Step 3: Configure Authorized Domains

1. Still in **Authentication** → **Settings** tab
2. Scroll down to **Authorized domains**
3. By default, `localhost` should already be authorized for development
4. When deploying to production, add your production domain(s):
   - Click "Add domain"
   - Enter your domain (e.g., `your-app.vercel.app`)
   - Click "Add"

## Step 4: Get Firebase Configuration for Frontend

1. Go to **Project Settings** (gear icon in left sidebar)
2. Scroll down to "Your apps" section
3. Click the **Web** icon (`</>`) to add a web app
4. Register app with nickname: `gamified-activity-tracker-web`
5. (Optional) Check "Also set up Firebase Hosting" if you plan to use it
6. Click "Register app"
7. Copy the `firebaseConfig` object values
8. Create a `.env.local` file in the `frontend` directory:

```bash
cd frontend
cp .env.local.example .env.local
```

9. Fill in the values from the Firebase config:

```env
NEXT_PUBLIC_FIREBASE_API_KEY=your_api_key_here
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=your_project_id.firebaseapp.com
NEXT_PUBLIC_FIREBASE_PROJECT_ID=your_project_id
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=your_project_id.appspot.com
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=your_sender_id
NEXT_PUBLIC_FIREBASE_APP_ID=your_app_id
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Step 5: Set Up Firebase Admin SDK for Backend

1. In **Project Settings**, go to the **Service accounts** tab
2. Click "Generate new private key"
3. Click "Generate key" in the confirmation dialog
4. A JSON file will be downloaded - this is your service account key
5. **IMPORTANT**: Keep this file secure and never commit it to version control
6. Move the downloaded file to your backend directory:

```bash
mv ~/Downloads/your-project-firebase-adminsdk-xxxxx.json backend/serviceAccountKey.json
```

7. Create a `.env` file in the `backend` directory:

```bash
cd backend
cp .env.example .env
```

8. Update the `.env` file:

```env
FIREBASE_CREDENTIALS_PATH=./serviceAccountKey.json
FIREBASE_PROJECT_ID=your_project_id
ALLOWED_ORIGINS=http://localhost:3000
API_HOST=0.0.0.0
API_PORT=8000
ENVIRONMENT=development
```

## Step 6: Set Up Firestore Database

1. In Firebase Console, navigate to **Firestore Database** in the left sidebar
2. Click "Create database"
3. Choose **Start in production mode** (we'll add security rules later)
4. Select a Cloud Firestore location (choose one close to your users)
5. Click "Enable"

## Step 7: Create Firestore Indexes

1. In **Firestore Database**, go to the **Indexes** tab
2. Click "Create index" and add the following composite index:
   - Collection ID: `logs`
   - Fields to index:
     - `familyId` (Ascending)
     - `verificationStatus` (Ascending)
     - `timestamp` (Descending)
   - Query scope: Collection
3. Click "Create"

## Step 8: Set Up Firebase Security Rules (Optional - for later)

The security rules will be implemented in a later task, but you can prepare by:

1. Going to **Firestore Database** → **Rules** tab
2. Keeping the default rules for now (we'll update them later)

## Verification

To verify your setup is correct:

1. Check that `.env.local` exists in `frontend/` with all Firebase config values
2. Check that `.env` exists in `backend/` with credentials path and project ID
3. Check that `serviceAccountKey.json` exists in `backend/` (and is in `.gitignore`)
4. Verify that Google sign-in is enabled in Firebase Console → Authentication

## Security Notes

- **Never commit** `serviceAccountKey.json` to version control
- **Never commit** `.env` or `.env.local` files with real credentials
- The `.gitignore` file should already exclude these files
- For production, use environment variables or secret management services

## Next Steps

After completing this setup:
1. The frontend Firebase configuration is ready (subtask 2.2 ✓)
2. The backend Firebase Admin SDK is ready (subtask 2.3 ✓)
3. You can proceed with implementing authentication flows

## Troubleshooting

**Issue**: "Firebase: Error (auth/unauthorized-domain)"
- **Solution**: Add your domain to Authorized domains in Firebase Console → Authentication → Settings

**Issue**: "Could not load the default credentials"
- **Solution**: Verify `FIREBASE_CREDENTIALS_PATH` in `.env` points to the correct service account key file

**Issue**: "Permission denied" errors in Firestore
- **Solution**: Check Firebase Security Rules and ensure they allow the operations you're attempting
