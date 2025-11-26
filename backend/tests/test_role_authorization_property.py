"""
Property-based tests for role-based authorization

Feature: gamified-activity-tracker, Property 7: Role-based authorization enforcement
Feature: gamified-activity-tracker, Property 8: Parent authorization verification
Feature: gamified-activity-tracker, Property 24: Role-based access control enforcement
Validates: Requirements 4.3, 4.4, 15.3
"""

import pytest
from hypothesis import given, strategies as st, settings, assume
from fastapi import HTTPException, status
from unittest.mock import Mock, patch, MagicMock
from fastapi.security import HTTPAuthorizationCredentials
import asyncio
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


# Strategy for generating user IDs
user_id_strategy = st.text(
    min_size=10, 
    max_size=50, 
    alphabet='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
)

# Strategy for generating family IDs
family_id_strategy = st.text(
    min_size=10, 
    max_size=50, 
    alphabet='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
)

# Strategy for generating email addresses
email_strategy = st.emails()

# Strategy for generating roles
role_strategy = st.sampled_from(['parent', 'child'])

# Strategy for generating user data with role
@st.composite
def user_with_role_strategy(draw):
    """Generate random user data with a specific role"""
    return {
        'uid': draw(user_id_strategy),
        'email': draw(email_strategy),
        'role': draw(role_strategy),
        'familyId': draw(st.one_of(st.none(), family_id_strategy))
    }


class TestRoleBasedAuthorizationEnforcement:
    """
    Property 7: Role-based authorization enforcement
    
    For any child user attempting to perform parent-only operations 
    (verify activities, delete activities, delete family group), 
    the Backend Service should reject the request and return an authorization error.
    """
    
    @given(user_data=user_with_role_strategy())
    @settings(max_examples=100)
    def test_child_cannot_access_parent_endpoints(self, user_data):
        """
        Feature: gamified-activity-tracker, Property 7: Role-based authorization enforcement
        
        Test that for any child user, attempting to access parent-only operations
        results in a 403 Forbidden error.
        
        This validates that the require_parent middleware correctly rejects
        all child users regardless of their other attributes.
        """
        # Only test when user is a child
        assume(user_data['role'] == 'child')
        
        # Mock Firebase to return child user data
        with patch('middleware.auth.firebase_service') as mock_firebase:
            mock_db = Mock()
            mock_user_ref = Mock()
            mock_user_doc = Mock()
            
            # Configure user document to exist and return child role
            type(mock_user_doc).exists = property(lambda self: True)
            mock_user_doc.to_dict.return_value = {
                'uid': user_data['uid'],
                'email': user_data['email'],
                'role': 'child',  # Child role
                'familyId': user_data['familyId']
            }
            
            mock_user_ref.get.return_value = mock_user_doc
            mock_collection = Mock()
            mock_collection.document.return_value = mock_user_ref
            mock_db.collection.return_value = mock_collection
            mock_firebase.get_db.return_value = mock_db
            
            # Import after mocking
            from middleware.auth import require_parent
            
            # Create token data (simulating verified token)
            token_data = {
                'uid': user_data['uid'],
                'email': user_data['email']
            }
            
            # Act & Assert - child should be rejected
            with pytest.raises(HTTPException) as exc_info:
                asyncio.run(require_parent(token_data))
            
            # Verify 403 Forbidden status for all child users
            assert exc_info.value.status_code == 403, \
                f"Expected 403 for child user, got {exc_info.value.status_code}"
            
            # Verify error message mentions parent role requirement
            assert 'parent' in str(exc_info.value.detail).lower(), \
                f"Error message should mention 'parent' role requirement"
    
    @given(user_data=user_with_role_strategy())
    @settings(max_examples=100)
    def test_parent_can_access_parent_endpoints(self, user_data):
        """
        Test that for any parent user, accessing parent-only operations
        is allowed and returns user data with role information.
        
        This validates that the require_parent middleware correctly accepts
        all parent users.
        """
        # Only test when user is a parent
        assume(user_data['role'] == 'parent')
        
        # Mock Firebase to return parent user data
        with patch('middleware.auth.firebase_service') as mock_firebase:
            mock_db = Mock()
            mock_user_ref = Mock()
            mock_user_doc = Mock()
            
            # Configure user document to exist and return parent role
            type(mock_user_doc).exists = property(lambda self: True)
            mock_user_doc.to_dict.return_value = {
                'uid': user_data['uid'],
                'email': user_data['email'],
                'role': 'parent',  # Parent role
                'familyId': user_data['familyId']
            }
            
            mock_user_ref.get.return_value = mock_user_doc
            mock_collection = Mock()
            mock_collection.document.return_value = mock_user_ref
            mock_db.collection.return_value = mock_collection
            mock_firebase.get_db.return_value = mock_db
            
            # Import after mocking
            from middleware.auth import require_parent
            
            # Create token data (simulating verified token)
            token_data = {
                'uid': user_data['uid'],
                'email': user_data['email']
            }
            
            # Act - parent should be accepted
            result = asyncio.run(require_parent(token_data))
            
            # Assert - should return token data with role
            assert result['uid'] == user_data['uid']
            assert result['role'] == 'parent'
            assert result['family_id'] == user_data['familyId']


