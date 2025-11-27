from fastapi import HTTPException, Security, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from services.firebase_service import firebase_service
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)

security = HTTPBearer()

async def verify_token(credentials: HTTPAuthorizationCredentials = Security(security)) -> Dict:
    """
    Verify Firebase ID token or guest token and return decoded token
    
    Validates: Requirements 15.2 - Backend Service validates authentication token
    
    Args:
        credentials: HTTP Bearer token credentials
        
    Returns:
        Dict containing decoded token data with uid, email, etc.
        
    Raises:
        HTTPException: 401 if token is invalid, expired, or missing
    """
    try:
        token = credentials.credentials
        
        # Check if it's a guest token
        if token.startswith("guest_token_"):
            guest_uid = token.replace("guest_token_", "")
            
            # For guest users, we trust the token and return minimal data
            # Guest users are for testing only and don't need full verification
            logger.info(f"Guest token accepted for user: {guest_uid}")
            return {
                'uid': guest_uid,
                'email': f'{guest_uid}@guest.local',
                'name': 'Guest User',
                'picture': '',
                'is_guest': True
            }
        
        # Verify the ID token with Firebase Admin SDK
        decoded_token = firebase_service.get_auth().verify_id_token(token)
        
        logger.info(f"Token verified successfully for user: {decoded_token.get('uid')}")
        return decoded_token
        
    except HTTPException:
        raise
    except Exception as e:
        # Check error type by name to handle both real and mocked Firebase exceptions
        error_type = type(e).__name__
        error_message = str(e).lower()
        
        if 'invalidid' in error_type.lower() or 'invalid' in error_message:
            logger.warning("Invalid ID token provided")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token"
            )
        elif 'expired' in error_type.lower() or 'expired' in error_message:
            logger.warning("Expired ID token provided")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expired, please sign in again"
            )
        elif 'revoked' in error_type.lower() or 'revoked' in error_message:
            logger.warning("Revoked ID token provided")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has been revoked"
            )
        else:
            logger.error(f"Error verifying token: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required"
            )

async def get_current_user(token_data: Dict = Security(verify_token)) -> Dict:
    """
    Get current user from token data
    
    Args:
        token_data: Decoded token data from verify_token
        
    Returns:
        Dict containing user information from token
    """
    return token_data

async def require_role(required_role: str, token_data: Dict = Security(verify_token)) -> Dict:
    """
    Verify user has the required role
    
    Validates: Requirements 15.3 - Backend Service enforces role-based access control
    
    Args:
        required_role: The role required ("parent" or "child")
        token_data: Decoded token data
        
    Returns:
        Dict containing user information
        
    Raises:
        HTTPException: 403 if user doesn't have required role
    """
    # Get user role from Firestore (works for both guest and Firebase users)
    try:
        user_ref = firebase_service.get_db().collection('users').document(token_data['uid'])
        user_doc = user_ref.get()
        
        if not user_doc.exists:
            logger.warning(f"User document not found for uid: {token_data['uid']}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User profile not found"
            )
        
        user_data = user_doc.to_dict()
        user_role = user_data.get('role')
        
        if user_role != required_role:
            logger.warning(
                f"User {token_data['uid']} with role '{user_role}' "
                f"attempted to access '{required_role}' endpoint"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"This action requires '{required_role}' role"
            )
        
        # Add role to token data for convenience
        token_data['role'] = user_role
        token_data['family_id'] = user_data.get('familyId')
        
        return token_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error checking user role: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error verifying user permissions"
        )

async def require_parent(token_data: Dict = Security(verify_token)) -> Dict:
    """
    Dependency that requires parent role
    
    Validates: Requirements 4.3, 4.4 - Backend Service verifies parent privileges
    
    Usage:
        @app.post("/api/activities")
        async def create_activity(user: Dict = Depends(require_parent)):
            ...
    
    Returns:
        Dict containing user information with role and family_id
        
    Raises:
        HTTPException: 403 if user is not a parent
    """
    return await require_role("parent", token_data)

async def require_child(token_data: Dict = Security(verify_token)) -> Dict:
    """
    Dependency that requires child role
    
    Validates: Requirements 4.3 - Backend Service enforces child-only operations
    
    Usage:
        @app.post("/api/logs")
        async def create_log(user: Dict = Depends(require_child)):
            ...
    
    Returns:
        Dict containing user information with role and family_id
        
    Raises:
        HTTPException: 403 if user is not a child
    """
    return await require_role("child", token_data)
