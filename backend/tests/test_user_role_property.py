"""
Property-based tests for user role assignment

Feature: gamified-activity-tracker, Property 1: User role assignment on first registration
Validates: Requirements 1.4
"""

import pytest
from hypothesis import given, strategies as st, settings
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from main import app
from models.user import User


# Strategy for generating valid user data
@st.composite
def user_data_strategy(draw):
    """Generate random user data for testing"""
    # Use only ASCII alphanumeric characters for UID to avoid encoding issues in HTTP headers
    uid = draw(st.text(min_size=10, max_size=50, alphabet='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'))
    email = draw(st.emails())
    # Use ASCII characters for name
    name = draw(st.text(min_size=1, max_size=100, alphabet='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 '))
    photo_url = draw(st.from_regex(r'https?://[a-z0-9\-\.]+\.[a-z]{2,}/[a-z0-9\-\.]+\.(jpg|png)', fullmatch=True))
    role = draw(st.sampled_from(['parent', 'child']))
    
    return {
        'uid': uid,
        'email': email,
        'name': name,
        'picture': photo_url,
        'role': role
    }


class TestUserRoleAssignment:
    """
    Property 1: User role assignment on first registration
    
    For any first-time user completing Google authentication and selecting a role 
    (parent or child), the Backend Service should create a user profile in Firebase 
    with the selected role correctly assigned.
    """
    
    @given(user_data=user_data_strategy())
    @settings(max_examples=100)
    def test_user_role_assignment_property(self, user_data):
        """
        Feature: gamified-activity-tracker, Property 1: User role assignment on first registration
        
        Test that for any user data and role selection, the backend correctly creates
        a user profile with the selected role.
        """
        client = TestClient(app)
        
        # Mock Firebase Admin SDK - patch both imports
        with patch('routers.auth.firebase_service') as mock_firebase_router, \
             patch('middleware.auth.firebase_service') as mock_firebase_middleware:
            
            # Configure both mocks identically
            for mock_firebase in [mock_firebase_router, mock_firebase_middleware]:
                # Mock auth verification
                mock_auth = Mock()
                mock_auth.verify_id_token.return_value = {
                    'uid': user_data['uid'],
                    'email': user_data['email'],
                    'name': user_data['name'],
                    'picture': user_data['picture']
                }
                mock_firebase.get_auth.return_value = mock_auth
            
            # Mock Firestore - create fresh mocks for each test run
            mock_db = Mock()
            mock_user_ref = Mock()
            mock_user_doc = Mock()
            # Configure exists as a property that returns False
            type(mock_user_doc).exists = property(lambda self: False)
            mock_user_ref.get.return_value = mock_user_doc
            
            # Track what data was written
            written_data = {}
            def capture_set(data):
                written_data.clear()
                written_data.update(data)
            mock_user_ref.set.side_effect = capture_set
            
            mock_collection = Mock()
            mock_collection.document.return_value = mock_user_ref
            mock_db.collection.return_value = mock_collection
            mock_firebase_router.get_db.return_value = mock_db
            
            # Make request to set role
            response = client.post(
                '/api/auth/set-role',
                json={'role': user_data['role']},
                headers={'Authorization': f'Bearer fake_token_{user_data["uid"]}'}
            )
            
            # Verify response
            assert response.status_code == 201, f"Expected 201, got {response.status_code}: {response.json()}"
            
            response_data = response.json()
            assert response_data['success'] is True
            assert 'user' in response_data
            
            # Verify the user profile was created with correct role
            user_profile = response_data['user']
            assert user_profile['uid'] == user_data['uid']
            assert user_profile['email'] == user_data['email']
            assert user_profile['role'] == user_data['role'], \
                f"Expected role {user_data['role']}, got {user_profile['role']}"
            
            # Verify data was written to Firestore with correct role
            assert written_data['role'] == user_data['role'], \
                f"Expected role {user_data['role']} in Firestore, got {written_data.get('role')}"
            assert written_data['uid'] == user_data['uid']
            assert written_data['email'] == user_data['email']
            assert written_data['familyId'] is None  # First-time users have no family
            assert written_data['theme'] == 'deep-ocean'  # Default theme
    
    @given(user_data=user_data_strategy())
    @settings(max_examples=100)
    def test_cannot_change_existing_role(self, user_data):
        """
        Test that users cannot change their role once it's set.
        This ensures role assignment is permanent on first registration.
        """
        client = TestClient(app)
        
        # Mock Firebase Admin SDK - patch both imports
        with patch('routers.auth.firebase_service') as mock_firebase_router, \
             patch('middleware.auth.firebase_service') as mock_firebase_middleware:
            
            # Configure both mocks identically
            for mock_firebase in [mock_firebase_router, mock_firebase_middleware]:
                # Mock auth verification
                mock_auth = Mock()
                mock_auth.verify_id_token.return_value = {
                    'uid': user_data['uid'],
                    'email': user_data['email'],
                    'name': user_data['name'],
                    'picture': user_data['picture']
                }
                mock_firebase.get_auth.return_value = mock_auth
            
            # Mock Firestore - user already exists with a role
            mock_db = Mock()
            mock_user_ref = Mock()
            mock_user_doc = Mock()
            # Configure exists as a property that returns True
            type(mock_user_doc).exists = property(lambda self: True)
            
            # User already has the opposite role
            existing_role = 'child' if user_data['role'] == 'parent' else 'parent'
            mock_user_doc.to_dict.return_value = {
                'uid': user_data['uid'],
                'email': user_data['email'],
                'role': existing_role,
                'familyId': None,
                'theme': 'deep-ocean'
            }
            mock_user_ref.get.return_value = mock_user_doc
            
            mock_collection = Mock()
            mock_collection.document.return_value = mock_user_ref
            mock_db.collection.return_value = mock_collection
            mock_firebase_router.get_db.return_value = mock_db
            
            # Attempt to set role again
            response = client.post(
                '/api/auth/set-role',
                json={'role': user_data['role']},
                headers={'Authorization': f'Bearer fake_token_{user_data["uid"]}'}
            )
            
            # Should be rejected
            assert response.status_code == 400, \
                f"Expected 400 for existing user, got {response.status_code}"
            
            response_data = response.json()
            assert 'already has a role' in response_data['detail'].lower()
            
            # Verify set was never called (role wasn't changed)
            mock_user_ref.set.assert_not_called()