class TestParentAuthorizationVerification:
    """
    Property 8: Parent authorization verification
    
    For any user attempting to delete a family group, the Backend Service 
    should verify the user has parent privileges before processing the request.
    """
    
    @given(user_data=user_with_role_strategy())
    @settings(max_examples=100)
    def test_parent_privilege_verification_before_operations(self, user_data):
        """
        Feature: gamified-activity-tracker, Property 8: Parent authorization verification
        
        Test that for any user attempting parent-only operations,
        the system verifies parent privileges by checking the role in Firestore.
        
        This validates Requirements 4.4 - Backend Service verifies parent privileges
        """
        # Mock Firebase to return user data
        with patch('middleware.auth.firebase_service') as mock_firebase:
            mock_db = Mock()
            mock_user_ref = Mock()
            mock_user_doc = Mock()
            
            # Configure user document to exist
            type(mock_user_doc).exists = property(lambda self: True)
            mock_user_doc.to_dict.return_value = {
                'uid': user_data['uid'],
                'email': user_data['email'],
                'role': user_data['role'],
                'familyId': user_data['familyId']
            }
            
            mock_user_ref.get.return_value = mock_user_doc
            mock_collection = Mock()
            mock_collection.document.return_value = mock_user_ref
            mock_db.collection.return_value = mock_collection
            mock_firebase.get_db.return_value = mock_db
            
            # Import after mocking
            from middleware.auth import require_parent
            
            # Create token data
            token_data = {
                'uid': user_data['uid'],
                'email': user_data['email']
            }
            
            # Act
            if user_data['role'] == 'parent':
                # Parent should be accepted
                result = asyncio.run(require_parent(token_data))
                assert result['role'] == 'parent'
                
                # Verify that Firestore was queried to check role
                mock_db.collection.assert_called_with('users')
                mock_collection.document.assert_called_with(user_data['uid'])
                mock_user_ref.get.assert_called_once()
            else:
                # Child should be rejected
                with pytest.raises(HTTPException) as exc_info:
                    asyncio.run(require_parent(token_data))
                
                assert exc_info.value.status_code == 403
                
                # Verify that Firestore was queried before rejection
                mock_db.collection.assert_called_with('users')
                mock_collection.document.assert_called_with(user_data['uid'])
                mock_user_ref.get.assert_called_once()
    
    @given(user_id=user_id_strategy, email=email_strategy)
    @settings(max_examples=100)
    def test_missing_user_profile_rejected(self, user_id, email):
        """
        Test that users without a profile in Firestore are rejected
        when attempting parent-only operations.
        
        This ensures privilege verification fails safely when user data is missing.
        """
        # Mock Firebase to return non-existent user
        with patch('middleware.auth.firebase_service') as mock_firebase:
            mock_db = Mock()
            mock_user_ref = Mock()
            mock_user_doc = Mock()
            
            # Configure user document to NOT exist
            type(mock_user_doc).exists = property(lambda self: False)
            
            mock_user_ref.get.return_value = mock_user_doc
            mock_collection = Mock()
            mock_collection.document.return_value = mock_user_ref
            mock_db.collection.return_value = mock_collection
            mock_firebase.get_db.return_value = mock_db
            
            # Import after mocking
            from middleware.auth import require_parent
            
            # Create token data
            token_data = {
                'uid': user_id,
                'email': email
            }
            
            # Act & Assert - should be rejected with 404
            with pytest.raises(HTTPException) as exc_info:
                asyncio.run(require_parent(token_data))
            
            assert exc_info.value.status_code == 404
            assert 'not found' in str(exc_info.value.detail).lower()


