from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, ValidationError
from typing import Literal, Dict
from datetime import datetime
from services.firebase_service import firebase_service
from middleware.auth import verify_token, get_current_user
from models.user import User
from utils.validation import (
    validate_role,
    sanitize_string,
    handle_validation_error
)
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/auth", tags=["authentication"])


class SetRoleRequest(BaseModel):
    """Request model for setting user role"""
    role: Literal["parent", "child"]
    
    class Config:
        json_schema_extra = {
            "example": {
                "role": "parent"
            }
        }


class SetRoleResponse(BaseModel):
    """Response model for set role endpoint"""
    success: bool
    user: User


class UserProfileResponse(BaseModel):
    """Response model for user profile endpoint"""
    user: User


class DeleteAccountResponse(BaseModel):
    """Response model for account deletion"""
    success: bool
    message: str


class GuestLoginRequest(BaseModel):
    """Request model for guest login"""
    role: Literal["parent", "child"]
    display_name: str = "Guest User"
    
    class Config:
        json_schema_extra = {
            "example": {
                "role": "parent",
                "display_name": "Guest Parent"
            }
        }


class GuestLoginResponse(BaseModel):
    """Response model for guest login"""
    success: bool
    user: User
    guest_token: str


@router.post("/set-role", response_model=SetRoleResponse, status_code=status.HTTP_201_CREATED)
async def set_user_role(
    request: SetRoleRequest,
    token_data: Dict = Depends(verify_token)
):
    """
    Set role for first-time user
    
    Validates: Requirements 1.4 - Backend Service creates user profile with selected role
    
    Args:
        request: SetRoleRequest containing the selected role
        token_data: Decoded Firebase token from authentication
        
    Returns:
        SetRoleResponse with success status and user data
        
    Raises:
        HTTPException: 400 if user already has a role set
        HTTPException: 500 if database operation fails
    """
    try:
        uid = token_data['uid']
        email = token_data.get('email', '')
        display_name = token_data.get('name', email.split('@')[0])
        photo_url = token_data.get('picture', '')
        
        # Validate and sanitize inputs
        try:
            validate_role(request.role)
            # Sanitize user-provided strings
            sanitized_display_name = sanitize_string(display_name, max_length=100)
            sanitized_email = sanitize_string(email, max_length=255)
            sanitized_photo_url = sanitize_string(photo_url, max_length=500)
        except ValueError as e:
            logger.warning(f"Validation error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        
        db = firebase_service.get_db()
        user_ref = db.collection('users').document(uid)
        
        # Check if user already exists
        user_doc = user_ref.get()
        if user_doc.exists:
            existing_user = user_doc.to_dict()
            if existing_user.get('role'):
                logger.warning(f"User {uid} already has role: {existing_user.get('role')}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="User already has a role assigned"
                )
        
        # Create user profile with sanitized data
        user_data = {
            'uid': uid,
            'email': sanitized_email,
            'displayName': sanitized_display_name,
            'photoURL': sanitized_photo_url,
            'role': request.role,
            'familyId': None,
            'theme': 'deep-ocean',
            'createdAt': datetime.utcnow()
        }
        
        user_ref.set(user_data)
        
        logger.info(f"User profile created successfully for {uid} with role {request.role}")
        
        # Convert to User model for response
        user = User(
            uid=uid,
            email=sanitized_email,
            display_name=sanitized_display_name,
            photo_url=sanitized_photo_url,
            role=request.role,
            family_id=None,
            theme='deep-ocean',
            created_at=user_data['createdAt']
        )
        
        return SetRoleResponse(success=True, user=user)
        
    except HTTPException:
        raise
    except ValidationError as e:
        # Pydantic validation errors
        raise handle_validation_error(e)
    except ValueError as e:
        # Custom validation errors
        logger.warning(f"Validation error setting role: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error setting user role: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user profile"
        )


@router.get("/profile", response_model=UserProfileResponse)
async def get_user_profile(token_data: Dict = Depends(get_current_user)):
    """
    Get user profile for existing users
    
    Validates: Requirements 1.5 - Backend Service retrieves user profile
    
    Args:
        token_data: Decoded Firebase token from authentication
        
    Returns:
        UserProfileResponse with user data
        
    Raises:
        HTTPException: 404 if user profile not found
        HTTPException: 500 if database operation fails
    """
    try:
        uid = token_data['uid']
        
        db = firebase_service.get_db()
        user_ref = db.collection('users').document(uid)
        user_doc = user_ref.get()
        
        if not user_doc.exists:
            logger.warning(f"User profile not found for uid: {uid}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User profile not found"
            )
        
        user_data = user_doc.to_dict()
        
        # Convert Firestore timestamp to datetime if needed
        created_at = user_data.get('createdAt')
        if hasattr(created_at, 'timestamp'):
            created_at = datetime.fromtimestamp(created_at.timestamp())
        
        user = User(
            uid=user_data['uid'],
            email=user_data['email'],
            display_name=user_data['displayName'],
            photo_url=user_data['photoURL'],
            role=user_data['role'],
            family_id=user_data.get('familyId'),
            theme=user_data.get('theme', 'deep-ocean'),
            created_at=created_at
        )
        
        logger.info(f"User profile retrieved for {uid}")
        
        return UserProfileResponse(user=user)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving user profile: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user profile"
        )


