from fastapi import APIRouter, HTTPException, status, Depends
from typing import Dict, List
from middleware.auth import get_current_user
from badge_definitions import get_all_badges, get_badge_by_id
from services.gamification_service import gamification_service
from services.firebase_service import firebase_service
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/badges", tags=["badges"])


@router.get("/all")
async def get_badges():
    """
    Get all available badge definitions
    
    Returns:
        Dict of all badges with their requirements
    """
    try:
        badges = get_all_badges()
        return {"badges": badges}
    except Exception as e:
        logger.error(f"Error getting badges: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve badges"
        )


@router.get("/user/{user_id}")
async def get_user_badges(
    user_id: str,
    token_data: Dict = Depends(get_current_user)
):
    """
    Get badges earned by a specific user
    
    Args:
        user_id: The user ID to get badges for
        token_data: Decoded token from authentication
        
    Returns:
        Dict with earned badges and progress
    """
    try:
        # Verify user can access this data
        if token_data['uid'] != user_id:
            # Check if same family
            db = firebase_service.get_db()
            user_ref = db.collection('users').document(token_data['uid'])
            user_doc = user_ref.get()
            
            if user_doc.exists:
                requester_family = user_doc.to_dict().get('familyId')
                target_user_ref = db.collection('users').document(user_id)
                target_user_doc = target_user_ref.get()
                
                if target_user_doc.exists:
                    target_family = target_user_doc.to_dict().get('familyId')
                    if requester_family != target_family:
                        raise HTTPException(
                            status_code=status.HTTP_403_FORBIDDEN,
                            detail="Access denied"
                        )
        
        db = firebase_service.get_db()
        
        # Get user's earned badges
        user_badges_ref = db.collection('user_badges').document(user_id)
        user_badges_doc = user_badges_ref.get()
        
        if user_badges_doc.exists:
            earned_badges = user_badges_doc.to_dict().get('badges', {})
        else:
            earned_badges = {}
        
        # Get all badge definitions
        all_badges = get_all_badges()
        
        # Combine earned status with definitions
        badges_with_status = {}
        for badge_id, badge_def in all_badges.items():
            badge_info = {**badge_def}
            if badge_id in earned_badges:
                badge_info['earned'] = True
                earned_at = earned_badges[badge_id].get('earnedAt')
                if hasattr(earned_at, 'timestamp'):
                    earned_at = datetime.fromtimestamp(earned_at.timestamp())
                badge_info['earnedAt'] = earned_at.isoformat() if earned_at else None
            else:
                badge_info['earned'] = False
                badge_info['earnedAt'] = None
            
            badges_with_status[badge_id] = badge_info
        
        # Get user stats for progress calculation
        stats_ref = db.collection('user_stats').document(user_id)
        stats_doc = stats_ref.get()
        stats = stats_doc.to_dict() if stats_doc.exists else {}
        
        return {
            "badges": badges_with_status,
            "total_earned": len(earned_badges),
            "total_available": len(all_badges),
            "stats": stats
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user badges: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user badges"
        )


@router.post("/check/{user_id}")
async def check_badges(
    user_id: str,
    token_data: Dict = Depends(get_current_user)
):
    """
    Check if user has earned any new badges
    
    Args:
        user_id: The user ID to check badges for
        token_data: Decoded token from authentication
        
    Returns:
        List of newly earned badges
    """
    try:
        # Verify user can trigger this check
        if token_data['uid'] != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Can only check your own badges"
            )
        
        newly_earned = await gamification_service.check_and_award_badges(user_id)
        
        return {
            "newly_earned": newly_earned,
            "count": len(newly_earned)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error checking badges: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to check badges"
        )


@router.get("/stats/{user_id}")
async def get_user_stats(
    user_id: str,
    token_data: Dict = Depends(get_current_user)
):
    """
    Get user's gamification stats (level, XP, streak, etc.)
    
    Args:
        user_id: The user ID to get stats for
        token_data: Decoded token from authentication
        
    Returns:
        User's gamification statistics
    """
    try:
        # Verify access
        if token_data['uid'] != user_id:
            # Check if same family
            db = firebase_service.get_db()
            user_ref = db.collection('users').document(token_data['uid'])
            user_doc = user_ref.get()
            
            if user_doc.exists:
                requester_family = user_doc.to_dict().get('familyId')
                target_user_ref = db.collection('users').document(user_id)
                target_user_doc = target_user_ref.get()
                
                if target_user_doc.exists:
                    target_family = target_user_doc.to_dict().get('familyId')
                    if requester_family != target_family:
                        raise HTTPException(
                            status_code=status.HTTP_403_FORBIDDEN,
                            detail="Access denied"
                        )
        
        db = firebase_service.get_db()
        stats_ref = db.collection('user_stats').document(user_id)
        stats_doc = stats_ref.get()
        
        if not stats_doc.exists:
            # Return default stats
            return {
                "level": 1,
                "experiencePoints": 0,
                "totalExperience": 0,
                "currentStreak": 0,
                "longestStreak": 0,
                "totalActivitiesLogged": 0,
                "totalEarnings": 0.0,
                "badgesEarned": 0,
                "xpToNextLevel": 100,
                "progressPercentage": 0
            }
        
        stats = stats_doc.to_dict()
        current_level = stats.get('level', 1)
        current_xp = stats.get('experiencePoints', 0)
        
        # Calculate XP to next level
        xp_to_next = gamification_service.calculate_xp_to_next_level(current_level)
        progress_percentage = (current_xp / xp_to_next * 100) if xp_to_next > 0 else 0
        
        return {
            **stats,
            "xpToNextLevel": xp_to_next,
            "progressPercentage": round(progress_percentage, 1)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user stats: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user stats"
        )
