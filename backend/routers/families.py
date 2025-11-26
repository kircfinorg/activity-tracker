from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, ValidationError
from typing import Dict, List
from datetime import datetime
from services.firebase_service import firebase_service
from middleware.auth import get_current_user
from models.family import Family
from models.user import User
from utils.validation import (
    validate_invite_code,
    validate_id_format,
    handle_validation_error
)
import logging
import random
import string

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/families", tags=["families"])


def generate_invite_code(length: int = 6) -> str:
    """
    Generate a unique 6-character alphanumeric invite code
    
    Validates: Requirements 2.1 - Backend Service generates unique alphanumeric invite code
    
    Args:
        length: Length of the invite code (default 6)
        
    Returns:
        A random alphanumeric string of specified length
    """
    characters = string.ascii_uppercase + string.digits
    return ''.join(random.choice(characters) for _ in range(length))


async def ensure_unique_invite_code(db) -> str:
    """
    Generate an invite code and ensure it's unique
    
    Validates: Requirements 2.4 - Backend Service ensures code does not conflict with existing codes
    
    Args:
        db: Firestore database instance
        
    Returns:
        A unique invite code
        
    Raises:
        RuntimeError: If unable to generate unique code after max attempts
    """
    max_attempts = 10
    
    for attempt in range(max_attempts):
        code = generate_invite_code()
        
        # Check if code already exists
        families_ref = db.collection('families')
        query = families_ref.where('inviteCode', '==', code).limit(1)
        existing = list(query.stream())
        
        if not existing:
            logger.info(f"Generated unique invite code: {code}")
            return code
        
        logger.debug(f"Invite code {code} already exists, retrying (attempt {attempt + 1}/{max_attempts})")
    
    logger.error(f"Failed to generate unique invite code after {max_attempts} attempts")
    raise RuntimeError("Failed to generate unique invite code")


class CreateFamilyResponse(BaseModel):
    """Response model for family creation"""
    family_id: str
    invite_code: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "family_id": "family123",
                "invite_code": "ABC123"
            }
        }


class JoinFamilyRequest(BaseModel):
    """Request model for joining a family"""
    invite_code: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "invite_code": "ABC123"
            }
        }


class JoinFamilyResponse(BaseModel):
    """Response model for joining a family"""
    success: bool
    family_id: str


class FamilyDetailsResponse(BaseModel):
    """Response model for family details"""
    family: Family
    members: List[User]


@router.post("", response_model=CreateFamilyResponse, status_code=status.HTTP_201_CREATED)
async def create_family(token_data: Dict = Depends(get_current_user)):
    """
    Create a new family group (parent only)
    
    Validates: Requirements 2.2, 2.5 - Backend Service stores group with parent as owner and member
    
    Args:
        token_data: Decoded Firebase token from authentication
        
    Returns:
        CreateFamilyResponse with family ID and invite code
        
    Raises:
        HTTPException: 403 if user is not a parent
        HTTPException: 400 if user already in a family
        HTTPException: 500 if database operation fails
    """
    try:
        uid = token_data['uid']
        
        db = firebase_service.get_db()
        
        # Get user data to check role and family membership
        user_ref = db.collection('users').document(uid)
        user_doc = user_ref.get()
        
        if not user_doc.exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User profile not found"
            )
        
        user_data = user_doc.to_dict()
        
        # Check if user is a parent
        if user_data.get('role') != 'parent':
            logger.warning(f"Non-parent user {uid} attempted to create family")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only parents can create family groups"
            )
        
        # Check if user already in a family
        if user_data.get('familyId'):
            logger.warning(f"User {uid} already in family {user_data.get('familyId')}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User already belongs to a family group"
            )
        
        # Generate unique invite code
        invite_code = await ensure_unique_invite_code(db)
        
        # Create family document
        family_ref = db.collection('families').document()
        family_id = family_ref.id
        
        family_data = {
            'id': family_id,
            'inviteCode': invite_code,
            'ownerId': uid,
            'members': [uid],
            'createdAt': datetime.utcnow()
        }
        
        family_ref.set(family_data)
        
        # Update user's familyId
        user_ref.update({'familyId': family_id})
        
        logger.info(f"Family {family_id} created by user {uid} with invite code {invite_code}")
        
        return CreateFamilyResponse(
            family_id=family_id,
            invite_code=invite_code
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating family: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create family group"
        )


