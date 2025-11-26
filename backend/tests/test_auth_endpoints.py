"""
Unit tests for authentication endpoints

Tests the auth router endpoints including account deletion.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime
from main import app


@pytest.fixture
def client():
    """Create test client"""
    return TestClient(app)


@pytest.fixture
def mock_firebase():
    """Mock Firebase service"""
    with patch('routers.auth.firebase_service') as mock_service:
        mock_db = MagicMock()
        mock_service.get_db.return_value = mock_db
        yield mock_service, mock_db


@pytest.fixture
def mock_auth_user():
    """Mock authentication for user"""
    with patch('middleware.auth.firebase_service') as mock_service:
        mock_db = MagicMock()
        mock_service.get_db.return_value = mock_db
        
        # Mock user document
        mock_user_doc = MagicMock()
        mock_user_doc.exists = True
        mock_user_doc.to_dict.return_value = {
            'uid': 'test_user_123',
            'role': 'parent',
            'familyId': 'family_123'
        }
        
        mock_user_ref = MagicMock()
        mock_user_ref.get.return_value = mock_user_doc
        mock_db.collection.return_value.document.return_value = mock_user_ref
        
        # Mock token verification
        mock_auth = MagicMock()
        mock_auth.verify_id_token.return_value = {
            'uid': 'test_user_123',
            'email': 'test@example.com'
        }
        mock_service.get_auth.return_value = mock_auth
        
        yield mock_service


class TestDeleteAccount:
    """Test account deletion endpoint"""
    
    def test_delete_account_success_parent_with_family_transfer(
        self, client, mock_firebase, mock_auth_user
    ):
        """
        Test Requirement 18.3, 18.4: Delete parent account with family ownership transfer
        """
        mock_service, mock_db = mock_firebase
        
        # Mock user document
        mock_user_doc = MagicMock()
        mock_user_doc.exists = True
        mock_user_doc.to_dict.return_value = {
            'uid': 'test_user_123',
            'email': 'test@example.com',
            'role': 'parent',
            'familyId': 'family_123'
        }
        
        # Mock family document
        mock_family_doc = MagicMock()
        mock_family_doc.exists = True
        mock_family_doc.to_dict.return_value = {
            'ownerId': 'test_user_123',
            'members': ['test_user_123', 'other_parent_456', 'child_789']
        }
        
        # Mock other parent document
        mock_other_parent_doc = MagicMock()
        mock_other_parent_doc.exists = True
        mock_other_parent_doc.to_dict.return_value = {
            'uid': 'other_parent_456',
            'role': 'parent'
        }
        
        # Setup mock collection queries
        mock_user_ref = MagicMock()
        mock_user_ref.get.return_value = mock_user_doc
        
        mock_family_ref = MagicMock()
        mock_family_ref.get.return_value = mock_family_doc
        
        mock_other_parent_ref = MagicMock()
        mock_other_parent_ref.get.return_value = mock_other_parent_doc
        
        def mock_document(doc_id):
            if doc_id == 'test_user_123':
                return mock_user_ref
            elif doc_id == 'family_123':
                return mock_family_ref
            elif doc_id == 'other_parent_456':
                return mock_other_parent_ref
            return MagicMock()
        
        mock_collection = MagicMock()
        mock_collection.document.side_effect = mock_document
        mock_db.collection.return_value = mock_collection
        
        # Make request
        response = client.delete(
            '/api/auth/delete-account',
            headers={"Authorization": "Bearer valid_token"}
        )
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
        assert 'deleted successfully' in data['message'].lower()
        
        # Verify family ownership was transferred
        mock_family_ref.update.assert_called_once()
        update_call = mock_family_ref.update.call_args[0][0]
        assert update_call['ownerId'] == 'other_parent_456'
        assert 'test_user_123' not in update_call['members']
        
        # Verify user was deleted
        mock_user_ref.delete.assert_called_once()
    
    def test_delete_account_success_parent_no_other_parents(
        self, client, mock_firebase, mock_auth_user
    ):
        """
        Test Requirement 18.4: Delete parent account when no other parents exist
        """
        mock_service, mock_db = mock_firebase
        
        # Mock user document
        mock_user_doc = MagicMock()
        mock_user_doc.exists = True
        mock_user_doc.to_dict.return_value = {
            'uid': 'test_user_123',
            'email': 'test@example.com',
            'role': 'parent',
            'familyId': 'family_123'
        }
        
        # Mock family document
        mock_family_doc = MagicMock()
        mock_family_doc.exists = True
        mock_family_doc.to_dict.return_value = {
            'ownerId': 'test_user_123',
            'members': ['test_user_123', 'child_789']
        }
        
        # Mock child document
        mock_child_doc = MagicMock()
        mock_child_doc.exists = True
        mock_child_doc.to_dict.return_value = {
            'uid': 'child_789',
            'role': 'child'
        }
        
        # Setup mock collection queries
        mock_user_ref = MagicMock()
        mock_user_ref.get.return_value = mock_user_doc
        
        mock_family_ref = MagicMock()
        mock_family_ref.get.return_value = mock_family_doc
        
        mock_child_ref = MagicMock()
        mock_child_ref.get.return_value = mock_child_doc
        
        def mock_document(doc_id):
            if doc_id == 'test_user_123':
                return mock_user_ref
            elif doc_id == 'family_123':
                return mock_family_ref
            elif doc_id == 'child_789':
                return mock_child_ref
            return MagicMock()
        
        mock_collection = MagicMock()
        mock_collection.document.side_effect = mock_document
        mock_db.collection.return_value = mock_collection
        
        # Make request
        response = client.delete(
            '/api/auth/delete-account',
            headers={"Authorization": "Bearer valid_token"}
        )
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
        
        # Verify family was deleted (no other parents)
        mock_family_ref.delete.assert_called_once()
        
        # Verify user was deleted
        mock_user_ref.delete.assert_called_once()
    
    def test_delete_account_success_child(
        self, client, mock_firebase, mock_auth_user
    ):
        """
        Test Requirement 18.3: Delete child account
        """
        mock_service, mock_db = mock_firebase
        
        # Mock user document
        mock_user_doc = MagicMock()
        mock_user_doc.exists = True
        mock_user_doc.to_dict.return_value = {
            'uid': 'test_user_123',
            'email': 'child@example.com',
            'role': 'child',
            'familyId': None
        }
        
        # Setup mock collection queries
        mock_user_ref = MagicMock()
        mock_user_ref.get.return_value = mock_user_doc
        
        mock_collection = MagicMock()
        mock_collection.document.return_value = mock_user_ref
        mock_db.collection.return_value = mock_collection
        
        # Make request
        response = client.delete(
            '/api/auth/delete-account',
            headers={"Authorization": "Bearer valid_token"}
        )
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
        
        # Verify user was deleted
        mock_user_ref.delete.assert_called_once()
    
    def test_delete_account_user_not_found(
        self, client, mock_firebase, mock_auth_user
    ):
        """
        Test account deletion when user profile doesn't exist
        """
        mock_service, mock_db = mock_firebase
        
        # Mock user document not found
        mock_user_doc = MagicMock()
        mock_user_doc.exists = False
        
        mock_user_ref = MagicMock()
        mock_user_ref.get.return_value = mock_user_doc
        
        mock_collection = MagicMock()
        mock_collection.document.return_value = mock_user_ref
        mock_db.collection.return_value = mock_collection
        
        # Make request
        response = client.delete(
            '/api/auth/delete-account',
            headers={"Authorization": "Bearer valid_token"}
        )
        
        # Verify response
        assert response.status_code == 404
        data = response.json()
        assert 'not found' in data['detail'].lower()
