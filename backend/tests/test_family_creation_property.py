"""
Property-based tests for family group creation

**Feature: gamified-activity-tracker, Property 3: Family group creation with owner**
**Validates: Requirements 2.2, 2.5**
"""
import pytest
from hypothesis import given, strategies as st, settings, assume
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime
import string


# Strategy for generating valid user IDs
user_id_strategy = st.text(
    alphabet=string.ascii_letters + string.digits,
    min_size=10,
    max_size=30
)

# Strategy for generating email addresses
email_strategy = st.emails()

# Strategy for generating display names
display_name_strategy = st.text(
    alphabet=string.ascii_letters + string.digits + ' ',
    min_size=1,
    max_size=50
).map(str.strip).filter(lambda x: len(x) > 0)


@settings(max_examples=100, deadline=None)
@given(
    user_id=user_id_strategy,
    email=email_strategy,
    display_name=display_name_strategy
)
def test_family_creation_owner_property(user_id, email, display_name):
    """
    Property test: For any parent user creating a family group, the Backend Service
    should store the group in Firebase with that parent as both the owner and a member
    
    **Feature: gamified-activity-tracker, Property 3: Family group creation with owner**
    **Validates: Requirements 2.2, 2.5**
    
    This test verifies that:
    1. The family is created with the parent as the owner
    2. The parent is added to the members list
    3. The family has a valid invite code
    """
    from routers.families import create_family
    from fastapi import HTTPException
    
    # Mock Firebase database
    mock_db = MagicMock()
    mock_user_ref = MagicMock()
    mock_user_doc = MagicMock()
    mock_family_ref = MagicMock()
    mock_families_collection = MagicMock()
    
    # Set up user document (parent role, no family)
    mock_user_doc.exists = True
    mock_user_doc.to_dict.return_value = {
        'uid': user_id,
        'email': email,
        'displayName': display_name,
        'role': 'parent',
        'familyId': None
    }
    mock_user_ref.get.return_value = mock_user_doc
    
    # Set up family collection to return no existing codes (all codes are unique)
    mock_families_collection.where.return_value.limit.return_value.stream.return_value = []
    
    # Set up family document creation
    family_id = f"family_{user_id[:10]}"
    mock_family_ref.id = family_id
    
    # Configure mock database
    def collection_side_effect(name):
        if name == 'users':
            mock_users_collection = MagicMock()
            mock_users_collection.document.return_value = mock_user_ref
            return mock_users_collection
        elif name == 'families':
            mock_families_collection.document.return_value = mock_family_ref
            return mock_families_collection
    
    mock_db.collection.side_effect = collection_side_effect
    
    # Mock token data
    token_data = {
        'uid': user_id,
        'email': email,
        'name': display_name
    }
    
    # Patch firebase_service
    with patch('routers.families.firebase_service') as mock_firebase_service:
        mock_firebase_service.get_db.return_value = mock_db
        
        # Call the create_family function
        try:
            import asyncio
            result = asyncio.run(create_family(token_data))
            
            # Verify the family was created
            assert mock_family_ref.set.called, "Family document should be created"
            
            # Get the family data that was set
            family_data = mock_family_ref.set.call_args[0][0]
            
            # Property 1: Owner should be the parent user
            assert family_data['ownerId'] == user_id, \
                f"Family owner should be {user_id}, got {family_data['ownerId']}"
            
            # Property 2: Parent should be in members list
            assert user_id in family_data['members'], \
                f"Parent {user_id} should be in members list {family_data['members']}"
            
            # Property 3: Members list should contain exactly one member (the parent)
            assert len(family_data['members']) == 1, \
                f"Members list should have 1 member, got {len(family_data['members'])}"
            
            # Property 4: Family should have a valid invite code
            assert 'inviteCode' in family_data, "Family should have an invite code"
            assert len(family_data['inviteCode']) == 6, \
                f"Invite code should be 6 characters, got {len(family_data['inviteCode'])}"
            
            # Property 5: User's familyId should be updated
            assert mock_user_ref.update.called, "User's familyId should be updated"
            update_data = mock_user_ref.update.call_args[0][0]
            assert update_data['familyId'] == family_id, \
                f"User's familyId should be {family_id}, got {update_data['familyId']}"
            
        except HTTPException as e:
            # Should not raise exception for valid parent user
            pytest.fail(f"Unexpected HTTPException: {e.detail}")


