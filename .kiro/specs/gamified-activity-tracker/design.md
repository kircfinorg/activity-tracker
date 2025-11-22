# Design Document

## Overview

The Gamified Activity & Reward Tracker is a full-stack web application built with React (Next.js), Python (FastAPI), and Firebase. The system enables families to track children's productivity through a parent-child verification workflow where children log activities and parents approve them for reward calculation.

The architecture follows a three-tier model:
- **Frontend**: React with Next.js, Tailwind CSS, and Lucide-React icons
- **Backend**: Python FastAPI service handling business logic and Firebase operations
- **Database**: Firebase Firestore for data persistence and Firebase Authentication for user management

Key design principles:
- Role-based access control (parent vs child permissions)
- Real-time data synchronization using Firebase listeners
- Mobile-first responsive design
- Secure authentication via Google OAuth
- Family-based data isolation

## Architecture

### System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                         Client Layer                         │
│  ┌────────────────────────────────────────────────────────┐ │
│  │         React/Next.js Application (Frontend)           │ │
│  │  - Authentication UI                                   │ │
│  │  - Dashboard Components                                │ │
│  │  - Activity Management                                 │ │
│  │  - Theme System                                        │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ HTTPS/REST API
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                      Application Layer                       │
│  ┌────────────────────────────────────────────────────────┐ │
│  │         Python FastAPI Backend Service                 │ │
│  │  - Authentication Middleware                           │ │
│  │  - Role-Based Access Control                           │ │
│  │  - Business Logic                                      │ │
│  │  - Data Validation                                     │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ Firebase SDK
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                        Data Layer                            │
│  ┌──────────────────────┐    ┌──────────────────────────┐  │
│  │  Firebase Auth       │    │  Firebase Firestore      │  │
│  │  - Google OAuth      │    │  - Users Collection      │  │
│  │  - User Sessions     │    │  - Families Collection   │  │
│  │  - Token Management  │    │  - Activities Collection │  │
│  └──────────────────────┘    │  - Logs Collection       │  │
│                               └──────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### Technology Stack

**Frontend:**
- React 18+ with functional components and hooks
- Next.js 14+ for server-side rendering and routing
- Tailwind CSS for styling
- Lucide-React for icons
- Firebase JavaScript SDK for real-time listeners

**Backend:**
- Python 3.11+
- FastAPI for REST API framework
- Firebase Admin SDK for server-side Firebase operations
- Pydantic for data validation
- Uvicorn as ASGI server

**Database & Authentication:**
- Firebase Authentication with Google OAuth provider
- Cloud Firestore for NoSQL data storage
- Firebase Security Rules for data access control

**Deployment:**
- Frontend: Vercel or Firebase Hosting
- Backend: Cloud Run, Railway, or similar Python hosting
- Environment variables for Firebase configuration

## Components and Interfaces

### Frontend Components

#### 1. Authentication Components

**GoogleSignInButton**
- Initiates Google OAuth flow
- Displays loading state during authentication
- Props: `onSuccess`, `onError`

**RoleSelectionModal**
- Shown to first-time users after Google sign-in
- Allows selection between "Parent" and "Child" roles
- Props: `onRoleSelect`, `isOpen`

**AccountSettings**
- Displays user profile information
- Provides sign-out functionality
- Includes account deletion option with confirmation
- Props: `user`, `onSignOut`, `onDeleteAccount`

#### 2. Family Group Components

**CreateFamilyForm**
- Form for parents to create a new family group
- Displays generated invite code after creation
- Props: `onFamilyCreated`

**JoinFamilyForm**
- Input field for entering invite code
- Validates code and joins family
- Props: `onFamilyJoined`, `onError`

**FamilyMembersList**
- Displays all members in the family group
- Shows role badges (Parent/Child)
- Props: `familyId`

#### 3. Activity Components

**CreateActivityForm** (Parent only)
- Form with fields: name, unit, rate
- Validates inputs before submission
- Props: `familyId`, `onActivityCreated`

**ActivityCard**
- Displays activity information (name, unit, rate)
- Shows earnings (pending/verified for children, total for parents)
- Increment button for children
- Delete button for parents
- Props: `activity`, `userRole`, `onIncrement`, `onDelete`

**ActivityGrid**
- Grid layout of activity cards
- Responsive design (single column on mobile)
- Props: `activities`, `userRole`

#### 4. Dashboard Components

