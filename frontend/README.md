# Frontend Setup and Configuration

This is the frontend application for the Gamified Activity & Reward Tracker, built with Next.js, React, TypeScript, and Firebase.

## Prerequisites

- Node.js 18+ and npm/yarn
- Firebase project with Authentication enabled
- Backend API running (see backend/README.md)

## Installation

1. Install dependencies:
```bash
npm install
# or
yarn install
```

2. Set up environment variables:
```bash
cp .env.local.example .env.local
```

3. Edit `.env.local` and configure with your Firebase project settings:
```env
NEXT_PUBLIC_FIREBASE_API_KEY=your_api_key_here
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=your_project_id.firebaseapp.com
NEXT_PUBLIC_FIREBASE_PROJECT_ID=your_project_id
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=your_project_id.appspot.com
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=your_sender_id
NEXT_PUBLIC_FIREBASE_APP_ID=your_app_id
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Running the Application

### Development Mode
```bash
npm run dev
# or
yarn dev
```

Visit http://localhost:3000

### Production Build
```bash
npm run build
npm run start
# or
yarn build
yarn start
```

## Testing

Run all tests:
```bash
npm test
# or
yarn test
```

Run tests in watch mode:
```bash
npm run test:watch
# or
yarn test:watch
```

## Project Structure

```
frontend/
├── app/                    # Next.js app directory
│   ├── layout.tsx         # Root layout
│   ├── page.tsx           # Home page
│   └── globals.css        # Global styles
├── lib/                   # Utility libraries
│   ├── firebase.ts        # Firebase configuration
│   ├── auth.ts           # Authentication helpers
│   └── api.ts            # API client
├── types/                # TypeScript type definitions
│   └── index.ts
├── components/           # React components (to be created)
└── public/              # Static assets
```

## Firebase Configuration

### Firebase Setup (`lib/firebase.ts`)

The Firebase configuration includes:
- Firebase app initialization
- Authentication service
- Firestore database
- Google OAuth provider

Features:
- Environment variable validation
- Error handling for initialization failures
- Singleton pattern to prevent multiple initializations
- Google sign-in configured with account selection prompt

### Authentication Helpers (`lib/auth.ts`)

Available functions:

#### `signInWithGoogle()`
Initiates Google OAuth sign-in flow
```typescript
import { signInWithGoogle } from '@/lib/auth';

try {
  const result = await signInWithGoogle();
  console.log('Signed in:', result.user);
} catch (error) {
  console.error('Sign in failed:', error);
}
```

#### `signOut()`
Signs out the current user
```typescript
import { signOut } from '@/lib/auth';

await signOut();
```

#### `getIdToken(forceRefresh?)`
Gets the current user's ID token for API requests
```typescript
import { getIdToken } from '@/lib/auth';

const token = await getIdToken();
// Use token in API requests
```

#### `onAuthChange(callback)`
Subscribe to authentication state changes
```typescript
import { onAuthChange } from '@/lib/auth';

const unsubscribe = onAuthChange((user) => {
  if (user) {
    console.log('User signed in:', user);
  } else {
    console.log('User signed out');
  }
});

// Later: unsubscribe()
```

#### `getCurrentUser()`
Get the current authenticated user synchronously
```typescript
import { getCurrentUser } from '@/lib/auth';

const user = getCurrentUser();
```

## API Client

### Making Authenticated Requests (`lib/api.ts`)

The API client handles communication with the backend:

```typescript
import { apiClient } from '@/lib/api';
import { getIdToken } from '@/lib/auth';

// GET request
const token = await getIdToken();
const data = await apiClient.get('/api/activities/family-123', token);

// POST request
const newActivity = await apiClient.post(
  '/api/activities',
  { name: 'Reading', unit: 'Pages', rate: 0.10 },
  token
);

// PATCH request
const updated = await apiClient.patch(
  '/api/logs/log-123/verify',
  { status: 'approved' },
  token
);

// DELETE request
await apiClient.delete('/api/activities/activity-123', token);
```

Features:
- Automatic error handling with user-friendly messages
- 401 → "Authentication required"
- 403 → "Permission denied"
- 404 → "Resource not found"
- 500+ → "Server error"
- Network errors → "Network error"

## TypeScript Types

Define your types in `types/index.ts`:

```typescript
export interface User {
  uid: string;
  email: string;
  displayName: string;
  photoURL: string;
  role: 'parent' | 'child';
  familyId: string | null;
  theme: string;
}

export interface Activity {
  id: string;
  familyId: string;
  name: string;
  unit: string;
  rate: number;
  createdBy: string;
  createdAt: Date;
}

// Add more types as needed
```

## Styling

The project uses:
- **Tailwind CSS** for utility-first styling
- **CSS Modules** for component-specific styles (optional)
- **Global styles** in `app/globals.css`

## Environment Variables

All Firebase configuration must be prefixed with `NEXT_PUBLIC_` to be accessible in the browser.

| Variable | Description | Required |
|----------|-------------|----------|
| `NEXT_PUBLIC_FIREBASE_API_KEY` | Firebase API key | Yes |
| `NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN` | Firebase auth domain | Yes |
| `NEXT_PUBLIC_FIREBASE_PROJECT_ID` | Firebase project ID | Yes |
| `NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET` | Firebase storage bucket | Yes |
| `NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID` | Firebase messaging sender ID | Yes |
| `NEXT_PUBLIC_FIREBASE_APP_ID` | Firebase app ID | Yes |
| `NEXT_PUBLIC_API_URL` | Backend API URL | Yes |

## Security Considerations

- Never commit `.env.local` to version control
- Firebase config values are public (they're in the browser)
- Security is enforced by Firebase Security Rules and backend authentication
- Always validate user permissions on the backend

## Common Issues

### "Missing required Firebase environment variables"
- Check that all `NEXT_PUBLIC_FIREBASE_*` variables are set in `.env.local`
- Restart the dev server after changing environment variables

### "Failed to initialize Firebase"
- Verify Firebase config values are correct
- Check Firebase console for project settings

### "Network error" when calling API
- Ensure backend server is running
- Check `NEXT_PUBLIC_API_URL` points to correct backend URL
- Verify CORS is configured correctly in backend

### Authentication popup blocked
- Browser may be blocking popups
- User needs to allow popups for the site

## Development Workflow

1. Start backend server (see backend/README.md)
2. Start frontend dev server: `npm run dev`
3. Open http://localhost:3000
4. Make changes - hot reload is enabled
5. Run tests before committing

## Testing Strategy

- **Unit tests**: Test individual components and functions
- **Integration tests**: Test component interactions
- **Property-based tests**: Use fast-check for property testing (configured)

Example test structure:
```typescript
import { render, screen } from '@testing-library/react';
import { signInWithGoogle } from '@/lib/auth';

describe('Authentication', () => {
  it('should sign in with Google', async () => {
    // Test implementation
  });
});
```

## Next Steps

After completing this setup:
1. Create UI components in `components/` directory
2. Implement authentication flow
3. Build dashboard views
4. Add activity management features
5. Implement real-time updates with Firestore listeners
