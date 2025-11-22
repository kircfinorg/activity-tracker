# Implementation Plan

- [-] 1. Set up project structure and dependencies
  - Create Next.js project with TypeScript and Tailwind CSS
  - Install Firebase SDK, Lucide-React icons, and other frontend dependencies
  - Create Python FastAPI project structure
  - Install Firebase Admin SDK, Pydantic, pytest, and Hypothesis
  - Set up environment configuration files for both frontend and backend
  - _Requirements: All_

- [x] 2. Configure Firebase and authentication
  - [x] 2.1 Set up Firebase project and enable Google Authentication
    - Create Firebase project in console
    - Enable Google OAuth provider
    - Configure authorized domains
    - _Requirements: 1.1, 1.2_
  
  - [ ] 2.2 Implement Firebase configuration in frontend
    - Create Firebase config file with environment variables
    - Initialize Firebase app and auth
    - _Requirements: 1.1_
  
  - [x] 2.3 Implement Firebase Admin SDK in backend
    - Initialize Firebase Admin with service account credentials
    - Create authentication middleware for token verification
    - _Requirements: 15.2_
  
  - [x] 2.4 Write property test for authentication token validation
    - **Property 23: Authentication token validation**
    - **Validates: Requirements 15.2**

- [x] 3. Implement user authentication and registration flow
  - [x] 3.1 Create Google sign-in UI component
    - Build GoogleSignInButton component
    - Implement OAuth flow initiation
    - Handle authentication success and errors
    - _Requirements: 1.1, 1.2_
  
  - [x] 3.2 Create role selection modal for first-time users
    - Build RoleSelectionModal component
    - Implement parent/child role selection
    - _Requirements: 1.3_
  
  - [x] 3.3 Implement backend endpoint for setting user role
    - Create POST /api/auth/set-role endpoint
    - Validate role selection and create user profile in Firestore
    - _Requirements: 1.4_
  
  - [x] 3.4 Write property test for user role assignment
    - **Property 1: User role assignment on first registration**
    - **Validates: Requirements 1.4**
  
  - [x] 3.5 Implement user profile retrieval for existing users
    - Create backend endpoint to fetch user data
    - Handle existing user login flow in frontend
    - _Requirements: 1.5_
  
  - [x] 3.6 Add sign-out functionality
    - Implement sign-out button in header
    - Clear session and redirect to login
    - _Requirements: 1.6_

- [ ] 4. Implement family group creation and joining
  - [ ] 4.1 Create invite code generation logic
    - Implement 6-character alphanumeric code generator
    - Ensure uniqueness by checking against existing codes
    - _Requirements: 2.1, 2.4_
  
  - [ ] 4.2 Write property test for invite code uniqueness
    - **Property 2: Invite code uniqueness**
    - **Validates: Requirements 2.4**
  
  - [ ] 4.3 Implement backend endpoint for family creation
    - Create POST /api/families endpoint
    - Generate invite code and store family in Firestore
    - Add parent as owner and member
    - _Requirements: 2.2, 2.5_
  
  - [ ] 4.4 Write property test for family group creation
    - **Property 3: Family group creation with owner**
    - **Validates: Requirements 2.2, 2.5**
  
  - [ ] 4.5 Create family creation UI for parents
    - Build CreateFamilyForm component
    - Display generated invite code after creation
    - _Requirements: 2.3_
  
  - [ ] 4.6 Implement backend endpoint for joining family
    - Create POST /api/families/join endpoint
    - Validate invite code and add user to family
    - Prevent users from joining multiple families
    - _Requirements: 3.1, 3.2, 3.5_
  
  - [ ] 4.7 Write property tests for invite code validation and family joining
    - **Property 4: Invite code validation**
    - **Property 5: Family membership addition**
    - **Property 6: Single family membership constraint**
    - **Validates: Requirements 3.1, 3.2, 3.3, 3.5**
  
  - [ ] 4.8 Create family joining UI
    - Build JoinFamilyForm component
    - Handle invite code input and validation errors
    - Redirect to dashboard on success
    - _Requirements: 3.3, 3.4_

- [ ] 5. Implement role-based access control
  - [ ] 5.1 Create authorization middleware in backend
    - Implement role checking logic
    - Create decorators for parent-only and child-only endpoints
    - _Requirements: 4.3, 4.4, 4.5_
  
  - [ ]* 5.2 Write property tests for role-based authorization
    - **Property 7: Role-based authorization enforcement**
    - **Property 8: Parent authorization verification**
    - **Property 24: Role-based access control enforcement**
    - **Validates: Requirements 4.3, 4.4, 15.3**
  
  - [ ] 5.3 Implement role-based UI rendering in frontend
    - Create useUserRole hook
    - Conditionally render components based on role
    - _Requirements: 4.1, 4.2_

