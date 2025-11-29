from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, Field, ValidationError
from typing import Dict, List, Literal
from datetime import datetime
from services.firebase_service import firebase_service
from middleware.auth import get_current_user, require_child, require_parent
from models.log_entry import LogEntry
from utils.validation import (
    validate_id_format,
    validate_units,
    validate_verification_status,
    handle_validation_error
)
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/logs", tags=["logs"])


class CreateLogRequest(BaseModel):
    """Request model for creating a log entry"""
    activity_id: str
    units: int = Field(gt=0, description="Units must be a positive value")
    
    class Config:
        json_schema_extra = {
            "example": {
                "activity_id": "activity123",
                "units": 1
            }
        }


class CreateLogResponse(BaseModel):
    """Response model for log creation"""
    log: LogEntry


class GetPendingLogsResponse(BaseModel):
    """Response model for getting pending logs"""
    logs: List[LogEntry]


class VerifyLogRequest(BaseModel):
    """Request model for verifying a log entry"""
    status: Literal["approved", "rejected"]
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "approved"
            }
        }


class VerifyLogResponse(BaseModel):
    """Response model for log verification"""
    log: LogEntry


@router.post("", response_model=CreateLogResponse, status_code=status.HTTP_201_CREATED)
async def create_log(
    request: CreateLogRequest,
    user_data: Dict = Depends(require_child)
):
    """
    Create a log entry (child only)
    
    Validates: Requirements 6.1, 6.2, 6.3 - Backend Service creates log entry with timestamp and pending status
    Validates: Requirements 17.1, 17.2 - Input validation and error messages
    
    Args:
        request: CreateLogRequest containing activity_id and units
        user_data: Decoded Firebase token from authentication (child only)
        
    Returns:
        CreateLogResponse with created log entry data
        
    Raises:
        HTTPException: 404 if activity not found
        HTTPException: 403 if user is not a member of the activity's family
        HTTPException: 400 if validation fails
        HTTPException: 500 if database operation fails
    """
    try:
        uid = user_data['uid']
        activity_id = request.activity_id
        
        # Validate input data
        try:
            validate_id_format(activity_id, "Activity ID")
            validate_units(request.units)
        except ValueError as e:
            logger.warning(f"Validation error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        
        db = firebase_service.get_db()
        
        # Get activity to verify it exists and get family_id
        activity_ref = db.collection('activities').document(activity_id)
        activity_doc = activity_ref.get()
        
        if not activity_doc.exists:
            logger.warning(f"Activity {activity_id} not found for log creation")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Activity not found"
            )
        
        activity_data = activity_doc.to_dict()
        family_id = activity_data.get('familyId')
        
        # Verify family membership
        if not firebase_service.verify_family_membership(uid, family_id):
            logger.warning(f"User {uid} attempted to log activity {activity_id} without family membership")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this family's data"
            )
        
        # Create log entry document
        log_ref = db.collection('logs').document()
        log_id = log_ref.id
        
        # Create log entry with current timestamp and pending status
        current_time = datetime.utcnow()
        
        log_entry = LogEntry(
            id=log_id,
            activity_id=activity_id,
            user_id=uid,
            family_id=family_id,
            units=request.units,
            timestamp=current_time,
            verification_status="pending",
            verified_by=None,
            verified_at=None
        )
        
        # Convert to dict for Firestore
        log_data = {
            'id': log_entry.id,
            'activityId': log_entry.activity_id,
            'userId': log_entry.user_id,
            'familyId': log_entry.family_id,
            'units': log_entry.units,
            'timestamp': log_entry.timestamp,
            'verificationStatus': log_entry.verification_status,
            'verifiedBy': log_entry.verified_by,
            'verifiedAt': log_entry.verified_at
        }
        
        log_ref.set(log_data)
        
        logger.info(f"Log entry {log_id} created by user {uid} for activity {activity_id}")
        
        # 🎮 GAMIFICATION: Award XP, update streak, check badges
        try:
            from services.gamification_service import gamification_service
            
            # Award base XP for logging activity
            await gamification_service.award_xp(uid, 5, "activity_logged")
            
            # Update streak
            await gamification_service.update_streak(uid)
            
            # Increment activity count
            await gamification_service.increment_activity_count(uid)
            
            # Check for new badges
            await gamification_service.check_and_award_badges(uid)
            
            logger.info(f"Gamification updated for user {uid}")
        except Exception as e:
            # Don't fail the request if gamification fails
            logger.error(f"Error updating gamification: {str(e)}")
        
        return CreateLogResponse(log=log_entry)
        
    except HTTPException:
        raise
    except ValidationError as e:
        # Pydantic validation errors
        raise handle_validation_error(e)
    except ValueError as e:
        # Custom validation errors
        logger.warning(f"Validation error creating log entry: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error creating log entry: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create log entry"
        )



