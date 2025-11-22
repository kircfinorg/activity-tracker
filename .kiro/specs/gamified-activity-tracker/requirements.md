# Requirements Document

## Introduction

The Gamified Activity & Reward Tracker is a full-stack web application that enables families to track children's productivity and habits by assigning monetary value to specific units of work. The system supports parent-child relationships where children log activities and parents verify completion to approve rewards. Users authenticate via Google, join family groups using invite codes, and interact through a responsive React interface backed by Python services and Firebase for data persistence. The application provides an engaging, gamified experience with multiple visual themes optimized for both mobile and desktop use.

## Glossary

- **Activity**: A user-defined trackable task or habit with an associated name, unit, and rate
- **Unit**: The measurement increment for an activity (e.g., "Pomodoro", "Day", "Mile")
- **Rate**: The monetary value assigned to one unit of an activity
- **Log Entry**: A timestamped record of units completed for a specific activity, requiring parent verification
- **Earnings**: The calculated monetary value based on verified logged units and activity rate
- **Theme**: A visual styling preset that changes the application's colors, fonts, and aesthetics
- **Dashboard**: The main view displaying activity cards and earnings summaries
- **Family Group**: A collection of parent and child users who share activities and verification workflows
- **Parent User**: A user with administrative privileges who can create family groups, verify activities, and manage children
- **Child User**: A user who can log activities and view their earnings pending parent verification
- **Invite Code**: A unique alphanumeric string used to join an existing family group
- **Verification Status**: The state of a log entry indicating whether it is pending, approved, or rejected by a parent
- **Application**: The Gamified Activity & Reward Tracker web application
- **Firebase**: The cloud database service used for data persistence and real-time synchronization
- **Backend Service**: The Python-based server component that handles business logic and Firebase operations

## Requirements

### Requirement 1: User Authentication and Registration

**User Story:** As a user, I want to sign in with my Google account and specify my role, so that I can securely access the application with appropriate permissions.

#### Acceptance Criteria

1. WHEN a user visits the application without an active session THEN the Application SHALL display a Google sign-in button
2. WHEN a user clicks the Google sign-in button THEN the Application SHALL initiate the Google OAuth authentication flow
3. WHEN Google authentication succeeds for a first-time user THEN the Application SHALL display a role selection interface asking whether the user is a parent or child
4. WHEN a first-time user selects their role THEN the Backend Service SHALL create the user profile in Firebase with the selected role
5. WHEN Google authentication succeeds for an existing user THEN the Application SHALL retrieve the user profile from Firebase and redirect to the dashboard
6. WHEN a user is authenticated THEN the Application SHALL display a sign-out button in the header

### Requirement 2: Family Group Creation

**User Story:** As a parent user, I want to create a family group with a unique invite code, so that my children can join and I can manage their activities.

#### Acceptance Criteria

1. WHEN a parent user creates a family group THEN the Backend Service SHALL generate a unique 6-character alphanumeric invite code
2. WHEN a family group is created THEN the Backend Service SHALL store the group in Firebase with the parent as the owner
3. WHEN a family group is created THEN the Application SHALL display the invite code prominently for sharing
4. WHEN generating an invite code THEN the Backend Service SHALL ensure the code does not conflict with existing codes
5. WHEN a parent creates a family group THEN the Application SHALL automatically add the parent as a member with admin privileges

### Requirement 3: Family Group Joining

**User Story:** As a child user, I want to join a family group using an invite code, so that I can participate in the activity tracking system.

#### Acceptance Criteria

1. WHEN a user enters an invite code THEN the Backend Service SHALL validate the code against existing family groups in Firebase
2. WHEN a valid invite code is provided THEN the Backend Service SHALL add the user to the family group as a child member
3. WHEN an invalid invite code is provided THEN the Application SHALL display an error message and reject the join request
4. WHEN a user successfully joins a family group THEN the Application SHALL redirect the user to the family dashboard
5. WHEN a user is already in a family group THEN the Application SHALL prevent joining additional groups

### Requirement 4: Role-Based Access Control

**User Story:** As a system administrator, I want users to have different permissions based on their role, so that parents can manage activities while children can only log their work.

#### Acceptance Criteria

1. WHEN a parent user accesses the dashboard THEN the Application SHALL display activity creation controls and verification interfaces
2. WHEN a child user accesses the dashboard THEN the Application SHALL display only activity logging controls without verification capabilities
3. WHEN a child user attempts to verify an activity THEN the Backend Service SHALL reject the request and return an authorization error
4. WHEN a parent user attempts to delete the family group THEN the Backend Service SHALL verify parent privileges before processing
5. WHEN determining user permissions THEN the Backend Service SHALL query the user's role from Firebase

### Requirement 5: Activity Creation

**User Story:** As a parent user, I want to create new activities with custom names, units, and rates, so that I can define what tasks my children should track.

#### Acceptance Criteria

