from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, Field, ValidationError
from typing import Dict, List
from datetime import datetime
from services.firebase_service import firebase_service
from middleware.auth import get_current_user, require_parent
from models.activity import Activity
from utils.validation import (
    validate_and_sanitize_activity_data,
    validate_id_format,
    handle_validation_error
)
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/activities", tags=["activities"])


class CreateActivityRequest(BaseModel):
    """Request model for creating an activity"""
    family_id: str
    name: str = Field(min_length=1, description="Activity name must not be empty")
    unit: str = Field(min_length=1, description="Unit must not be empty")
    rate: float = Field(gt=0, description="Rate must be a positive value")
    
    class Config:
        json_schema_extra = {
            "example": {
                "family_id": "family123",
                "name": "Reading",
                "unit": "Pages",
                "rate": 0.10
            }
        }


class CreateActivityResponse(BaseModel):
    """Response model for activity creation"""
    activity: Activity


class GetActivitiesResponse(BaseModel):
    """Response model for getting activities"""
    activities: List[Activity]


class DeleteActivityResponse(BaseModel):
    """Response model for activity deletion"""
    success: bool
    message: str


@router.post("", response_model=CreateActivityResponse, status_code=status.HTTP_201_CREATED)
async def create_activity(
    request: CreateActivityRequest,
    user_data: Dict = Depends(require_parent)
):
    """
    Create a new activity (parent only)
    
    Validates: Requirements 5.1, 5.2, 5.3, 5.4 - Backend Service creates activity with validation
    Validates: Requirements 17.1, 17.2, 17.3 - Input validation, error messages, and sanitization
    
    Args:
        request: CreateActivityRequest containing activity details
        user_data: Decoded Firebase token from authentication (parent only)
        
    Returns:
        CreateActivityResponse with created activity data
        
    Raises:
        HTTPException: 403 if user is not a member of the family
        HTTPException: 400 if validation fails
        HTTPException: 500 if database operation fails
    """
    try:
        uid = user_data['uid']
        family_id = request.family_id
        
        # Validate and sanitize input data
        try:
            validate_id_format(family_id, "Family ID")
            sanitized_name, sanitized_unit, validated_rate = validate_and_sanitize_activity_data(
                request.name,
                request.unit,
                request.rate
            )
        except ValueError as e:
            logger.warning(f"Validation error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        
        db = firebase_service.get_db()
        
        # Verify family membership
        if not firebase_service.verify_family_membership(uid, family_id):
            logger.warning(f"User {uid} attempted to create activity for family {family_id} without membership")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this family's data"
            )
        
        # Create activity document
        activity_ref = db.collection('activities').document()
        activity_id = activity_ref.id
        
        # Create activity using Pydantic model with sanitized data
        activity = Activity(
            id=activity_id,
            family_id=family_id,
            name=sanitized_name,
            unit=sanitized_unit,
            rate=validated_rate,
            created_by=uid,
            created_at=datetime.utcnow()
        )
        
        # Convert to dict for Firestore
        activity_data = {
            'id': activity.id,
            'familyId': activity.family_id,
            'name': activity.name,
            'unit': activity.unit,
            'rate': activity.rate,
            'createdBy': activity.created_by,
            'createdAt': activity.created_at
        }
        
        activity_ref.set(activity_data)
        
        logger.info(f"Activity {activity_id} created by user {uid} for family {family_id}")
        
        return CreateActivityResponse(activity=activity)
        
    except HTTPException:
        raise
    except ValidationError as e:
        # Pydantic validation errors
        raise handle_validation_error(e)
    except ValueError as e:
        # Custom validation errors
        logger.warning(f"Validation error creating activity: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error creating activity: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create activity"
        )


