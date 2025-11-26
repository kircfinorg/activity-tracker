"""
Earnings API endpoints

Provides endpoints for retrieving user earnings data.
Validates: Requirements 8.1, 8.2
"""

from fastapi import APIRouter, HTTPException, status, Depends
from typing import Dict
from services.firebase_service import firebase_service
from services.earnings_service import calculate_today_earnings, calculate_weekly_earnings
from middleware.auth import get_current_user
from models.earnings import Earnings
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/earnings", tags=["earnings"])


@router.get("/{user_id}/today", response_model=Earnings)
async def get_today_earnings(
    user_id: str,
    user_data: Dict = Depends(get_current_user)
):
    """
    Get today's earnings for a user.
    
    Validates: Requirements 8.1 - Display verified earnings for current 24-hour period
    
    Args:
        user_id: ID of the user to get earnings for
        user_data: Decoded Firebase token from authentication
        
    Returns:
        Earnings object with pending and verified amounts
        
    Raises:
        HTTPException: 403 if user attempts to access another user's earnings
        HTTPException: 404 if user not found
        HTTPException: 500 if database operation fails
    """
    try:
        uid = user_data['uid']
        
        # Users can only access their own earnings
        if uid != user_id:
            logger.warning(f"User {uid} attempted to access earnings for user {user_id}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only access your own earnings"
            )
        
        db = firebase_service.get_db()
        
        # Get user's family ID
        user_ref = db.collection('users').document(user_id)
        user_doc = user_ref.get()
        
        if not user_doc.exists:
            logger.warning(f"User {user_id} not found")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        user_profile = user_doc.to_dict()
        family_id = user_profile.get('familyId')
        
        if not family_id:
            # User not in a family yet, return zero earnings
            logger.info(f"User {user_id} not in a family, returning zero earnings")
            return Earnings(pending=0.0, verified=0.0)
        
        # Calculate today's earnings
        pending, verified = calculate_today_earnings(user_id, family_id)
        
        logger.info(f"Retrieved today's earnings for user {user_id}")
        
        return Earnings(pending=pending, verified=verified)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving today's earnings: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve earnings"
        )


@router.get("/{user_id}/weekly", response_model=Earnings)
async def get_weekly_earnings(
    user_id: str,
    user_data: Dict = Depends(get_current_user)
):
    """
    Get weekly earnings for a user (last 7 days).
    
    Validates: Requirements 8.2 - Display verified earnings for last 7 days
    
    Args:
        user_id: ID of the user to get earnings for
        user_data: Decoded Firebase token from authentication
        
    Returns:
        Earnings object with pending and verified amounts
        
    Raises:
        HTTPException: 403 if user attempts to access another user's earnings
        HTTPException: 404 if user not found
        HTTPException: 500 if database operation fails
    """
    try:
        uid = user_data['uid']
        
        # Users can only access their own earnings
        if uid != user_id:
            logger.warning(f"User {uid} attempted to access earnings for user {user_id}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only access your own earnings"
            )
        
        db = firebase_service.get_db()
        
        # Get user's family ID
        user_ref = db.collection('users').document(user_id)
        user_doc = user_ref.get()
        
        if not user_doc.exists:
            logger.warning(f"User {user_id} not found")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        user_profile = user_doc.to_dict()
        family_id = user_profile.get('familyId')
        
        if not family_id:
            # User not in a family yet, return zero earnings
            logger.info(f"User {user_id} not in a family, returning zero earnings")
            return Earnings(pending=0.0, verified=0.0)
        
        # Calculate weekly earnings
        pending, verified = calculate_weekly_earnings(user_id, family_id)
        
        logger.info(f"Retrieved weekly earnings for user {user_id}")
        
        return Earnings(pending=pending, verified=verified)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving weekly earnings: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve earnings"
        )