**EarningsSummaryCard**
- Displays today's earnings and weekly earnings
- Shows pending vs verified amounts for children
- Props: `todayEarnings`, `weeklyEarnings`, `isPending`

**ParentDashboard**
- Overview of all children's activities
- Pending verification count
- Navigation to verification interface
- Props: `familyId`

**ChildDashboard**
- Activity grid for logging
- Earnings summaries
- Pending verification status
- Props: `userId`, `familyId`

#### 5. Verification Components

**VerificationQueue** (Parent only)
- List of pending log entries grouped by child
- Shows activity name, units, timestamp, child name
- Approve/Reject buttons for each entry
- Props: `familyId`, `onVerify`

**VerificationItem**
- Single log entry awaiting verification
- Displays all relevant information
- Action buttons
- Props: `logEntry`, `onApprove`, `onReject`

#### 6. Theme Components

**ThemeSelector**
- Dropdown or button group for theme selection
- Three options: Hacker Terminal, Soft Serenity, Deep Ocean
- Props: `currentTheme`, `onThemeChange`

**ThemeProvider**
- Context provider for theme state
- Applies theme classes to root element
- Persists theme to Firebase
- Props: `children`

### Backend API Endpoints

#### Authentication Endpoints

```python
POST /api/auth/verify-token
# Verifies Firebase ID token and returns user data
Request: { "idToken": string }
Response: { "uid": string, "email": string, "role": string }

POST /api/auth/set-role
# Sets role for first-time user
Request: { "idToken": string, "role": "parent" | "child" }
Response: { "success": boolean, "user": User }

DELETE /api/auth/delete-account
# Deletes user account and handles family group cleanup
Request: { "idToken": string }
Response: { "success": boolean }
```

#### Family Group Endpoints

```python
POST /api/families
# Creates a new family group (parent only)
Request: { "idToken": string }
Response: { "familyId": string, "inviteCode": string }

POST /api/families/join
# Joins existing family using invite code
Request: { "idToken": string, "inviteCode": string }
Response: { "success": boolean, "familyId": string }

GET /api/families/{familyId}
# Gets family group details and members
Request Headers: { "Authorization": "Bearer {idToken}" }
Response: { "family": Family, "members": User[] }
```

#### Activity Endpoints

```python
POST /api/activities
# Creates new activity (parent only)
Request: { "idToken": string, "familyId": string, "name": string, "unit": string, "rate": float }
Response: { "activity": Activity }

GET /api/activities/{familyId}
# Gets all activities for family
Request Headers: { "Authorization": "Bearer {idToken}" }
Response: { "activities": Activity[] }

DELETE /api/activities/{activityId}
# Deletes activity (parent only)
Request Headers: { "Authorization": "Bearer {idToken}" }
Response: { "success": boolean }
```

#### Log Entry Endpoints

```python
POST /api/logs
# Creates log entry (child only)
Request: { "idToken": string, "activityId": string, "units": int }
Response: { "log": LogEntry }

GET /api/logs/{familyId}/pending
# Gets pending log entries for verification (parent only)
Request Headers: { "Authorization": "Bearer {idToken}" }
Response: { "logs": LogEntry[] }

PATCH /api/logs/{logId}/verify
# Approves or rejects log entry (parent only)
Request: { "idToken": string, "status": "approved" | "rejected" }
Response: { "log": LogEntry }
```

#### Earnings Endpoints

```python
GET /api/earnings/{userId}/today
# Gets today's earnings for user
Request Headers: { "Authorization": "Bearer {idToken}" }
Response: { "pending": float, "verified": float }

GET /api/earnings/{userId}/weekly
# Gets weekly earnings for user
Request Headers: { "Authorization": "Bearer {idToken}" }
Response: { "pending": float, "verified": float }
```

### Middleware

**AuthenticationMiddleware**
- Verifies Firebase ID token on all protected routes
- Extracts user ID and role from token
- Returns 401 for invalid/expired tokens

**RoleAuthorizationMiddleware**
- Checks user role against endpoint requirements
- Returns 403 for insufficient permissions
- Validates family membership for data access

## Data Models

### Firestore Collections Structure