@router.post("/guest-login", response_model=GuestLoginResponse, status_code=status.HTTP_201_CREATED)
async def guest_login(request: GuestLoginRequest):
    """
    Create a guest user account for testing without authentication
    
    Args:
        request: GuestLoginRequest containing role and optional display name
        
    Returns:
        GuestLoginResponse with success status, user data, and guest token
        
    Raises:
        HTTPException: 400 if validation fails
        HTTPException: 500 if database operation fails
    """
    try:
        import uuid
        
        # Generate a unique guest ID
        guest_uid = f"guest_{uuid.uuid4().hex[:12]}"
        guest_email = f"{guest_uid}@guest.local"
        
        # Validate and sanitize inputs
        try:
            validate_role(request.role)
            sanitized_display_name = sanitize_string(request.display_name, max_length=100)
        except ValueError as e:
            logger.warning(f"Validation error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        
        db = firebase_service.get_db()
        user_ref = db.collection('users').document(guest_uid)
        
        # Create guest user profile
        user_data = {
            'uid': guest_uid,
            'email': guest_email,
            'displayName': sanitized_display_name,
            'photoURL': '',
            'role': request.role,
            'familyId': None,
            'theme': 'deep-ocean',
            'createdAt': datetime.utcnow(),
            'isGuest': True
        }
        
        user_ref.set(user_data)
        
        logger.info(f"Guest user created: {guest_uid} with role {request.role}")
        
        # Convert to User model for response
        user = User(
            uid=guest_uid,
            email=guest_email,
            display_name=sanitized_display_name,
            photo_url='',
            role=request.role,
            family_id=None,
            theme='deep-ocean',
            created_at=user_data['createdAt']
        )
        
        # Create a simple guest token (just the UID for testing)
        guest_token = f"guest_token_{guest_uid}"
        
        return GuestLoginResponse(
            success=True,
            user=user,
            guest_token=guest_token
        )
        
    except HTTPException:
        raise
    except ValidationError as e:
        raise handle_validation_error(e)
    except ValueError as e:
        logger.warning(f"Validation error in guest login: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error creating guest user: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create guest user"
        )


@router.delete("/delete-account", response_model=DeleteAccountResponse)
async def delete_account(token_data: Dict = Depends(get_current_user)):
    """
    Delete user account and handle cleanup
    
    Validates: Requirements 18.3, 18.4 - Backend Service removes user profile and handles family ownership
    
    Args:
        token_data: Decoded Firebase token from authentication
        
    Returns:
        DeleteAccountResponse with success status
        
    Raises:
        HTTPException: 404 if user profile not found
        HTTPException: 500 if database operation fails
    """
    try:
        uid = token_data['uid']
        
        db = firebase_service.get_db()
        user_ref = db.collection('users').document(uid)
        user_doc = user_ref.get()
        
        if not user_doc.exists:
            logger.warning(f"User profile not found for deletion: {uid}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User profile not found"
            )
        
        user_data = user_doc.to_dict()
        family_id = user_data.get('familyId')
        user_role = user_data.get('role')
        
        # Handle family ownership transfer if user is a parent
        if family_id and user_role == 'parent':
            family_ref = db.collection('families').document(family_id)
            family_doc = family_ref.get()
            
            if family_doc.exists:
                family_data = family_doc.to_dict()
                
                # If user is the owner, handle ownership transfer
                if family_data.get('ownerId') == uid:
                    # Find another parent in the family
                    members = family_data.get('members', [])
                    other_parents = []
                    
                    for member_id in members:
                        if member_id != uid:
                            member_ref = db.collection('users').document(member_id)
                            member_doc = member_ref.get()
                            if member_doc.exists and member_doc.to_dict().get('role') == 'parent':
                                other_parents.append(member_id)
                    
                    if other_parents:
                        # Transfer ownership to another parent
                        new_owner_id = other_parents[0]
                        family_ref.update({
                            'ownerId': new_owner_id,
                            'members': [m for m in members if m != uid]
                        })
                        logger.info(f"Family {family_id} ownership transferred to {new_owner_id}")
                    else:
                        # No other parents, delete the family
                        family_ref.delete()
                        logger.info(f"Family {family_id} deleted (no other parents)")
                else:
                    # User is not owner, just remove from members
                    members = family_data.get('members', [])
                    family_ref.update({
                        'members': [m for m in members if m != uid]
                    })
        
        # Delete user profile
        user_ref.delete()
        
        logger.info(f"User account deleted successfully: {uid}")
        
        return DeleteAccountResponse(
            success=True,
            message="Account deleted successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting account: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete account"
        )
