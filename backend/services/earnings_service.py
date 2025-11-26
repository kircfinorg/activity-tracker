"""
Earnings calculation service

Provides functions to calculate earnings based on log entries and activity rates.
Validates: Requirements 7.4, 7.5, 8.5
"""

from datetime import datetime, timedelta
from typing import Dict, List, Tuple
from services.firebase_service import firebase_service
import logging

logger = logging.getLogger(__name__)


def calculate_earnings_for_user(
    user_id: str,
    family_id: str,
    start_time: datetime,
    end_time: datetime
) -> Tuple[float, float]:
    """
    Calculate earnings for a user within a time window.
    
    Validates: Requirements 7.4, 7.5, 8.5 - Calculate earnings based on verification status
    and time window
    
    Args:
        user_id: ID of the user to calculate earnings for
        family_id: ID of the family group
        start_time: Start of the time window (inclusive)
        end_time: End of the time window (inclusive)
        
    Returns:
        Tuple of (pending_earnings, verified_earnings)
        
    Raises:
        Exception: If database operation fails
    """
    try:
        db = firebase_service.get_db()
        
        # Query log entries for the user within the time window
        logs_ref = db.collection('logs')
        query = (logs_ref
                .where('userId', '==', user_id)
                .where('familyId', '==', family_id)
                .where('timestamp', '>=', start_time)
                .where('timestamp', '<=', end_time))
        
        # Get all activities for the family to look up rates
        activities_ref = db.collection('activities')
        activities_query = activities_ref.where('familyId', '==', family_id)
        
        # Build activity rate lookup
        activity_rates = {}
        for activity_doc in activities_query.stream():
            activity_data = activity_doc.to_dict()
            activity_rates[activity_data['id']] = activity_data['rate']
        
        # Calculate earnings
        pending_earnings = 0.0
        verified_earnings = 0.0
        
        for log_doc in query.stream():
            log_data = log_doc.to_dict()
            
            activity_id = log_data.get('activityId')
            units = log_data.get('units', 0)
            verification_status = log_data.get('verificationStatus')
            
            # Get the rate for this activity
            rate = activity_rates.get(activity_id, 0.0)
            
            # Calculate earnings for this log entry
            log_earnings = units * rate
            
            # Add to appropriate total based on verification status
            if verification_status == 'approved':
                verified_earnings += log_earnings
            elif verification_status == 'pending':
                pending_earnings += log_earnings
            # rejected logs are not counted
        
        logger.info(
            f"Calculated earnings for user {user_id}: "
            f"pending={pending_earnings}, verified={verified_earnings}"
        )
        
        return pending_earnings, verified_earnings
        
    except Exception as e:
        logger.error(f"Error calculating earnings for user {user_id}: {str(e)}")
        raise


def calculate_today_earnings(user_id: str, family_id: str) -> Tuple[float, float]:
    """
    Calculate earnings for today (current 24-hour period).
    
    Validates: Requirements 8.1 - Calculate today's earnings
    
    Args:
        user_id: ID of the user to calculate earnings for
        family_id: ID of the family group
        
    Returns:
        Tuple of (pending_earnings, verified_earnings)
    """
    # Get start and end of today in UTC
    now = datetime.utcnow()
    start_of_today = datetime(now.year, now.month, now.day, 0, 0, 0)
    end_of_today = datetime(now.year, now.month, now.day, 23, 59, 59)
    
    return calculate_earnings_for_user(user_id, family_id, start_of_today, end_of_today)


def calculate_weekly_earnings(user_id: str, family_id: str) -> Tuple[float, float]:
    """
    Calculate earnings for the last 7 days.
    
    Validates: Requirements 8.2 - Calculate weekly earnings
    
    Args:
        user_id: ID of the user to calculate earnings for
        family_id: ID of the family group
        
    Returns:
        Tuple of (pending_earnings, verified_earnings)
    """
    # Get start and end of last 7 days
    now = datetime.utcnow()
    seven_days_ago = now - timedelta(days=7)
    
    return calculate_earnings_for_user(user_id, family_id, seven_days_ago, now)