class TestRoleBasedAccessControlEnforcement:
    """
    Property 24: Role-based access control enforcement
    
    For any request processed by the Backend Service, the service should 
    enforce role-based access control rules, ensuring users can only perform 
    operations permitted for their role.
    """
    
    @given(user_data=user_with_role_strategy())
    @settings(max_examples=100)
    def test_rbac_enforcement_for_all_roles(self, user_data):
        """
        Feature: gamified-activity-tracker, Property 24: Role-based access control enforcement
        
        Test that for any user with any role, the RBAC system correctly
        enforces access control by checking the role from Firestore.
        
        This validates Requirements 15.3 - Backend Service enforces role-based access control
        """
        # Mock Firebase to return user data
        with patch('middleware.auth.firebase_service') as mock_firebase:
            mock_db = Mock()
            mock_user_ref = Mock()
            mock_user_doc = Mock()
            
            # Configure user document
            type(mock_user_doc).exists = property(lambda self: True)
            mock_user_doc.to_dict.return_value = {
                'uid': user_data['uid'],
                'email': user_data['email'],
                'role': user_data['role'],
                'familyId': user_data['familyId']
            }
            
            mock_user_ref.get.return_value = mock_user_doc
            mock_collection = Mock()
            mock_collection.document.return_value = mock_user_ref
            mock_db.collection.return_value = mock_collection
            mock_firebase.get_db.return_value = mock_db
            
            # Import after mocking
            from middleware.auth import require_role
            
            # Create token data
            token_data = {
                'uid': user_data['uid'],
                'email': user_data['email']
            }
            
            # Test requiring the user's actual role - should succeed
            result = asyncio.run(require_role(user_data['role'], token_data))
            assert result['role'] == user_data['role']
            assert result['uid'] == user_data['uid']
            
            # Test requiring the opposite role - should fail
            opposite_role = 'child' if user_data['role'] == 'parent' else 'parent'
            with pytest.raises(HTTPException) as exc_info:
                asyncio.run(require_role(opposite_role, token_data))
            
            assert exc_info.value.status_code == 403
            assert opposite_role in str(exc_info.value.detail).lower()
    
    @given(user_data=user_with_role_strategy())
    @settings(max_examples=100)
    def test_child_specific_operations_require_child_role(self, user_data):
        """
        Test that child-only operations correctly require child role.
        
        This ensures bidirectional RBAC - not just parent-only, but also
        child-only operations are protected.
        """
        # Mock Firebase to return user data
        with patch('middleware.auth.firebase_service') as mock_firebase:
            mock_db = Mock()
            mock_user_ref = Mock()
            mock_user_doc = Mock()
            
            # Configure user document
            type(mock_user_doc).exists = property(lambda self: True)
            mock_user_doc.to_dict.return_value = {
                'uid': user_data['uid'],
                'email': user_data['email'],
                'role': user_data['role'],
                'familyId': user_data['familyId']
            }
            
            mock_user_ref.get.return_value = mock_user_doc
            mock_collection = Mock()
            mock_collection.document.return_value = mock_user_ref
            mock_db.collection.return_value = mock_collection
            mock_firebase.get_db.return_value = mock_db
            
            # Import after mocking
            from middleware.auth import require_child
            
            # Create token data
            token_data = {
                'uid': user_data['uid'],
                'email': user_data['email']
            }
            
            # Act
            if user_data['role'] == 'child':
                # Child should be accepted
                result = asyncio.run(require_child(token_data))
                assert result['role'] == 'child'
                assert result['uid'] == user_data['uid']
            else:
                # Parent should be rejected
                with pytest.raises(HTTPException) as exc_info:
                    asyncio.run(require_child(token_data))
                
                assert exc_info.value.status_code == 403
                assert 'child' in str(exc_info.value.detail).lower()
    
    @given(
        user_data=user_with_role_strategy(),
        required_role=role_strategy
    )
    @settings(max_examples=100)
    def test_rbac_consistency_across_all_role_combinations(self, user_data, required_role):
        """
        Test that RBAC enforcement is consistent for all combinations
        of user roles and required roles.
        
        This is a comprehensive property test that validates the core
        RBAC logic works correctly for any role combination.
        """
        # Mock Firebase to return user data
        with patch('middleware.auth.firebase_service') as mock_firebase:
            mock_db = Mock()
            mock_user_ref = Mock()
            mock_user_doc = Mock()
            
            # Configure user document
            type(mock_user_doc).exists = property(lambda self: True)
            mock_user_doc.to_dict.return_value = {
                'uid': user_data['uid'],
                'email': user_data['email'],
                'role': user_data['role'],
                'familyId': user_data['familyId']
            }
            
            mock_user_ref.get.return_value = mock_user_doc
            mock_collection = Mock()
            mock_collection.document.return_value = mock_user_ref
            mock_db.collection.return_value = mock_collection
            mock_firebase.get_db.return_value = mock_db
            
            # Import after mocking
            from middleware.auth import require_role
            
            # Create token data
            token_data = {
                'uid': user_data['uid'],
                'email': user_data['email']
            }
            
            # Act
            if user_data['role'] == required_role:
                # Roles match - should succeed
                result = asyncio.run(require_role(required_role, token_data))
                assert result['role'] == user_data['role']
                assert result['uid'] == user_data['uid']
                assert result['family_id'] == user_data['familyId']
            else:
                # Roles don't match - should fail with 403
                with pytest.raises(HTTPException) as exc_info:
                    asyncio.run(require_role(required_role, token_data))
                
                assert exc_info.value.status_code == 403
                assert required_role in str(exc_info.value.detail).lower()