@settings(max_examples=100, deadline=None)
@given(
    user_id=user_id_strategy,
    email=email_strategy,
    display_name=display_name_strategy
)
def test_family_creation_child_rejection_property(user_id, email, display_name):
    """
    Property test: For any child user attempting to create a family, the request
    should be rejected with a 403 Forbidden error
    
    **Feature: gamified-activity-tracker, Property 3: Family group creation with owner**
    **Validates: Requirements 2.2**
    
    This test verifies that only parents can create families.
    """
    from routers.families import create_family
    from fastapi import HTTPException
    
    # Mock Firebase database
    mock_db = MagicMock()
    mock_user_ref = MagicMock()
    mock_user_doc = MagicMock()
    
    # Set up user document (child role, no family)
    mock_user_doc.exists = True
    mock_user_doc.to_dict.return_value = {
        'uid': user_id,
        'email': email,
        'displayName': display_name,
        'role': 'child',  # Child role
        'familyId': None
    }
    mock_user_ref.get.return_value = mock_user_doc
    
    # Configure mock database
    mock_users_collection = MagicMock()
    mock_users_collection.document.return_value = mock_user_ref
    mock_db.collection.return_value = mock_users_collection
    
    # Mock token data
    token_data = {
        'uid': user_id,
        'email': email,
        'name': display_name
    }
    
    # Patch firebase_service
    with patch('routers.families.firebase_service') as mock_firebase_service:
        mock_firebase_service.get_db.return_value = mock_db
        
        # Call the create_family function
        import asyncio
        with pytest.raises(HTTPException) as exc_info:
            asyncio.run(create_family(token_data))
        
        # Verify it's a 403 Forbidden error
        assert exc_info.value.status_code == 403, \
            f"Expected 403 Forbidden, got {exc_info.value.status_code}"
        assert "parent" in exc_info.value.detail.lower(), \
            "Error message should mention parent requirement"


@settings(max_examples=100, deadline=None)
@given(
    user_id=user_id_strategy,
    email=email_strategy,
    display_name=display_name_strategy,
    existing_family_id=st.text(min_size=5, max_size=20)
)
def test_family_creation_already_in_family_property(user_id, email, display_name, existing_family_id):
    """
    Property test: For any user already in a family, attempting to create another
    family should be rejected with a 400 Bad Request error
    
    **Feature: gamified-activity-tracker, Property 3: Family group creation with owner**
    **Validates: Requirements 2.2**
    
    This test verifies that users can only be in one family at a time.
    """
    from routers.families import create_family
    from fastapi import HTTPException
    
    # Mock Firebase database
    mock_db = MagicMock()
    mock_user_ref = MagicMock()
    mock_user_doc = MagicMock()
    
    # Set up user document (parent role, already in a family)
    mock_user_doc.exists = True
    mock_user_doc.to_dict.return_value = {
        'uid': user_id,
        'email': email,
        'displayName': display_name,
        'role': 'parent',
        'familyId': existing_family_id  # Already in a family
    }
    mock_user_ref.get.return_value = mock_user_doc
    
    # Configure mock database
    mock_users_collection = MagicMock()
    mock_users_collection.document.return_value = mock_user_ref
    mock_db.collection.return_value = mock_users_collection
    
    # Mock token data
    token_data = {
        'uid': user_id,
        'email': email,
        'name': display_name
    }
    
    # Patch firebase_service
    with patch('routers.families.firebase_service') as mock_firebase_service:
        mock_firebase_service.get_db.return_value = mock_db
        
        # Call the create_family function
        import asyncio
        with pytest.raises(HTTPException) as exc_info:
            asyncio.run(create_family(token_data))
        
        # Verify it's a 400 Bad Request error
        assert exc_info.value.status_code == 400, \
            f"Expected 400 Bad Request, got {exc_info.value.status_code}"
        assert "already" in exc_info.value.detail.lower(), \
            "Error message should mention user is already in a family"