```
users/
  {userId}/
    email: string
    displayName: string
    photoURL: string
    role: "parent" | "child"
    familyId: string | null
    theme: string
    createdAt: timestamp

families/
  {familyId}/
    inviteCode: string (indexed)
    ownerId: string
    createdAt: timestamp
    members: string[] (array of userIds)

activities/
  {activityId}/
    familyId: string (indexed)
    name: string
    unit: string
    rate: float
    createdBy: string (userId)
    createdAt: timestamp

logs/
  {logId}/
    activityId: string (indexed)
    userId: string (indexed)
    familyId: string (indexed)
    units: int
    timestamp: timestamp
    verificationStatus: "pending" | "approved" | "rejected"
    verifiedBy: string | null (userId of parent)
    verifiedAt: timestamp | null
```

### TypeScript Interfaces (Frontend)

```typescript
interface User {
  uid: string;
  email: string;
  displayName: string;
  photoURL: string;
  role: 'parent' | 'child';
  familyId: string | null;
  theme: string;
}

interface Family {
  id: string;
  inviteCode: string;
  ownerId: string;
  members: string[];
  createdAt: Date;
}

interface Activity {
  id: string;
  familyId: string;
  name: string;
  unit: string;
  rate: number;
  createdBy: string;
  createdAt: Date;
}

interface LogEntry {
  id: string;
  activityId: string;
  userId: string;
  familyId: string;
  units: number;
  timestamp: Date;
  verificationStatus: 'pending' | 'approved' | 'rejected';
  verifiedBy: string | null;
  verifiedAt: Date | null;
}

interface Earnings {
  pending: number;
  verified: number;
}
```

### Python Models (Backend)

```python
from pydantic import BaseModel, Field
from typing import Literal, Optional
from datetime import datetime

class User(BaseModel):
    uid: str
    email: str
    display_name: str
    photo_url: str
    role: Literal["parent", "child"]
    family_id: Optional[str] = None
    theme: str = "deep-ocean"

class Family(BaseModel):
    id: str
    invite_code: str
    owner_id: str
    members: list[str]
    created_at: datetime

class Activity(BaseModel):
    id: str
    family_id: str
    name: str
    unit: str
    rate: float = Field(gt=0)
    created_by: str
    created_at: datetime

class LogEntry(BaseModel):
    id: str
    activity_id: str
    user_id: str
    family_id: str
    units: int = Field(gt=0)
    timestamp: datetime
    verification_status: Literal["pending", "approved", "rejected"]
    verified_by: Optional[str] = None
    verified_at: Optional[datetime] = None

class Earnings(BaseModel):
    pending: float
    verified: float
```


## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: User role assignment on first registration

*For any* first-time user completing Google authentication and selecting a role (parent or child), the Backend Service should create a user profile in Firebase with the selected role correctly assigned.

**Validates: Requirements 1.4**

### Property 2: Invite code uniqueness

*For any* set of generated invite codes, no two codes should be identical, ensuring each family group has a unique join code.

**Validates: Requirements 2.4**

### Property 3: Family group creation with owner

*For any* parent user creating a family group, the Backend Service should store the group in Firebase with that parent as both the owner and a member with admin privileges.

**Validates: Requirements 2.2, 2.5**

### Property 4: Invite code validation

*For any* invite code entered by a user, the Backend Service should correctly validate it against existing family groups, accepting valid codes and rejecting invalid ones.

**Validates: Requirements 3.1, 3.3**

### Property 5: Family membership addition

*For any* valid invite code provided by a user not already in a family, the Backend Service should add the user to the corresponding family group as a child member.

**Validates: Requirements 3.2**

### Property 6: Single family membership constraint

*For any* user already in a family group, attempting to join another family should be prevented by the Application.

**Validates: Requirements 3.5**

### Property 7: Role-based authorization enforcement

*For any* child user attempting to perform parent-only operations (verify activities, delete activities, delete family group), the Backend Service should reject the request and return an authorization error.

**Validates: Requirements 4.3, 11.5**

### Property 8: Parent authorization verification

*For any* user attempting to delete a family group, the Backend Service should verify the user has parent privileges before processing the request.

**Validates: Requirements 4.4**

### Property 9: Activity creation with family association

*For any* parent user submitting a valid activity (non-empty name and unit, positive rate), the Backend Service should create the activity in Firebase and correctly associate it with the user's family group.

**Validates: Requirements 5.1**

### Property 10: Activity rate validation

*For any* activity submission with a non-positive rate value (zero or negative), the Backend Service should reject the submission and return a validation error.

**Validates: Requirements 5.4**

### Property 11: Log entry creation with required fields

