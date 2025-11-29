"""
Gamification service for handling XP, levels, streaks, and badges
"""
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from services.firebase_service import firebase_service
from badge_definitions import get_all_badges, get_badge_by_id

logger = logging.getLogger(__name__)

class GamificationService:
    
    @staticmethod
    def calculate_xp_for_earnings(amount: float) -> int:
        """Calculate XP from earnings: $1 = 10 XP"""
        return int(amount * 10)
    
    @staticmethod
    def calculate_xp_to_next_level(current_level: int) -> int:
        """Calculate XP needed for next level (exponential growth)"""
        return int(100 * (current_level ** 1.5))
    
    @staticmethod
    async def award_xp(user_id: str, xp_amount: int, reason: str = "activity") -> Dict:
        """
        Award XP to a user and handle level ups
        
        Returns dict with level_up info if applicable
        """
        try:
            db = firebase_service.get_db()
            stats_ref = db.collection('user_stats').document(user_id)
            stats_doc = stats_ref.get()
            
            if not stats_doc.exists:
                # Initialize stats for new user
                stats_data = {
                    'userId': user_id,
                    'level': 1,
                    'experiencePoints': 0,
                    'totalExperience': 0,
                    'currentStreak': 0,
                    'longestStreak': 0,
                    'lastActivityDate': None,
                    'totalActivitiesLogged': 0,
                    'totalEarnings': 0.0,
                    'badgesEarned': 0
                }
                stats_ref.set(stats_data)
                stats = stats_data
            else:
                stats = stats_doc.to_dict()
            
            # Add XP
            current_xp = stats.get('experiencePoints', 0)
            total_xp = stats.get('totalExperience', 0)
            current_level = stats.get('level', 1)
            
            new_xp = current_xp + xp_amount
            new_total_xp = total_xp + xp_amount
            
            # Check for level up
            level_up = False
            new_level = current_level
            xp_to_next = GamificationService.calculate_xp_to_next_level(current_level)
            
            while new_xp >= xp_to_next:
                new_xp -= xp_to_next
                new_level += 1
                level_up = True
                xp_to_next = GamificationService.calculate_xp_to_next_level(new_level)
                logger.info(f"User {user_id} leveled up to {new_level}!")
            
            # Update stats
            stats_ref.update({
                'experiencePoints': new_xp,
                'totalExperience': new_total_xp,
                'level': new_level
            })
            
            result = {
                'xp_awarded': xp_amount,
                'new_xp': new_xp,
                'new_total_xp': new_total_xp,
                'level': new_level,
                'level_up': level_up,
                'xp_to_next_level': xp_to_next
            }
            
            if level_up:
                result['old_level'] = current_level
                result['new_level'] = new_level
            
            return result
            
        except Exception as e:
            logger.error(f"Error awarding XP: {str(e)}")
            return {'error': str(e)}
    
    @staticmethod
    async def update_streak(user_id: str) -> Dict:
        """
        Update user's activity streak
        
        Returns dict with streak info and any bonuses
        """
        try:
            db = firebase_service.get_db()
            stats_ref = db.collection('user_stats').document(user_id)
            stats_doc = stats_ref.get()
            
            if not stats_doc.exists:
                # Initialize with first activity
                stats_ref.set({
                    'userId': user_id,
                    'currentStreak': 1,
                    'longestStreak': 1,
                    'lastActivityDate': datetime.utcnow(),
                    'level': 1,
                    'experiencePoints': 0,
                    'totalExperience': 0,
                    'totalActivitiesLogged': 1,
                    'totalEarnings': 0.0,
                    'badgesEarned': 0
                })
                return {
                    'current_streak': 1,
                    'longest_streak': 1,
                    'streak_bonus_xp': 0,
                    'streak_continued': False
                }
            
            stats = stats_doc.to_dict()
            last_activity = stats.get('lastActivityDate')
            current_streak = stats.get('currentStreak', 0)
            longest_streak = stats.get('longestStreak', 0)
            
            now = datetime.utcnow()
            
            # Convert Firestore timestamp if needed
            if hasattr(last_activity, 'timestamp'):
                last_activity = datetime.fromtimestamp(last_activity.timestamp())
            
            # Check if this is a new day
            if last_activity:
                time_diff = now - last_activity
                
                if time_diff.days == 0:
                    # Same day, no streak change
                    return {
                        'current_streak': current_streak,
                        'longest_streak': longest_streak,
                        'streak_bonus_xp': 0,
                        'streak_continued': False
                    }
                elif time_diff.days == 1:
                    # Next day, continue streak
                    current_streak += 1
                    streak_continued = True
                else:
                    # Missed a day, reset streak
                    current_streak = 1
                    streak_continued = False
            else:
                current_streak = 1
                streak_continued = False
            
            # Update longest streak
            if current_streak > longest_streak:
                longest_streak = current_streak
            
            # Calculate streak bonus XP (every 7 days)
            streak_bonus_xp = 0
            if current_streak % 7 == 0:
                streak_bonus_xp = current_streak * 10
                logger.info(f"User {user_id} earned {streak_bonus_xp} bonus XP for {current_streak}-day streak!")
            
            # Update stats
            stats_ref.update({
                'currentStreak': current_streak,
                'longestStreak': longest_streak,
                'lastActivityDate': now
            })
            
            # Award bonus XP if applicable
            if streak_bonus_xp > 0:
                await GamificationService.award_xp(user_id, streak_bonus_xp, "streak_bonus")
            
            return {
                'current_streak': current_streak,
                'longest_streak': longest_streak,
                'streak_bonus_xp': streak_bonus_xp,
                'streak_continued': streak_continued
            }
            
        except Exception as e:
            logger.error(f"Error updating streak: {str(e)}")
            return {'error': str(e)}
    
    @staticmethod
    async def check_and_award_badges(user_id: str) -> List[Dict]:
        """
        Check if user has earned any new badges
        
        Returns list of newly earned badges
        """
        try:
            db = firebase_service.get_db()
            
            # Get user stats
            stats_ref = db.collection('user_stats').document(user_id)
            stats_doc = stats_ref.get()
            
            if not stats_doc.exists:
                return []
            
            stats = stats_doc.to_dict()
            
            # Get user's current badges
            user_badges_ref = db.collection('user_badges').document(user_id)
            user_badges_doc = user_badges_ref.get()
            
            if user_badges_doc.exists:
                earned_badges = user_badges_doc.to_dict().get('badges', {})
            else:
                earned_badges = {}
                user_badges_ref.set({'userId': user_id, 'badges': {}})
            
            # Check all badges
            all_badges = get_all_badges()
            newly_earned = []
            
            for badge_id, badge_def in all_badges.items():
                # Skip if already earned
                if badge_id in earned_badges:
                    continue
                
                # Check if requirements are met
                earned = False
                req_type = badge_def['requirement_type']
                req_value = badge_def['requirement_value']
                
                if req_type == 'activity_count':
                    earned = stats.get('totalActivitiesLogged', 0) >= req_value
                elif req_type == 'total_earnings':
                    earned = stats.get('totalEarnings', 0) >= req_value
                elif req_type == 'current_streak':
                    earned = stats.get('currentStreak', 0) >= req_value
                elif req_type == 'pages_read':
                    # TODO: Implement pages tracking
                    earned = False
                elif req_type == 'goals_completed':
                    # TODO: Implement goals tracking
                    earned = False
                
                if earned:
                    # Award badge
                    earned_badges[badge_id] = {
                        'earnedAt': datetime.utcnow(),
                        'progress': 100
                    }
                    newly_earned.append(badge_def)
                    logger.info(f"User {user_id} earned badge: {badge_def['name']}")
            
            # Update user badges
            if newly_earned:
                user_badges_ref.update({'badges': earned_badges})
                stats_ref.update({'badgesEarned': len(earned_badges)})
            
            return newly_earned
            
        except Exception as e:
            logger.error(f"Error checking badges: {str(e)}")
            return []
    
    @staticmethod
    async def increment_activity_count(user_id: str):
        """Increment total activities logged counter"""
        try:
            db = firebase_service.get_db()
            stats_ref = db.collection('user_stats').document(user_id)
            stats_doc = stats_ref.get()
            
            if stats_doc.exists:
                current_count = stats_doc.to_dict().get('totalActivitiesLogged', 0)
                stats_ref.update({'totalActivitiesLogged': current_count + 1})
            else:
                stats_ref.set({
                    'userId': user_id,
                    'totalActivitiesLogged': 1,
                    'level': 1,
                    'experiencePoints': 0,
                    'totalExperience': 0,
                    'currentStreak': 0,
                    'longestStreak': 0,
                    'totalEarnings': 0.0,
                    'badgesEarned': 0
                })
        except Exception as e:
            logger.error(f"Error incrementing activity count: {str(e)}")
    
    @staticmethod
    async def add_to_total_earnings(user_id: str, amount: float):
        """Add to total earnings counter"""
        try:
            db = firebase_service.get_db()
            stats_ref = db.collection('user_stats').document(user_id)
            stats_doc = stats_ref.get()
            
            if stats_doc.exists:
                current_earnings = stats_doc.to_dict().get('totalEarnings', 0.0)
                stats_ref.update({'totalEarnings': current_earnings + amount})
            else:
                stats_ref.set({
                    'userId': user_id,
                    'totalEarnings': amount,
                    'level': 1,
                    'experiencePoints': 0,
                    'totalExperience': 0,
                    'currentStreak': 0,
                    'longestStreak': 0,
                    'totalActivitiesLogged': 0,
                    'badgesEarned': 0
                })
        except Exception as e:
            logger.error(f"Error adding to total earnings: {str(e)}")

gamification_service = GamificationService()