@router.get("/{family_id}/pending", response_model=GetPendingLogsResponse)
async def get_pending_logs(
    family_id: str,
    user_data: Dict = Depends(require_parent)
):
    """
    Get pending log entries for verification (parent only)
    
    Validates: Requirements 7.1, 9.3 - Backend Service retrieves pending log entries
    
    Args:
        family_id: ID of the family group
        user_data: Decoded Firebase token from authentication (parent only)
        
    Returns:
        GetPendingLogsResponse with list of pending log entries
        
    Raises:
        HTTPException: 403 if user is not a member of the family
        HTTPException: 500 if database operation fails
    """
    try:
        uid = user_data['uid']
        
        # Verify family membership
        if not firebase_service.verify_family_membership(uid, family_id):
            logger.warning(f"User {uid} attempted to access pending logs for family {family_id} without membership")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this family's data"
            )
        
        db = firebase_service.get_db()
        
        # Query pending log entries for the family
        logs_ref = db.collection('logs')
        query = logs_ref.where('familyId', '==', family_id).where('verificationStatus', '==', 'pending')
        
        # Get all pending logs
        pending_logs = []
        for doc in query.stream():
            log_data = doc.to_dict()
            
            # Convert Firestore field names to Python model field names
            log_entry = LogEntry(
                id=log_data.get('id'),
                activity_id=log_data.get('activityId'),
                user_id=log_data.get('userId'),
                family_id=log_data.get('familyId'),
                units=log_data.get('units'),
                timestamp=log_data.get('timestamp'),
                verification_status=log_data.get('verificationStatus'),
                verified_by=log_data.get('verifiedBy'),
                verified_at=log_data.get('verifiedAt')
            )
            pending_logs.append(log_entry)
        
        logger.info(f"Retrieved {len(pending_logs)} pending logs for family {family_id}")
        
        return GetPendingLogsResponse(logs=pending_logs)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving pending logs: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve pending logs"
        )


@router.patch("/{log_id}/verify", response_model=VerifyLogResponse)
async def verify_log(
    log_id: str,
    request: VerifyLogRequest,
    user_data: Dict = Depends(require_parent)
):
    """
    Approve or reject a log entry (parent only)
    
    Validates: Requirements 7.2, 7.3 - Backend Service updates verification status
    Validates: Requirements 17.1, 17.2 - Input validation and error messages
    
    Args:
        log_id: ID of the log entry to verify
        request: VerifyLogRequest containing status (approved or rejected)
        user_data: Decoded Firebase token from authentication (parent only)
        
    Returns:
        VerifyLogResponse with updated log entry
        
    Raises:
        HTTPException: 404 if log entry not found
        HTTPException: 403 if user is not a member of the log's family
        HTTPException: 400 if log is already verified
        HTTPException: 500 if database operation fails
    """
    try:
        uid = user_data['uid']
        
        # Validate input data
        try:
            validate_id_format(log_id, "Log ID")
            validate_verification_status(request.status)
        except ValueError as e:
            logger.warning(f"Validation error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        
        db = firebase_service.get_db()
        
        # Get the log entry
        log_ref = db.collection('logs').document(log_id)
        log_doc = log_ref.get()
        
        if not log_doc.exists:
            logger.warning(f"Log entry {log_id} not found for verification")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Log entry not found"
            )
        
        log_data = log_doc.to_dict()
        family_id = log_data.get('familyId')
        
        # Verify family membership
        if not firebase_service.verify_family_membership(uid, family_id):
            logger.warning(f"User {uid} attempted to verify log {log_id} without family membership")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this family's data"
            )
        
        # Check if log is already verified
        current_status = log_data.get('verificationStatus')
        if current_status != 'pending':
            logger.warning(f"Attempted to verify log {log_id} with status {current_status}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Log entry is already {current_status}"
            )
        
        # Update verification status
        current_time = datetime.utcnow()
        
        update_data = {
            'verificationStatus': request.status,
            'verifiedBy': uid,
            'verifiedAt': current_time
        }
        
        log_ref.update(update_data)
        
        # Get updated log entry
        updated_log_doc = log_ref.get()
        updated_log_data = updated_log_doc.to_dict()
        
        # Convert to LogEntry model
        log_entry = LogEntry(
            id=updated_log_data.get('id'),
            activity_id=updated_log_data.get('activityId'),
            user_id=updated_log_data.get('userId'),
            family_id=updated_log_data.get('familyId'),
            units=updated_log_data.get('units'),
            timestamp=updated_log_data.get('timestamp'),
            verification_status=updated_log_data.get('verificationStatus'),
            verified_by=updated_log_data.get('verifiedBy'),
            verified_at=updated_log_data.get('verifiedAt')
        )
        
        logger.info(f"Log entry {log_id} verified as {request.status} by user {uid}")
        
        # 🎮 GAMIFICATION: Award XP for approved earnings
        if request.status == "approved":
            try:
                from services.gamification_service import gamification_service
                
                # Get activity to calculate earnings
                activity_ref = db.collection('activities').document(log_entry.activity_id)
                activity_doc = activity_ref.get()
                
                if activity_doc.exists:
                    activity_data = activity_doc.to_dict()
                    rate = activity_data.get('rate', 0)
                    earnings = rate * log_entry.units
                    
                    # Award XP based on earnings ($1 = 10 XP)
                    xp_amount = gamification_service.calculate_xp_for_earnings(earnings)
                    await gamification_service.award_xp(log_entry.user_id, xp_amount, "earnings")
                    
                    # Add to total earnings
                    await gamification_service.add_to_total_earnings(log_entry.user_id, earnings)
                    
                    # Check for new badges
                    await gamification_service.check_and_award_badges(log_entry.user_id)
                    
                    logger.info(f"Awarded {xp_amount} XP to user {log_entry.user_id} for ${earnings:.2f} earnings")
            except Exception as e:
                logger.error(f"Error updating gamification on approval: {str(e)}")
        
        return VerifyLogResponse(log=log_entry)
        
    except HTTPException:
        raise
    except ValidationError as e:
        # Pydantic validation errors
        raise handle_validation_error(e)
    except ValueError as e:
        # Custom validation errors
        logger.warning(f"Validation error verifying log: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error verifying log entry: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to verify log entry"
        )