*For any* child user logging an activity, the Backend Service should create a log entry in Firebase containing the current timestamp, pending verification status, and references to both the child user and the activity.

**Validates: Requirements 6.1, 6.2**

### Property 12: Multiple log entry independence

*For any* child logging the same activity multiple times, the Backend Service should maintain separate timestamped entries for each log, ensuring no logs are merged or overwritten.

**Validates: Requirements 6.3**

### Property 13: Verification status transitions

*For any* log entry being verified by a parent, the Backend Service should update the verification status in Firebase to either "approved" or "rejected" based on the parent's action.

**Validates: Requirements 7.2, 7.3**

### Property 14: Earnings calculation based on verification

*For any* log entry, the calculated earnings should be included in the child's verified totals if and only if the verification status is "approved", and excluded if "rejected" or "pending".

**Validates: Requirements 7.4, 7.5**

### Property 15: Time-windowed earnings filtering

*For any* time window (today or last 7 days) and set of log entries, the earnings calculation should include only approved log entries with timestamps falling within the specified window.

**Validates: Requirements 8.5**

### Property 16: Pending verification display completeness

*For any* pending log entry displayed in the verification interface, the rendered output should contain the activity name, units logged, timestamp, and child name.

**Validates: Requirements 9.3**

### Property 17: Activity card information display

*For any* activity displayed on a card, the rendered output should show the activity name, unit, and rate, and for child users, should separately display pending and verified earnings.

**Validates: Requirements 10.1, 10.2**

### Property 18: Activity deletion cascade

*For any* activity deleted by a parent, the Backend Service should remove both the activity and all associated log entries from Firebase, and recalculate earnings for all affected children.

**Validates: Requirements 11.1, 11.2**

### Property 19: Theme application universality

*For any* theme change, the Application should update all background colors, card colors, text colors, and accent colors immediately across all UI elements.

**Validates: Requirements 12.4**

### Property 20: Theme persistence round-trip

*For any* theme selected by a user, persisting it to Firebase and then reloading the application should restore the same theme preference.

**Validates: Requirements 12.5**

### Property 21: Touch target accessibility

*For any* interactive element (button, link, input) in the mobile view, the element should have a minimum touch target size of 44px to ensure touch-friendliness.

**Validates: Requirements 13.2**

### Property 22: Responsive layout without horizontal scroll

*For any* screen size within the supported range (320px to 2560px width), the Application should maintain readability and usability without requiring horizontal scrolling.

**Validates: Requirements 13.3**

### Property 23: Authentication token validation

*For any* request received by the Backend Service, the service should validate the user's authentication token before processing the request.

**Validates: Requirements 15.2**

### Property 24: Role-based access control enforcement

*For any* request processed by the Backend Service, the service should enforce role-based access control rules, ensuring users can only perform operations permitted for their role.

**Validates: Requirements 15.3**

### Property 25: HTTP status code correctness

*For any* operation completed by the Backend Service, the service should return appropriate HTTP status codes (2xx for success, 4xx for client errors, 5xx for server errors) matching the operation outcome.

**Validates: Requirements 15.4**

### Property 26: Error response descriptiveness

*For any* error encountered by the Backend Service, the service should return descriptive error messages in the response and log the error details.

**Validates: Requirements 15.5**

### Property 27: Input validation and rejection

*For any* user input received by the Backend Service, the service should validate all fields against expected data types and formats, rejecting invalid input with specific validation error messages.

**Validates: Requirements 17.1, 17.2**

### Property 28: String input sanitization

*For any* string input being stored in Firebase, the Backend Service should sanitize the input to prevent injection attacks.

**Validates: Requirements 17.3**

### Property 29: Cross-family data access prevention

*For any* user attempting to access data belonging to a family group they are not a member of, the Backend Service should verify family membership and reject the unauthorized request.

**Validates: Requirements 17.4**

### Property 30: Firebase security rules enforcement

*For any* data access attempt in Firebase, the security rules should enforce that users can only read and write data for their own family group.

**Validates: Requirements 17.5**

### Property 31: Account deletion cleanup

*For any* user confirming account deletion, the Backend Service should remove the user profile from Firebase completely.

**Validates: Requirements 18.3**

### Property 32: Family ownership transfer on parent deletion

*For any* parent user deleting their account, the Backend Service should transfer family group ownership to another parent if one exists, or delete the entire group if no other parents exist.

**Validates: Requirements 18.4**

