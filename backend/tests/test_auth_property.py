"""
Property-based tests for authentication middleware

Feature: gamified-activity-tracker, Property 23: Authentication token validation
Validates: Requirements 15.2
"""
import pytest
from hypothesis import given, strategies as st, settings
from fastapi import HTTPException, status
from unittest.mock import Mock, patch, MagicMock
from fastapi.security import HTTPAuthorizationCredentials
import asyncio


# Strategy for generating random token strings
token_strategy = st.text(
    alphabet=st.characters(
        whitelist_categories=('Lu', 'Ll', 'Nd'),
        whitelist_characters='.-_'
    ),
    min_size=10,
    max_size=500
)

# Strategy for generating valid decoded token data
valid_token_data_strategy = st.fixed_dictionaries({
    'uid': st.text(min_size=1, max_size=128),
    'email': st.emails(),
    'email_verified': st.booleans(),
    'auth_time': st.integers(min_value=1000000000, max_value=2000000000),
    'iat': st.integers(min_value=1000000000, max_value=2000000000),
    'exp': st.integers(min_value=2000000000, max_value=3000000000),
})


class TestAuthenticationTokenValidation:
    """
    Property 23: Authentication token validation
    
    For any request received by the Backend Service, the service should 
    validate the user's authentication token before processing the request.
    """
    
    @given(token_data=valid_token_data_strategy, token_string=token_strategy)
    @settings(max_examples=100)
    def test_valid_tokens_are_accepted(self, token_data, token_string):
        """
        Property: For any valid token that Firebase can verify, 
        verify_token should return the decoded token data
        
        This tests that the middleware correctly accepts and returns 
        valid token data for all valid tokens.
        """
        # Arrange
        with patch('middleware.auth.firebase_service') as mock_firebase_service:
            mock_auth = Mock()
            mock_auth.verify_id_token.return_value = token_data
            mock_firebase_service.get_auth.return_value = mock_auth
            
            # Import here to use the mocked service
            from middleware.auth import verify_token
            
            credentials = HTTPAuthorizationCredentials(
                scheme="Bearer",
                credentials=token_string
            )
            
            # Act
            import asyncio
            result = asyncio.run(verify_token(credentials))
            
            # Assert
            assert result == token_data
            assert 'uid' in result
            assert 'email' in result
            mock_auth.verify_id_token.assert_called_once_with(token_string)
    
    @given(token_string=token_strategy)
    @settings(max_examples=100)
    def test_invalid_tokens_are_rejected(self, token_string):
        """
        Property: For any token that Firebase cannot verify (invalid format, 
        expired, revoked), verify_token should raise HTTPException with 401 status
        
        This tests that the middleware correctly rejects all invalid tokens.
        """
        # Arrange
        with patch('middleware.auth.firebase_service') as mock_firebase_service:
            mock_auth = Mock()
            # Simulate Firebase rejecting the token
            mock_auth.InvalidIdTokenError = Exception
            mock_auth.verify_id_token.side_effect = mock_auth.InvalidIdTokenError("Invalid token")
            mock_firebase_service.get_auth.return_value = mock_auth
            
            from middleware.auth import verify_token
            
            credentials = HTTPAuthorizationCredentials(
                scheme="Bearer",
                credentials=token_string
            )
            
            # Act & Assert
            import asyncio
            with pytest.raises(HTTPException) as exc_info:
                asyncio.run(verify_token(credentials))
            
            # Verify 401 status code for all invalid tokens
            assert exc_info.value.status_code == 401
            mock_auth.verify_id_token.assert_called_once_with(token_string)
    
    @given(token_string=token_strategy)
    @settings(max_examples=100)
    def test_expired_tokens_are_rejected(self, token_string):
        """
        Property: For any expired token, verify_token should raise 
        HTTPException with 401 status and appropriate error message
        
        This tests that expired tokens are consistently rejected.
        """
        # Arrange
        with patch('middleware.auth.firebase_service') as mock_firebase_service:
            mock_auth = Mock()
            mock_auth.ExpiredIdTokenError = Exception
            mock_auth.verify_id_token.side_effect = mock_auth.ExpiredIdTokenError("Token expired")
            mock_firebase_service.get_auth.return_value = mock_auth
            
            from middleware.auth import verify_token
            
            credentials = HTTPAuthorizationCredentials(
                scheme="Bearer",
                credentials=token_string
            )
            
            # Act & Assert
            import asyncio
            with pytest.raises(HTTPException) as exc_info:
                asyncio.run(verify_token(credentials))
            
            assert exc_info.value.status_code == 401
            assert "expired" in str(exc_info.value.detail).lower()
    
    @given(token_string=token_strategy)
    @settings(max_examples=100)
    def test_revoked_tokens_are_rejected(self, token_string):
        """
        Property: For any revoked token, verify_token should raise 
        HTTPException with 401 status
        
        This tests that revoked tokens are consistently rejected.
        """
        # Arrange
        with patch('middleware.auth.firebase_service') as mock_firebase_service:
            mock_auth = Mock()
            mock_auth.RevokedIdTokenError = Exception
            mock_auth.verify_id_token.side_effect = mock_auth.RevokedIdTokenError("Token revoked")
            mock_firebase_service.get_auth.return_value = mock_auth
            
            from middleware.auth import verify_token
            
            credentials = HTTPAuthorizationCredentials(
                scheme="Bearer",
                credentials=token_string
            )
            
            # Act & Assert
            import asyncio
            with pytest.raises(HTTPException) as exc_info:
                asyncio.run(verify_token(credentials))
            
            assert exc_info.value.status_code == 401
            assert "revoked" in str(exc_info.value.detail).lower()
    
    @given(
        token_string=token_strategy,
        error_message=st.text(
            alphabet=st.characters(blacklist_categories=('Cc', 'Cs')),
            min_size=10,
            max_size=200
        )
    )
    @settings(max_examples=100)
    def test_all_verification_errors_return_401(self, token_string, error_message):
        """
        Property: For any error during token verification, verify_token 
        should always return 401 status code (never expose internal errors)
        
        This tests that all verification failures result in consistent 
        401 responses, maintaining security.
        """
        # Arrange
        with patch('middleware.auth.firebase_service') as mock_firebase_service:
            mock_auth = Mock()
            mock_auth.verify_id_token.side_effect = Exception(error_message)
            mock_firebase_service.get_auth.return_value = mock_auth
            
            from middleware.auth import verify_token
            
            credentials = HTTPAuthorizationCredentials(
                scheme="Bearer",
                credentials=token_string
            )
            
            # Act & Assert
            import asyncio
            with pytest.raises(HTTPException) as exc_info:
                asyncio.run(verify_token(credentials))
            
            # All errors should result in 401, never 500 or other codes
            assert exc_info.value.status_code == 401
            # Error message should be a generic message, not the internal error
            # The detail should be one of our predefined safe messages
            detail = str(exc_info.value.detail)
            assert detail in [
                "Invalid authentication token",
                "Token expired, please sign in again",
                "Token has been revoked",
                "Authentication required"
            ]