- [ ] 6. Implement activity creation and management
  - [ ] 6.1 Create activity data model and validation
    - Define Activity Pydantic model with validation rules
    - Implement validation for name, unit, and rate fields
    - _Requirements: 5.2, 5.3, 5.4_
  
  - [ ]* 6.2 Write property tests for activity creation and validation
    - **Property 9: Activity creation with family association**
    - **Property 10: Activity rate validation**
    - **Validates: Requirements 5.1, 5.4**
  
  - [ ] 6.3 Implement backend endpoints for activities
    - Create POST /api/activities endpoint (parent only)
    - Create GET /api/activities/{familyId} endpoint
    - Create DELETE /api/activities/{activityId} endpoint (parent only)
    - _Requirements: 5.1, 11.1_
  
  - [ ] 6.4 Create activity creation form UI
    - Build CreateActivityForm component with name, unit, rate fields
    - Implement form validation and error display
    - _Requirements: 5.2, 5.3, 5.4_
  
  - [ ] 6.5 Create ActivityCard component
    - Display activity name, unit, rate
    - Show earnings (pending/verified for children, total for parents)
    - Add increment button for children
    - Add delete button for parents
    - _Requirements: 10.1, 10.2, 10.3, 10.4_
  
  - [ ]* 6.6 Write property test for activity card display
    - **Property 17: Activity card information display**
    - **Validates: Requirements 10.1, 10.2**
  
  - [ ] 6.7 Create ActivityGrid component
    - Implement responsive grid layout
    - Handle empty state
    - _Requirements: 10.1_
  
  - [ ] 6.8 Implement activity deletion with cascade
    - Delete activity and all associated log entries
    - Recalculate earnings for affected children
    - _Requirements: 11.1, 11.2, 11.3, 11.4_
  
  - [ ]* 6.9 Write property test for activity deletion cascade
    - **Property 18: Activity deletion cascade**
    - **Validates: Requirements 11.1, 11.2**

- [ ] 7. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 8. Implement activity logging by children
  - [ ] 8.1 Create log entry data model
    - Define LogEntry Pydantic model
    - Include timestamp, verification status, and references
    - _Requirements: 6.1, 6.2_
  
  - [ ] 8.2 Implement backend endpoint for creating log entries
    - Create POST /api/logs endpoint (child only)
    - Generate timestamp and set status to pending
    - Store in Firestore with all required fields
    - _Requirements: 6.1, 6.2, 6.3_
  
  - [ ]* 8.3 Write property tests for log entry creation
    - **Property 11: Log entry creation with required fields**
    - **Property 12: Multiple log entry independence**
    - **Validates: Requirements 6.1, 6.2, 6.3**
  
  - [ ] 8.4 Implement increment button functionality in ActivityCard
    - Handle button click to create log entry
    - Show visual feedback on success
    - Display "Pending Verification" status
    - _Requirements: 6.4, 6.5, 10.5_
  
  - [ ] 8.5 Implement real-time notification for parents
    - Update parent's pending verification count when child logs activity
    - Display notification badge
    - _Requirements: 6.5, 16.1, 16.2_

- [ ] 9. Implement activity verification by parents
  - [ ] 9.1 Create verification queue UI component
    - Build VerificationQueue component
    - Display pending log entries grouped by child
    - Show activity name, units, timestamp, child name
    - _Requirements: 7.1, 9.3_
  
  - [ ]* 9.2 Write property test for pending verification display
    - **Property 16: Pending verification display completeness**
    - **Validates: Requirements 9.3**
  
  - [ ] 9.3 Create VerificationItem component
    - Display single log entry details
    - Add approve and reject buttons
    - _Requirements: 7.1_
  
  - [ ] 9.4 Implement backend endpoint for verification
    - Create PATCH /api/logs/{logId}/verify endpoint (parent only)
    - Update verification status to approved or rejected
    - Record verifiedBy and verifiedAt fields
    - _Requirements: 7.2, 7.3_
  
  - [ ]* 9.5 Write property test for verification status transitions
    - **Property 13: Verification status transitions**
    - **Validates: Requirements 7.2, 7.3**
  
  - [ ] 9.6 Implement real-time updates for children
    - Update child's dashboard when parent verifies
    - Clear notification badge for parents
    - _Requirements: 16.3, 16.4, 16.5_