## Error Handling

### Frontend Error Handling

**Authentication Errors:**
- Google OAuth failures: Display user-friendly error message with retry option
- Token expiration: Automatically redirect to login page
- Network errors during auth: Show offline indicator and retry mechanism

**API Request Errors:**
- 401 Unauthorized: Clear session and redirect to login
- 403 Forbidden: Display "You don't have permission" message
- 404 Not Found: Display "Resource not found" message
- 500 Server Error: Display generic error message and log details
- Network timeout: Show retry button with exponential backoff

**Validation Errors:**
- Display inline error messages next to form fields
- Highlight invalid fields in red
- Prevent form submission until all fields are valid

**Firebase Connection Errors:**
- Display connection status indicator
- Implement automatic reconnection with exponential backoff
- Cache data locally when offline (future enhancement)

### Backend Error Handling

**Authentication Middleware Errors:**
- Invalid token: Return 401 with "Invalid authentication token" message
- Expired token: Return 401 with "Token expired, please sign in again" message
- Missing token: Return 401 with "Authentication required" message

**Authorization Errors:**
- Insufficient permissions: Return 403 with specific permission required
- Family membership mismatch: Return 403 with "Access denied to this family's data"

**Validation Errors:**
- Return 400 Bad Request with detailed field-level error messages
- Use Pydantic validation to catch type and format errors
- Sanitize error messages to avoid exposing internal details

**Database Errors:**
- Firebase connection failure: Return 503 Service Unavailable
- Document not found: Return 404 with specific resource type
- Write conflicts: Implement retry logic with exponential backoff
- Transaction failures: Rollback and return 500 with logged error ID

**Business Logic Errors:**
- Duplicate invite code: Regenerate code automatically (transparent to user)
- User already in family: Return 400 with "Already member of a family"
- Invalid invite code: Return 400 with "Invalid or expired invite code"
- Activity not found: Return 404 with "Activity does not exist"

### Error Logging

**Frontend Logging:**
- Log errors to browser console in development
- Send error reports to monitoring service in production (e.g., Sentry)
- Include user ID, timestamp, error message, and stack trace

**Backend Logging:**
- Use Python logging module with structured logging
- Log levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
- Include request ID, user ID, endpoint, timestamp, and error details
- Store logs in Cloud Logging or similar service for analysis

## Testing Strategy

### Unit Testing

**Frontend Unit Tests (Jest + React Testing Library):**
- Component rendering tests for all UI components
- User interaction tests (button clicks, form submissions)
- State management tests (hooks, context)
- Theme switching logic
- Form validation logic
- Utility function tests (date calculations, earnings calculations)

**Backend Unit Tests (pytest):**
- API endpoint tests for all routes
- Authentication middleware tests
- Authorization logic tests
- Data validation tests (Pydantic models)
- Business logic tests (invite code generation, earnings calculation)
- Error handling tests
- Firebase interaction mocking

**Key Unit Test Examples:**
- Test that empty activity name is rejected (edge case for 5.2)
- Test that empty unit field is rejected (edge case for 5.3)
- Test that Firebase connection errors are handled gracefully (edge case for 14.4)
- Test that corrupted Firebase data is handled (edge case for 14.5)
- Test that no pending verifications shows appropriate message (edge case for 9.5)
- Test that all pending verifications cleared removes badge (edge case for 16.4)

### Property-Based Testing

**Property-Based Testing Library:**
- Frontend: fast-check (JavaScript/TypeScript property-based testing)
- Backend: Hypothesis (Python property-based testing)

**Configuration:**
- Minimum 100 iterations per property test
- Use shrinking to find minimal failing examples
- Seed random generation for reproducibility

**Property Test Tagging:**
Each property-based test must include a comment with this format:
```
// Feature: gamified-activity-tracker, Property 1: User role assignment on first registration
```

**Frontend Property Tests:**
- Property 19: Theme application universality - Generate random theme selections and verify all UI elements update
- Property 21: Touch target accessibility - Generate random interactive elements and verify minimum 44px size
- Property 22: Responsive layout - Generate random viewport sizes and verify no horizontal scroll

