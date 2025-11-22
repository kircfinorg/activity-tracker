import firebase_admin
from firebase_admin import credentials, firestore, auth
from config import settings
import os
import logging

logger = logging.getLogger(__name__)

class FirebaseService:
    """
    Singleton service for Firebase Admin SDK operations
    
    Provides centralized access to Firebase Authentication and Firestore
    """
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(FirebaseService, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self._initialize_firebase()
            self._initialized = True
    
    def _initialize_firebase(self):
        """
        Initialize Firebase Admin SDK
        
        Validates: Requirements 15.2 - Backend Service initializes Firebase Admin SDK
        
        Attempts to initialize with service account credentials if provided,
        otherwise falls back to default credentials (useful for Cloud Run)
        """
        if not firebase_admin._apps:
            try:
                # Check if credentials path is provided
                cred_path = settings.firebase_credentials_path
                
                if cred_path and os.path.exists(cred_path):
                    logger.info(f"Initializing Firebase with credentials from: {cred_path}")
                    cred = credentials.Certificate(cred_path)
                    firebase_admin.initialize_app(cred)
                else:
                    logger.info("Initializing Firebase with default credentials")
                    # Use default credentials (for Cloud Run or local emulator)
                    firebase_admin.initialize_app()
                
                logger.info("Firebase Admin SDK initialized successfully")
                
            except Exception as e:
                logger.error(f"Failed to initialize Firebase Admin SDK: {str(e)}")
                raise RuntimeError(
                    "Failed to initialize Firebase. Please check your credentials configuration."
                ) from e
        
        try:
            self.db = firestore.client()
            self.auth = auth
            logger.info("Firebase services (Firestore, Auth) initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Firebase services: {str(e)}")
            raise RuntimeError("Failed to initialize Firebase services") from e
    
    def get_db(self):
        """
        Get Firestore database instance
        
        Returns:
            Firestore client instance
        """
        return self.db
    
    def get_auth(self):
        """
        Get Firebase Auth instance
        
        Returns:
            Firebase Auth module
        """
        return self.auth
    
    def verify_family_membership(self, user_id: str, family_id: str) -> bool:
        """
        Verify that a user is a member of a specific family
        
        Validates: Requirements 17.4 - Backend Service verifies family membership
        
        Args:
            user_id: The user's Firebase UID
            family_id: The family group ID to check
            
        Returns:
            True if user is a member of the family, False otherwise
        """
        try:
            user_ref = self.db.collection('users').document(user_id)
            user_doc = user_ref.get()
            
            if not user_doc.exists:
                logger.warning(f"User {user_id} not found when checking family membership")
                return False
            
            user_data = user_doc.to_dict()
            user_family_id = user_data.get('familyId')
            
            is_member = user_family_id == family_id
            
            if not is_member:
                logger.warning(
                    f"User {user_id} attempted to access family {family_id} "
                    f"but belongs to family {user_family_id}"
                )
            
            return is_member
            
        except Exception as e:
            logger.error(f"Error verifying family membership: {str(e)}")
            return False

# Singleton instance
firebase_service = FirebaseService()