- [ ] 10. Implement earnings calculation and display
  - [ ] 10.1 Create earnings calculation logic
    - Calculate earnings based on log entries and activity rates
    - Filter by verification status (approved only)
    - Filter by time window (today, last 7 days)
    - _Requirements: 7.4, 7.5, 8.5_
  
  - [ ]* 10.2 Write property tests for earnings calculation
    - **Property 14: Earnings calculation based on verification**
    - **Property 15: Time-windowed earnings filtering**
    - **Validates: Requirements 7.4, 7.5, 8.5**
  
  - [ ] 10.3 Implement backend endpoints for earnings
    - Create GET /api/earnings/{userId}/today endpoint
    - Create GET /api/earnings/{userId}/weekly endpoint
    - Return pending and verified earnings separately
    - _Requirements: 8.1, 8.2_
  
  - [ ] 10.4 Create EarningsSummaryCard component
    - Display today's earnings
    - Display weekly earnings
    - Show pending vs verified amounts for children
    - _Requirements: 8.1, 8.2_
  
  - [ ] 10.5 Implement real-time earnings updates
    - Recalculate and update earnings when logs are verified
    - Update both today's and weekly displays
    - _Requirements: 8.3, 8.4_

- [ ] 11. Implement parent and child dashboards
  - [ ] 11.1 Create ParentDashboard component
    - Display all children with pending verification counts
    - Show total pending verifications
    - Provide navigation to verification interface
    - Display empty state when no pending verifications
    - _Requirements: 9.1, 9.4, 9.5_
  
  - [ ] 11.2 Create ChildDashboard component
    - Display activity grid for logging
    - Show earnings summary cards
    - Display pending verification status
    - _Requirements: 8.1, 8.2, 6.4_
  
  - [ ] 11.3 Implement child selection and detail view for parents
    - Allow parent to select a child
    - Display child's activity history and pending logs
    - _Requirements: 9.2_

- [ ] 12. Implement theme system
  - [ ] 12.1 Create theme configuration
    - Define three theme objects (Hacker Terminal, Soft Serenity, Deep Ocean)
    - Specify colors, fonts, and styling for each theme
    - _Requirements: 12.1, 12.2, 12.3_
  
  - [ ] 12.2 Create ThemeProvider context
    - Implement theme state management
    - Apply theme classes to root element
    - _Requirements: 12.4_
  
  - [ ]* 12.3 Write property test for theme application
    - **Property 19: Theme application universality**
    - **Validates: Requirements 12.4**
  
  - [ ] 12.4 Create ThemeSelector component
    - Build dropdown or button group for theme selection
    - Handle theme change events
    - _Requirements: 12.1, 12.2, 12.3_
  
  - [ ] 12.5 Implement theme persistence
    - Save theme preference to Firebase user profile
    - Load theme on application start
    - _Requirements: 12.5_
  
  - [ ]* 12.6 Write property test for theme persistence
    - **Property 20: Theme persistence round-trip**
    - **Validates: Requirements 12.5**

- [ ] 13. Implement responsive design
  - [ ] 13.1 Configure Tailwind for responsive breakpoints
    - Set up mobile-first responsive classes
    - Define custom breakpoints if needed
    - _Requirements: 13.1, 13.3_
  
  - [ ] 13.2 Implement responsive layouts for all components
    - Single-column layout on mobile
    - Vertical stacking of activity cards
    - Responsive verification interface
    - _Requirements: 13.1, 13.4, 13.5_
  
  - [ ] 13.3 Ensure touch-friendly interactive elements
    - Set minimum 44px touch targets for all buttons
    - Add appropriate spacing for mobile
    - _Requirements: 13.2_
  
  - [ ]* 13.4 Write property tests for responsive design
    - **Property 21: Touch target accessibility**
    - **Property 22: Responsive layout without horizontal scroll**
    - **Validates: Requirements 13.2, 13.3**

- [ ] 14. Implement data persistence and synchronization
  - [ ] 14.1 Set up Firestore collections and indexes
    - Create users, families, activities, logs collections
    - Add composite indexes for efficient queries
    - _Requirements: 14.1, 14.2_
  
  - [ ] 14.2 Implement Firebase Security Rules
    - Write security rules for all collections
    - Enforce family-based data isolation
    - Test rules with Firebase Emulator
    - _Requirements: 17.5_
  
  - [ ]* 14.3 Write property test for Firebase security rules
    - **Property 30: Firebase security rules enforcement**
    - **Validates: Requirements 17.5**
  
  - [ ] 14.3 Implement real-time listeners in frontend
    - Set up Firestore listeners for activities and logs
    - Handle real-time updates and refresh UI
    - _Requirements: 14.3, 16.5_
  
  - [ ] 14.4 Implement error handling for Firebase operations
    - Handle connection errors with retry logic
    - Handle corrupted data gracefully
    - Display error messages to users
    - _Requirements: 14.4, 14.5_