**Backend Property Tests:**
- Property 1: User role assignment - Generate random user data and roles, verify correct profile creation
- Property 2: Invite code uniqueness - Generate many invite codes, verify no duplicates
- Property 3: Family group creation - Generate random parent users, verify owner and membership
- Property 4: Invite code validation - Generate random valid/invalid codes, verify correct validation
- Property 5: Family membership addition - Generate random users and codes, verify correct addition
- Property 6: Single family constraint - Generate users in families, verify join prevention
- Property 7: Role-based authorization - Generate random child users and parent operations, verify rejection
- Property 8: Parent authorization - Generate random users and roles, verify privilege checking
- Property 9: Activity creation - Generate random valid activities, verify creation and association
- Property 10: Activity rate validation - Generate random non-positive rates, verify rejection
- Property 11: Log entry creation - Generate random child users and activities, verify log fields
- Property 12: Multiple log independence - Generate multiple logs for same activity, verify separation
- Property 13: Verification status - Generate random log entries and verification actions, verify status updates
- Property 14: Earnings calculation - Generate random logs with various statuses, verify correct earnings
- Property 15: Time-windowed earnings - Generate random logs with various timestamps, verify filtering
- Property 16: Pending verification display - Generate random pending logs, verify all fields present
- Property 17: Activity card display - Generate random activities, verify all information displayed
- Property 18: Activity deletion cascade - Generate random activities with logs, verify complete removal
- Property 20: Theme persistence - Generate random themes, verify round-trip through Firebase
- Property 23: Token validation - Generate random requests, verify token validation occurs
- Property 24: RBAC enforcement - Generate random requests with various roles, verify access control
- Property 25: HTTP status codes - Generate random operations, verify correct status codes
- Property 26: Error responses - Generate random errors, verify descriptive messages
- Property 27: Input validation - Generate random valid/invalid inputs, verify validation and rejection
- Property 28: String sanitization - Generate random strings including malicious inputs, verify sanitization
- Property 29: Cross-family access - Generate random users and families, verify access prevention
- Property 30: Firebase security rules - Generate random data access attempts, verify rule enforcement
- Property 31: Account deletion - Generate random users, verify profile removal
- Property 32: Ownership transfer - Generate random family configurations, verify correct transfer logic

### Integration Testing

**Frontend-Backend Integration:**
- End-to-end authentication flow (Google OAuth → role selection → dashboard)
- Activity creation flow (form submission → API call → Firebase → UI update)
- Activity logging flow (button click → API call → Firebase → notification)
- Verification flow (parent approval → API call → Firebase → child UI update)
- Real-time synchronization (Firebase change → UI update)

**Firebase Integration:**
- Test actual Firebase operations in test environment
- Verify security rules with Firebase Emulator
- Test real-time listeners and data synchronization

### Test Data Generation

**Generators for Property Tests:**
- User generator: Random uid, email, role, familyId
- Activity generator: Random name, unit, positive rate
- Log entry generator: Random activityId, userId, timestamp, status
- Invite code generator: Random 6-character alphanumeric strings
- Theme generator: Random selection from three themes
- Timestamp generator: Random dates within various time windows

**Constraints for Generators:**
- Rates must be positive floats
- Timestamps must be valid dates
- Invite codes must be exactly 6 alphanumeric characters
- Roles must be either "parent" or "child"
- Verification status must be "pending", "approved", or "rejected"

### Test Environment Setup

**Frontend Test Environment:**
- Mock Firebase SDK for unit tests
- Use Firebase Emulator for integration tests
- Mock API calls with MSW (Mock Service Worker)
- Test in multiple viewport sizes for responsive tests

**Backend Test Environment:**
- Use Firebase Emulator for Firestore and Auth
- Mock external services (Google OAuth)
- Use pytest fixtures for test data setup
- Separate test database from production

**CI/CD Integration:**
- Run all tests on every pull request
- Require 80% code coverage minimum
- Run property tests with fixed seed for consistency
- Deploy only if all tests pass

## Implementation Notes

### Firebase Configuration

**Firestore Indexes:**
- Composite index on `logs` collection: `(familyId, verificationStatus, timestamp)`
- Single field index on `families.inviteCode` for fast lookup
- Single field index on `activities.familyId` for family queries
- Single field index on `logs.userId` for user queries