@router.get("/{family_id}", response_model=GetActivitiesResponse)
async def get_activities(
    family_id: str,
    user_data: Dict = Depends(get_current_user)
):
    """
    Get all activities for a family
    
    Validates: Requirements 5.1 - Backend Service retrieves activities for family
    
    Args:
        family_id: The family group ID
        user_data: Decoded Firebase token from authentication
        
    Returns:
        GetActivitiesResponse with list of activities
        
    Raises:
        HTTPException: 403 if user is not a member of the family
        HTTPException: 500 if database operation fails
    """
    try:
        uid = user_data['uid']
        
        # Verify family membership
        if not firebase_service.verify_family_membership(uid, family_id):
            logger.warning(f"User {uid} attempted to access activities for family {family_id} without membership")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this family's data"
            )
        
        db = firebase_service.get_db()
        
        # Query activities for the family
        activities_ref = db.collection('activities')
        query = activities_ref.where('familyId', '==', family_id)
        activity_docs = query.stream()
        
        activities = []
        for doc in activity_docs:
            activity_data = doc.to_dict()
            
            # Convert Firestore timestamp to datetime
            created_at = activity_data.get('createdAt')
            if hasattr(created_at, 'timestamp'):
                created_at = datetime.fromtimestamp(created_at.timestamp())
            
            activity = Activity(
                id=activity_data['id'],
                family_id=activity_data['familyId'],
                name=activity_data['name'],
                unit=activity_data['unit'],
                rate=activity_data['rate'],
                created_by=activity_data['createdBy'],
                created_at=created_at
            )
            activities.append(activity)
        
        logger.info(f"Retrieved {len(activities)} activities for family {family_id}")
        
        return GetActivitiesResponse(activities=activities)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving activities: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve activities"
        )


@router.delete("/{activity_id}", response_model=DeleteActivityResponse)
async def delete_activity(
    activity_id: str,
    user_data: Dict = Depends(require_parent)
):
    """
    Delete an activity and cascade delete all associated log entries (parent only)
    
    Validates: Requirements 11.1, 11.2, 11.3, 11.4 - Backend Service removes activity and associated logs
    
    Args:
        activity_id: The activity ID to delete
        user_data: Decoded Firebase token from authentication (parent only)
        
    Returns:
        DeleteActivityResponse with success status
        
    Raises:
        HTTPException: 403 if user is not a member of the family
        HTTPException: 404 if activity not found
        HTTPException: 500 if database operation fails
    """
    try:
        uid = user_data['uid']
        
        db = firebase_service.get_db()
        
        # Get activity to verify family membership
        activity_ref = db.collection('activities').document(activity_id)
        activity_doc = activity_ref.get()
        
        if not activity_doc.exists:
            logger.warning(f"Activity {activity_id} not found for deletion")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Activity not found"
            )
        
        activity_data = activity_doc.to_dict()
        family_id = activity_data.get('familyId')
        
        # Verify family membership
        if not firebase_service.verify_family_membership(uid, family_id):
            logger.warning(f"User {uid} attempted to delete activity {activity_id} without family membership")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this family's data"
            )
        
        # Cascade delete: Find and delete all log entries associated with this activity
        logs_ref = db.collection('logs')
        logs_query = logs_ref.where('activityId', '==', activity_id)
        log_docs = logs_query.stream()
        
        deleted_logs_count = 0
        affected_users = set()
        
        for log_doc in log_docs:
            log_data = log_doc.to_dict()
            affected_users.add(log_data.get('userId'))
            log_doc.reference.delete()
            deleted_logs_count += 1
        
        # Delete the activity
        activity_ref.delete()
        
        logger.info(
            f"Activity {activity_id} deleted by user {uid}. "
            f"Cascade deleted {deleted_logs_count} log entries. "
            f"Affected users: {affected_users}"
        )
        
        # Note: Earnings recalculation will happen automatically when the frontend
        # queries for earnings, as it will no longer find the deleted log entries
        
        return DeleteActivityResponse(
            success=True,
            message=f"Activity deleted successfully. {deleted_logs_count} log entries removed."
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting activity: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete activity"
        )