- [ ] 15. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 16. Implement backend API error handling and validation
  - [ ] 16.1 Implement comprehensive input validation
    - Validate all request fields with Pydantic
    - Return specific validation error messages
    - _Requirements: 17.1, 17.2_
  
  - [ ]* 16.2 Write property test for input validation
    - **Property 27: Input validation and rejection**
    - **Validates: Requirements 17.1, 17.2**
  
  - [ ] 16.3 Implement string sanitization
    - Sanitize all string inputs before storing
    - Prevent injection attacks
    - _Requirements: 17.3_
  
  - [ ]* 16.4 Write property test for string sanitization
    - **Property 28: String input sanitization**
    - **Validates: Requirements 17.3**
  
  - [ ] 16.5 Implement family membership verification
    - Check family membership on all data access
    - Reject unauthorized cross-family requests
    - _Requirements: 17.4_
  
  - [ ]* 16.6 Write property test for cross-family access prevention
    - **Property 29: Cross-family data access prevention**
    - **Validates: Requirements 17.4**
  
  - [ ] 16.7 Implement HTTP status code handling
    - Return appropriate status codes for all operations
    - Include descriptive error messages
    - Log errors with details
    - _Requirements: 15.4, 15.5_
  
  - [ ]* 16.8 Write property tests for HTTP responses
    - **Property 25: HTTP status code correctness**
    - **Property 26: Error response descriptiveness**
    - **Validates: Requirements 15.4, 15.5**

- [ ] 17. Implement account deletion
  - [ ] 17.1 Create AccountSettings component
    - Display user profile information
    - Add delete account button
    - _Requirements: 18.1_
  
  - [ ] 17.2 Create account deletion confirmation dialog
    - Display warning about data loss
    - Require explicit confirmation
    - _Requirements: 18.2_
  
  - [ ] 17.3 Implement backend endpoint for account deletion
    - Create DELETE /api/auth/delete-account endpoint
    - Remove user profile from Firestore
    - Handle family ownership transfer logic
    - _Requirements: 18.3, 18.4_
  
  - [ ]* 17.4 Write property tests for account deletion
    - **Property 31: Account deletion cleanup**
    - **Property 32: Family ownership transfer on parent deletion**
    - **Validates: Requirements 18.3, 18.4**
  
  - [ ] 17.5 Implement post-deletion flow
    - Sign out user after deletion
    - Redirect to login page
    - _Requirements: 18.5_

- [ ] 18. Implement family member management
  - [ ] 18.1 Create FamilyMembersList component
    - Display all family members
    - Show role badges (Parent/Child)
    - _Requirements: 9.1_
  
  - [ ] 18.2 Implement backend endpoint for family details
    - Create GET /api/families/{familyId} endpoint
    - Return family info and member list
    - _Requirements: 9.1_

- [ ] 19. Add loading states and visual feedback
  - [ ] 19.1 Create loading spinner components
    - Build reusable loading indicators
    - Add to all async operations
    - _Requirements: 10.5_
  
  - [ ] 19.2 Implement success/error toast notifications
    - Show feedback for activity creation, logging, verification
    - Display error messages for failed operations
    - _Requirements: 10.5_
  
  - [ ] 19.3 Add skeleton loaders for data fetching
    - Show placeholders while loading activities and logs
    - Improve perceived performance
    - _Requirements: 14.1, 14.2_

- [ ] 20. Final checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 21. Polish UI and user experience
  - [ ] 21.1 Add animations and transitions
    - Smooth theme transitions
    - Card hover effects
    - Button click animations
    - _Requirements: 12.4_
  
  - [ ] 21.2 Improve form UX
    - Add input focus states
    - Show inline validation errors
    - Auto-focus first field
    - _Requirements: 5.2, 5.3, 5.4_
  
  - [ ] 21.3 Add empty states
    - Show helpful messages when no activities exist
    - Guide users to create first activity
    - Display empty state for no pending verifications
    - _Requirements: 9.5_
  
  - [ ] 21.4 Optimize mobile experience
    - Test on various mobile devices
    - Adjust spacing and sizing for better touch interaction
    - Ensure single-handed operation for key flows
    - _Requirements: 13.5_