**Security Rules:**
```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Helper functions
    function isAuthenticated() {
      return request.auth != null;
    }
    
    function getUserData() {
      return get(/databases/$(database)/documents/users/$(request.auth.uid)).data;
    }
    
    function isParent() {
      return getUserData().role == 'parent';
    }
    
    function isSameFamily(familyId) {
      return getUserData().familyId == familyId;
    }
    
    // Users collection
    match /users/{userId} {
      allow read: if isAuthenticated() && (request.auth.uid == userId || isSameFamily(resource.data.familyId));
      allow create: if isAuthenticated() && request.auth.uid == userId;
      allow update: if isAuthenticated() && request.auth.uid == userId;
      allow delete: if isAuthenticated() && request.auth.uid == userId;
    }
    
    // Families collection
    match /families/{familyId} {
      allow read: if isAuthenticated() && isSameFamily(familyId);
      allow create: if isAuthenticated() && isParent();
      allow update: if isAuthenticated() && isParent() && isSameFamily(familyId);
      allow delete: if isAuthenticated() && isParent() && isSameFamily(familyId);
    }
    
    // Activities collection
    match /activities/{activityId} {
      allow read: if isAuthenticated() && isSameFamily(resource.data.familyId);
      allow create: if isAuthenticated() && isParent() && isSameFamily(request.resource.data.familyId);
      allow update: if isAuthenticated() && isParent() && isSameFamily(resource.data.familyId);
      allow delete: if isAuthenticated() && isParent() && isSameFamily(resource.data.familyId);
    }
    
    // Logs collection
    match /logs/{logId} {
      allow read: if isAuthenticated() && isSameFamily(resource.data.familyId);
      allow create: if isAuthenticated() && isSameFamily(request.resource.data.familyId);
      allow update: if isAuthenticated() && isParent() && isSameFamily(resource.data.familyId);
      allow delete: if isAuthenticated() && isParent() && isSameFamily(resource.data.familyId);
    }
  }
}
```

### Performance Considerations

**Frontend Optimization:**
- Lazy load components with React.lazy()
- Memoize expensive calculations with useMemo()
- Debounce real-time listeners to avoid excessive re-renders
- Implement virtual scrolling for long lists of activities/logs
- Use React.memo() for activity cards to prevent unnecessary re-renders

**Backend Optimization:**
- Implement caching for frequently accessed data (family groups, activities)
- Use batch operations for multiple Firebase writes
- Implement pagination for large log entry queries
- Use Firebase transactions for concurrent updates
- Add rate limiting to prevent abuse

**Database Optimization:**
- Denormalize data where appropriate (e.g., store activity name in logs for faster queries)
- Use Firestore batch writes for related operations
- Implement data archiving for old log entries
- Monitor query performance and add indexes as needed

### Security Considerations

**Authentication Security:**
- Use Firebase Authentication with Google OAuth only
- Implement token refresh logic before expiration
- Store tokens securely (httpOnly cookies for web)
- Implement CSRF protection for state-changing operations

**Authorization Security:**
- Always verify user role on backend, never trust frontend
- Implement family membership checks on all data access
- Use Firebase Security Rules as second layer of defense
- Log all authorization failures for security monitoring

**Data Security:**
- Sanitize all user inputs to prevent XSS and injection attacks
- Use parameterized queries for all database operations
- Implement rate limiting on API endpoints
- Encrypt sensitive data at rest (Firebase handles this)
- Use HTTPS for all communications

**Privacy Considerations:**
- Only share data within family groups
- Implement proper account deletion (GDPR compliance)
- Don't log sensitive user information
- Provide clear privacy policy and terms of service

### Deployment Architecture

**Frontend Deployment:**
- Deploy Next.js app to Vercel or Firebase Hosting
- Use environment variables for Firebase config
- Enable automatic deployments from main branch
- Implement preview deployments for pull requests

**Backend Deployment:**
- Deploy FastAPI to Cloud Run, Railway, or similar
- Use environment variables for Firebase Admin SDK credentials
- Enable auto-scaling based on traffic
- Implement health check endpoint for monitoring

**Database:**
- Use Firebase Firestore in production mode
- Set up automated backups
- Monitor usage and costs
- Implement data retention policies

### Monitoring and Observability

**Application Monitoring:**
- Use Firebase Analytics for user behavior tracking
- Implement error tracking with Sentry or similar
- Monitor API response times and error rates
- Set up alerts for critical errors

**Performance Monitoring:**
- Use Firebase Performance Monitoring for frontend
- Monitor backend API latency and throughput
- Track database query performance
- Monitor real-time listener connection counts

**Business Metrics:**
- Track daily active users (parents and children)
- Monitor activity creation and logging rates
- Track verification completion rates
- Measure user retention and engagement