1. WHEN a parent submits a new activity with a name, unit, and rate THEN the Backend Service SHALL create the activity in Firebase and associate it with the family group
2. WHEN a parent provides an empty name field THEN the Backend Service SHALL reject the submission and return a validation error
3. WHEN a parent provides an empty unit field THEN the Backend Service SHALL reject the submission and return a validation error
4. WHEN a parent provides a non-positive rate value THEN the Backend Service SHALL reject the submission and return a validation error
5. WHEN a new activity is created THEN the Application SHALL display the activity on the family dashboard immediately

### Requirement 6: Activity Logging by Children

**User Story:** As a child user, I want to log units of work for activities, so that I can record my completed tasks and earn rewards pending parent approval.

#### Acceptance Criteria

1. WHEN a child clicks the increment button on an activity card THEN the Backend Service SHALL create a log entry with the current timestamp and pending verification status
2. WHEN a log entry is created THEN the Backend Service SHALL store the entry in Firebase with a reference to the child user and activity
3. WHEN a child logs multiple units for the same activity THEN the Backend Service SHALL maintain separate timestamped entries for each log
4. WHEN a log entry is created THEN the Application SHALL display the entry as "Pending Verification" on the child's dashboard
5. WHEN a log entry is created THEN the Application SHALL notify parent users that verification is required

### Requirement 7: Activity Verification by Parents

**User Story:** As a parent user, I want to review and verify my children's logged activities on a daily basis, so that I can confirm they completed the work before approving rewards.

#### Acceptance Criteria

1. WHEN a parent accesses the verification interface THEN the Application SHALL display all pending log entries from the current day grouped by child
2. WHEN a parent approves a log entry THEN the Backend Service SHALL update the verification status to approved in Firebase
3. WHEN a parent rejects a log entry THEN the Backend Service SHALL update the verification status to rejected in Firebase
4. WHEN a log entry is approved THEN the Application SHALL add the earnings to the child's verified totals
5. WHEN a log entry is rejected THEN the Application SHALL exclude the earnings from the child's totals and mark it as rejected

### Requirement 8: Earnings Dashboard

**User Story:** As a child user, I want to view my earnings for today and this week, so that I can track my progress and stay motivated.

#### Acceptance Criteria

1. WHEN the dashboard loads THEN the Application SHALL display a summary card showing verified earnings for the current 24-hour period
2. WHEN the dashboard loads THEN the Application SHALL display a summary card showing verified earnings for the last 7 days
3. WHEN a parent verifies a log entry THEN the Application SHALL recalculate and update the child's today's earnings display
4. WHEN a parent verifies a log entry THEN the Application SHALL recalculate and update the child's weekly earnings display
5. WHEN calculating time-based earnings THEN the Backend Service SHALL include only approved log entries within the specified time window

### Requirement 9: Parent Dashboard View

**User Story:** As a parent user, I want to view all children's activities and pending verifications in one place, so that I can efficiently manage the family's tracking system.

#### Acceptance Criteria

1. WHEN a parent accesses the dashboard THEN the Application SHALL display all children in the family group with their pending verification counts
2. WHEN a parent selects a child THEN the Application SHALL display that child's activity history and pending log entries
3. WHEN displaying pending verifications THEN the Application SHALL show the activity name, units logged, timestamp, and child name
4. WHEN a parent views the dashboard THEN the Application SHALL display the total pending verifications requiring attention
5. WHEN no pending verifications exist THEN the Application SHALL display a message indicating all activities are up to date

### Requirement 10: Activity Cards Display

**User Story:** As a user, I want to see activity cards displaying key information and controls, so that I can quickly understand and interact with tracked activities.

#### Acceptance Criteria

1. WHEN an activity is displayed THEN the Application SHALL show the activity name, unit, and rate on the card
2. WHEN an activity is displayed to a child THEN the Application SHALL show pending and verified earnings separately
3. WHEN an activity is displayed to a child THEN the Application SHALL provide a prominent increment button for logging units
4. WHEN an activity is displayed to a parent THEN the Application SHALL provide a delete button for removing the activity
5. WHEN the increment button is clicked THEN the Application SHALL provide visual feedback indicating the log was created

### Requirement 11: Activity Deletion

**User Story:** As a parent user, I want to delete activities that are no longer needed, so that I can keep the dashboard focused on current goals.

#### Acceptance Criteria

1. WHEN a parent clicks the delete button on an activity card THEN the Backend Service SHALL remove the activity and all associated log entries from Firebase
2. WHEN an activity is deleted THEN the Backend Service SHALL recalculate earnings for all affected children
3. WHEN an activity is deleted THEN the Application SHALL update the dashboard immediately
4. WHEN an activity is deleted THEN the Application SHALL remove the activity card from all users' displays
5. WHEN a child user attempts to delete an activity THEN the Backend Service SHALL reject the request and return an authorization error

### Requirement 12: Theme System

**User Story:** As a user, I want to switch between different visual themes, so that I can customize the application's appearance to match my preferences.

