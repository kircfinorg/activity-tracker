"""
Unit tests for authentication middleware

These tests verify the authentication token validation logic.
"""
import pytest
from fastapi import HTTPException
from unittest.mock import Mock, patch, MagicMock
from fastapi.security import HTTPAuthorizationCredentials

# Mock Firebase before importing middleware
with patch('services.firebase_service.firebase_admin'):
    with patch('services.firebase_service.firestore'):
        with patch('services.firebase_service.auth'):
            from middleware.auth import verify_token, require_role


class TestVerifyToken:
    """Test suite for verify_token function"""
    
    @pytest.mark.asyncio
    @patch('middleware.auth.firebase_service')
    async def test_verify_token_success(self, mock_firebase_service):
        """Test successful token verification"""
        # Arrange
        mock_auth = Mock()
        mock_auth.verify_id_token.return_value = {
            'uid': 'test-user-123',
            'email': 'test@example.com'
        }
        mock_firebase_service.get_auth.return_value = mock_auth
        
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials="valid-token"
        )
        
        # Act
        result = await verify_token(credentials)
        
        # Assert
        assert result['uid'] == 'test-user-123'
        assert result['email'] == 'test@example.com'
        mock_auth.verify_id_token.assert_called_once_with("valid-token")
    
    @pytest.mark.asyncio
    @patch('middleware.auth.firebase_service')
    async def test_verify_token_invalid(self, mock_firebase_service):
        """Test token verification with invalid token"""
        # Arrange
        mock_auth = Mock()
        mock_auth.InvalidIdTokenError = Exception
        mock_auth.verify_id_token.side_effect = mock_auth.InvalidIdTokenError("Invalid token")
        mock_firebase_service.get_auth.return_value = mock_auth
        
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials="invalid-token"
        )
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await verify_token(credentials)
        
        assert exc_info.value.status_code == 401
    
    @pytest.mark.asyncio
    @patch('middleware.auth.firebase_service')
    async def test_verify_token_expired(self, mock_firebase_service):
        """Test token verification with expired token"""
        # Arrange
        mock_auth = Mock()
        mock_auth.ExpiredIdTokenError = Exception
        mock_auth.verify_id_token.side_effect = mock_auth.ExpiredIdTokenError("Token expired")
        mock_firebase_service.get_auth.return_value = mock_auth
        
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials="expired-token"
        )
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await verify_token(credentials)
        
        assert exc_info.value.status_code == 401
        assert "expired" in str(exc_info.value.detail).lower()


class TestRequireRole:
    """Test suite for require_role function"""
    
    @pytest.mark.asyncio
    @patch('middleware.auth.firebase_service')
    async def test_require_role_parent_success(self, mock_firebase_service):
        """Test role verification for parent user"""
        # Arrange
        mock_db = Mock()
        mock_doc = Mock()
        mock_doc.exists = True
        mock_doc.to_dict.return_value = {
            'role': 'parent',
            'familyId': 'family-123'
        }
        mock_db.collection.return_value.document.return_value.get.return_value = mock_doc
        mock_firebase_service.get_db.return_value = mock_db
        
        token_data = {'uid': 'user-123', 'email': 'parent@example.com'}
        
        # Act
        result = await require_role('parent', token_data)
        
        # Assert
        assert result['role'] == 'parent'
        assert result['family_id'] == 'family-123'
    
    @pytest.mark.asyncio
    @patch('middleware.auth.firebase_service')
    async def test_require_role_insufficient_permissions(self, mock_firebase_service):
        """Test role verification when user has wrong role"""
        # Arrange
        mock_db = Mock()
        mock_doc = Mock()
        mock_doc.exists = True
        mock_doc.to_dict.return_value = {
            'role': 'child',
            'familyId': 'family-123'
        }
        mock_db.collection.return_value.document.return_value.get.return_value = mock_doc
        mock_firebase_service.get_db.return_value = mock_db
        
        token_data = {'uid': 'user-123', 'email': 'child@example.com'}
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await require_role('parent', token_data)
        
        assert exc_info.value.status_code == 403
    
    @pytest.mark.asyncio
    @patch('middleware.auth.firebase_service')
    async def test_require_role_user_not_found(self, mock_firebase_service):
        """Test role verification when user document doesn't exist"""
        # Arrange
        mock_db = Mock()
        mock_doc = Mock()
        mock_doc.exists = False
        mock_db.collection.return_value.document.return_value.get.return_value = mock_doc
        mock_firebase_service.get_db.return_value = mock_db
        
        token_data = {'uid': 'nonexistent-user', 'email': 'test@example.com'}
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await require_role('parent', token_data)
        
        assert exc_info.value.status_code == 404