@router.post("/join", response_model=JoinFamilyResponse)
async def join_family(
    request: JoinFamilyRequest,
    token_data: Dict = Depends(get_current_user)
):
    """
    Join an existing family using invite code
    
    Validates: Requirements 3.1, 3.2, 3.5 - Backend Service validates code and adds user to family
    Validates: Requirements 17.1, 17.2 - Input validation and error messages
    
    Args:
        request: JoinFamilyRequest containing the invite code
        token_data: Decoded Firebase token from authentication
        
    Returns:
        JoinFamilyResponse with success status and family ID
        
    Raises:
        HTTPException: 400 if invite code is invalid or user already in a family
        HTTPException: 500 if database operation fails
    """
    try:
        uid = token_data['uid']
        
        # Validate and normalize invite code
        try:
            invite_code = validate_invite_code(request.invite_code)
        except ValueError as e:
            logger.warning(f"Validation error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        
        db = firebase_service.get_db()
        
        # Get user data to check family membership
        user_ref = db.collection('users').document(uid)
        user_doc = user_ref.get()
        
        if not user_doc.exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User profile not found"
            )
        
        user_data = user_doc.to_dict()
        
        # Check if user already in a family
        if user_data.get('familyId'):
            logger.warning(f"User {uid} already in family {user_data.get('familyId')}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User already belongs to a family group"
            )
        
        # Find family by invite code
        families_ref = db.collection('families')
        query = families_ref.where('inviteCode', '==', invite_code).limit(1)
        families = list(query.stream())
        
        if not families:
            logger.warning(f"Invalid invite code attempted: {invite_code}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired invite code"
            )
        
        family_doc = families[0]
        family_data = family_doc.to_dict()
        family_id = family_data['id']
        
        # Add user to family members
        members = family_data.get('members', [])
        if uid not in members:
            members.append(uid)
            family_doc.reference.update({'members': members})
        
        # Update user's familyId
        user_ref.update({'familyId': family_id})
        
        logger.info(f"User {uid} joined family {family_id} using invite code {invite_code}")
        
        return JoinFamilyResponse(
            success=True,
            family_id=family_id
        )
        
    except HTTPException:
        raise
    except ValidationError as e:
        # Pydantic validation errors
        raise handle_validation_error(e)
    except ValueError as e:
        # Custom validation errors
        logger.warning(f"Validation error joining family: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error joining family: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to join family group"
        )


@router.get("/{family_id}", response_model=FamilyDetailsResponse)
async def get_family_details(
    family_id: str,
    token_data: Dict = Depends(get_current_user)
):
    """
    Get family group details and members
    
    Validates: Requirements 9.1 - Backend Service returns family info and member list
    
    Args:
        family_id: The family group ID
        token_data: Decoded Firebase token from authentication
        
    Returns:
        FamilyDetailsResponse with family data and member list
        
    Raises:
        HTTPException: 403 if user is not a member of the family
        HTTPException: 404 if family not found
        HTTPException: 500 if database operation fails
    """
    try:
        uid = token_data['uid']
        
        db = firebase_service.get_db()
        
        # Verify family membership
        if not firebase_service.verify_family_membership(uid, family_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this family's data"
            )
        
        # Get family data
        family_ref = db.collection('families').document(family_id)
        family_doc = family_ref.get()
        
        if not family_doc.exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Family group not found"
            )
        
        family_data = family_doc.to_dict()
        
        # Convert Firestore timestamp to datetime
        created_at = family_data.get('createdAt')
        if hasattr(created_at, 'timestamp'):
            created_at = datetime.fromtimestamp(created_at.timestamp())
        
        family = Family(
            id=family_data['id'],
            invite_code=family_data['inviteCode'],
            owner_id=family_data['ownerId'],
            members=family_data.get('members', []),
            created_at=created_at
        )
        
        # Get member details
        members = []
        for member_id in family_data.get('members', []):
            member_ref = db.collection('users').document(member_id)
            member_doc = member_ref.get()
            
            if member_doc.exists:
                member_data = member_doc.to_dict()
                
                # Convert Firestore timestamp
                member_created_at = member_data.get('createdAt')
                if hasattr(member_created_at, 'timestamp'):
                    member_created_at = datetime.fromtimestamp(member_created_at.timestamp())
                
                member = User(
                    uid=member_data['uid'],
                    email=member_data['email'],
                    display_name=member_data['displayName'],
                    photo_url=member_data['photoURL'],
                    role=member_data['role'],
                    family_id=member_data.get('familyId'),
                    theme=member_data.get('theme', 'deep-ocean'),
                    created_at=member_created_at
                )
                members.append(member)
        
        logger.info(f"Family details retrieved for {family_id} by user {uid}")
        
        return FamilyDetailsResponse(
            family=family,
            members=members
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving family details: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve family details"
        )