#### Acceptance Criteria

1. WHEN a user selects the "Hacker Terminal" theme THEN the Application SHALL apply black background, bright neon green text, and monospace font styling
2. WHEN a user selects the "Soft Serenity" theme THEN the Application SHALL apply pastel pink and cream white colors with rounded aesthetics
3. WHEN a user selects the "Deep Ocean" theme THEN the Application SHALL apply dark blue, teal, and white text styling
4. WHEN a theme is changed THEN the Application SHALL update all background colors, card colors, text colors, and accent colors immediately
5. WHEN a theme is selected THEN the Application SHALL persist the theme preference to Firebase associated with the user profile

### Requirement 13: Responsive Design

**User Story:** As a user, I want the application to work seamlessly on mobile devices, so that I can track activities on the go.

#### Acceptance Criteria

1. WHEN the application is viewed on a mobile device THEN the Application SHALL display all content in a single-column responsive layout
2. WHEN the application is viewed on a mobile device THEN the Application SHALL ensure all buttons and interactive elements are touch-friendly with minimum 44px touch targets
3. WHEN the application is viewed on different screen sizes THEN the Application SHALL maintain readability and usability without horizontal scrolling
4. WHEN activity cards are displayed on mobile THEN the Application SHALL stack them vertically with appropriate spacing
5. WHEN the verification interface is displayed on mobile THEN the Application SHALL optimize the layout for single-handed operation

### Requirement 14: Data Persistence and Synchronization

**User Story:** As a user, I want my data to persist and synchronize across devices, so that I can access my activities from anywhere.

#### Acceptance Criteria

1. WHEN the application loads THEN the Backend Service SHALL retrieve all family group data from Firebase
2. WHEN the application loads THEN the Backend Service SHALL retrieve all activities and log entries for the user's family group
3. WHEN data changes in Firebase THEN the Application SHALL receive real-time updates and refresh the display
4. WHEN the Backend Service cannot connect to Firebase THEN the Application SHALL display an error message and retry the connection
5. WHEN Firebase data is corrupted THEN the Backend Service SHALL handle the error gracefully and log the issue for investigation

### Requirement 15: Backend API Architecture

**User Story:** As a system architect, I want a Python-based backend service handling business logic, so that the application maintains separation of concerns and security.

#### Acceptance Criteria

1. WHEN the Application needs to create an activity THEN the Application SHALL send a request to the Backend Service API endpoint
2. WHEN the Backend Service receives a request THEN the Backend Service SHALL validate the user's authentication token before processing
3. WHEN the Backend Service processes a request THEN the Backend Service SHALL enforce role-based access control rules
4. WHEN the Backend Service completes an operation THEN the Backend Service SHALL return appropriate HTTP status codes and response data
5. WHEN the Backend Service encounters an error THEN the Backend Service SHALL return descriptive error messages and log the error details

### Requirement 16: Real-Time Notifications

**User Story:** As a parent user, I want to receive notifications when my children log activities, so that I can verify them promptly.

#### Acceptance Criteria

1. WHEN a child logs an activity THEN the Application SHALL display a notification badge on the parent's verification interface
2. WHEN pending verifications exist THEN the Application SHALL show the count of pending items in the parent dashboard header
3. WHEN a parent approves or rejects a log entry THEN the Application SHALL update the notification count immediately
4. WHEN all pending verifications are processed THEN the Application SHALL clear the notification badge
5. WHEN a child's activity is verified THEN the Application SHALL update the child's dashboard in real-time without requiring a page refresh

### Requirement 17: Data Validation and Security

**User Story:** As a system administrator, I want all user inputs validated and sanitized, so that the application remains secure and data integrity is maintained.

#### Acceptance Criteria

1. WHEN the Backend Service receives user input THEN the Backend Service SHALL validate all fields against expected data types and formats
2. WHEN the Backend Service detects invalid input THEN the Backend Service SHALL reject the request and return specific validation error messages
3. WHEN storing data in Firebase THEN the Backend Service SHALL sanitize all string inputs to prevent injection attacks
4. WHEN a user attempts to access another family's data THEN the Backend Service SHALL verify family membership and reject unauthorized requests
5. WHEN Firebase security rules are evaluated THEN Firebase SHALL enforce that users can only read and write data for their own family group

### Requirement 18: Account Deletion

**User Story:** As a user, I want to delete my account if I made a mistake during registration, so that I can remove my data and start over if needed.

#### Acceptance Criteria

1. WHEN a user accesses account settings THEN the Application SHALL display a delete account option
2. WHEN a user initiates account deletion THEN the Application SHALL display a confirmation dialog warning about data loss
3. WHEN a user confirms account deletion THEN the Backend Service SHALL remove the user profile from Firebase
4. WHEN a parent user deletes their account THEN the Backend Service SHALL transfer family group ownership to another parent or delete the group if no other parents exist
5. WHEN an account is deleted THEN the Application SHALL sign out the user and redirect to the login page

