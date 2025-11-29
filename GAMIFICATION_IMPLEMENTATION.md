# Gamification Features Implementation Plan

## 🎯 Phase 1: Core Features (Implementing Now)

### 1. Achievement Badges System ✅
**Status:** Models created, backend routes next

**Components:**
- Badge model with rarity levels
- 20+ predefined badges
- Badge checking service
- Badge unlock animations (frontend)
- Badge collection display

**Database:**
- `badges` collection (predefined)
- `user_badges` collection (earned badges)
- User profile includes badge count

### 2. Streak Tracking ✅
**Status:** Model created, integration next

**Components:**
- Streak model
- Daily streak checker
- Streak bonus calculator
- Streak display with fire emoji
- Streak milestone badges

**Logic:**
- Updates on every activity log
- Resets if no activity for 24+ hours
- Awards bonus XP for milestones

### 3. Level System ✅
**Status:** Model created, XP calculation next

**Components:**
- Level model with XP tracking
- Exponential XP requirements
- Level-up animations
- Theme unlocks at levels
- Progress bar display

**XP Awards:**
- $1 earned = 10 XP
- Activity logged = 5 XP
- Streak bonus = level * 10 XP

### 4. Savings Goals ✅
**Status:** Model created, CRUD operations next

**Components:**
- Savings goal model
- Goal creation form
- Progress tracking
- Goal completion celebration
- Multiple active goals support

**Features:**
- Custom icons
- Progress percentage
- Remaining amount calculator
- Completion notifications

### 5. Family Leaderboard
**Status:** Planning

**Components:**
- Leaderboard calculation service
- Weekly/monthly views
- Real-time ranking updates
- Crown for #1 position
- Activity and earnings stats

### 6. Activity Icons/Emojis
**Status:** Quick win

**Components:**
- Emoji picker in activity creation
- Icon display in activity cards
- Color coding support
- Default icons by category

### 7. Bonus Multipliers
**Status:** Planning

**Components:**
- Multiplier configuration
- Weekend bonus (2x)
- Special event multipliers
- Multiplier display in UI
- Automatic application

## 📊 Database Schema Updates

### New Collections:
```
user_badges/
  {userId}/
    badges/
      {badgeId}: {
        earnedAt: timestamp,
        progress: number
      }

user_stats/
  {userId}: {
    level: number,
    experiencePoints: number,
    totalExperience: number,
    currentStreak: number,
    longestStreak: number,
    lastActivityDate: timestamp,
    totalActivitiesLogged: number,
    totalEarnings: number,
    badgesEarned: number
  }

savings_goals/
  {goalId}: {
    userId: string,
    name: string,
    description: string,
    targetAmount: number,
    currentAmount: number,
    icon: string,
    createdAt: timestamp,
    completedAt: timestamp | null,
    isCompleted: boolean
  }

multipliers/
  {familyId}/
    active: {
      type: string,
      value: number,
      startDate: timestamp,
      endDate: timestamp
    }
```

### Updated Collections:
```
activities/
  + icon: string (emoji)
  + color: string (hex code)

users/
  + level: number
  + experiencePoints: number
  + currentStreak: number
  + avatar: string (emoji or URL)
```

## 🎨 Frontend Components

### New Components:
1. `BadgeCard.tsx` - Display individual badge
2. `BadgeCollection.tsx` - Grid of all badges
3. `BadgeUnlockModal.tsx` - Celebration animation
4. `StreakDisplay.tsx` - Fire emoji with count
5. `LevelProgress.tsx` - XP bar and level
6. `SavingsGoalCard.tsx` - Goal with progress bar
7. `SavingsGoalForm.tsx` - Create/edit goals
8. `Leaderboard.tsx` - Family rankings
9. `EmojiPicker.tsx` - Icon selector
10. `MultiplierBanner.tsx` - Active bonus display

### Updated Components:
- `ChildDashboard.tsx` - Add streak, level, goals
- `ParentDashboard.tsx` - Add leaderboard
- `ActivityCard.tsx` - Add icon display
- `CreateActivityForm.tsx` - Add emoji picker
- `Header.tsx` - Add level indicator

## 🔄 API Endpoints

### New Endpoints:
```
GET    /api/badges - Get all badge definitions
GET    /api/badges/user/{userId} - Get user's badges
POST   /api/badges/check/{userId} - Check for new badges

GET    /api/stats/{userId} - Get user stats
POST   /api/stats/{userId}/xp - Award XP

GET    /api/goals/{userId} - Get user's goals
POST   /api/goals - Create goal
PUT    /api/goals/{goalId} - Update goal
DELETE /api/goals/{goalId} - Delete goal
POST   /api/goals/{goalId}/contribute - Add money to goal

GET    /api/leaderboard/{familyId} - Get family rankings
GET    /api/leaderboard/{familyId}/weekly - Weekly rankings

GET    /api/multipliers/{familyId} - Get active multipliers
POST   /api/multipliers/{familyId} - Create multiplier
```

### Updated Endpoints:
```
POST /api/logs - Now awards XP, updates streak, checks badges
```

## 🎮 Implementation Order

1. ✅ Create all models
2. ✅ Create badge definitions
3. 🔄 Create user stats service
4. 🔄 Create badge checking service
5. 🔄 Update logs endpoint to award XP and update streak
6. 🔄 Create savings goals CRUD
7. 🔄 Create leaderboard calculation
8. 🔄 Build frontend components
9. 🔄 Add animations and celebrations
10. 🔄 Test and polish

## 🚀 Next Steps

Starting with backend services and API endpoints...
