"""
Property-based tests for family joining and invite code validation

**Feature: gamified-activity-tracker, Property 4, 5, 6: Invite code validation, family membership, and single family constraint**
**Validates: Requirements 3.1, 3.2, 3.3, 3.5**
"""
import pytest
from hypothesis import given, strategies as st, settings
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

# Strategy for generating invite codes (6 uppercase alphanumeric)
invite_code_strategy = st.text(
    alphabet=string.ascii_uppercase + string.digits,
    min_size=6,
    max_size=6
)

# Strategy for generating family IDs
family_id_strategy = st.text(
    alphabet=string.ascii_letters + string.digits,
    min_size=10,
    max_size=30
)


@settings(max_examples=100, deadline=None)
@given(
    user_id=user_id_strategy,
    email=email_strategy,
    display_name=display_name_strategy,
    invite_code=invite_code_strategy,
    family_id=family_id_strategy,
    owner_id=user_id_strategy
)
def test_invite_code_validation_valid_property(user_id, email, display_name, invite_code, family_id, owner_id):
    """
    Property test: For any valid invite code, the Backend Service should correctly
    validate it and accept the join request
    
    **Feature: gamified-activity-tracker, Property 4: Invite code validation**
    **Validates: Requirements 3.1**
    
    This test verifies that valid invite codes are accepted.
    """
    from routers.families import join_family, JoinFamilyRequest
    from fastapi import HTTPException
    
    # Ensure user_id and owner_id are different
    if user_id == owner_id:
        owner_id = owner_id + "_owner"
    
    # Mock Firebase database
    mock_db = MagicMock()
    mock_user_ref = MagicMock()
    mock_user_doc = MagicMock()
    mock_family_doc = MagicMock()
    
    # Set up user document (not in a family)
    mock_user_doc.exists = True
    mock_user_doc.to_dict.return_value = {
        'uid': user_id,
        'email': email,
        'displayName': display_name,
        'role': 'child',
        'familyId': None
    }
    mock_user_ref.get.return_value = mock_user_doc
    
    # Set up family document (valid invite code)
    mock_family_doc.to_dict.return_value = {
        'id': family_id,
        'inviteCode': invite_code.upper(),
        'ownerId': owner_id,
        'members': [owner_id],
        'createdAt': datetime.utcnow()
    }
    mock_family_doc.reference = MagicMock()
    
    # Configure mock database
    def collection_side_effect(name):
        if name == 'users':
            mock_users_collection = MagicMock()
            mock_users_collection.document.return_value = mock_user_ref
            return mock_users_collection
        elif name == 'families':
            mock_families_collection = MagicMock()
            mock_query = MagicMock()
            mock_query.stream.return_value = [mock_family_doc]
            mock_families_collection.where.return_value.limit.return_value = mock_query
            return mock_families_collection
    
    mock_db.collection.side_effect = collection_side_effect
    
    # Mock token data
    token_data = {
        'uid': user_id,
        'email': email,
        'name': display_name
    }
    
    # Create request
    request = JoinFamilyRequest(invite_code=invite_code)
    
    # Patch firebase_service
    with patch('routers.families.firebase_service') as mock_firebase_service:
        mock_firebase_service.get_db.return_value = mock_db
        
        # Call the join_family function
        import asyncio
        result = asyncio.run(join_family(request, token_data))
        
        # Property: Valid invite code should be accepted
        assert result.success is True, "Valid invite code should be accepted"
        assert result.family_id == family_id, \
            f"Should join family {family_id}, got {result.family_id}"


@settings(max_examples=100, deadline=None)
@given(
    user_id=user_id_strategy,
    email=email_strategy,
    display_name=display_name_strategy,
    invalid_code=st.text(min_size=1, max_size=10)
)
def test_invite_code_validation_invalid_property(user_id, email, display_name, invalid_code):
    """
    Property test: For any invalid invite code, the Backend Service should reject
    the join request with an error
    
    **Feature: gamified-activity-tracker, Property 4: Invite code validation**
    **Validates: Requirements 3.3**
    
    This test verifies that invalid invite codes are rejected.
    """
    from routers.families import join_family, JoinFamilyRequest
    from fastapi import HTTPException
    
    # Mock Firebase database
    mock_db = MagicMock()
    mock_user_ref = MagicMock()
    mock_user_doc = MagicMock()
    
    # Set up user document (not in a family)
    mock_user_doc.exists = True
    mock_user_doc.to_dict.return_value = {
        'uid': user_id,
        'email': email,
        'displayName': display_name,
        'role': 'child',
        'familyId': None
    }
    mock_user_ref.get.return_value = mock_user_doc
    
    # Configure mock database - no family found with this code
    def collection_side_effect(name):
        if name == 'users':
            mock_users_collection = MagicMock()
            mock_users_collection.document.return_value = mock_user_ref
            return mock_users_collection
        elif name == 'families':
            mock_families_collection = MagicMock()
            mock_query = MagicMock()
            mock_query.stream.return_value = []  # No family found
            mock_families_collection.where.return_value.limit.return_value = mock_query
            return mock_families_collection
    
    mock_db.collection.side_effect = collection_side_effect
    
    # Mock token data
    token_data = {
        'uid': user_id,
        'email': email,
        'name': display_name
    }
    
    # Create request with invalid code
    request = JoinFamilyRequest(invite_code=invalid_code)
    
    # Patch firebase_service
    with patch('routers.families.firebase_service') as mock_firebase_service:
        mock_firebase_service.get_db.return_value = mock_db
        
        # Call the join_family function
        import asyncio
        with pytest.raises(HTTPException) as exc_info:
            asyncio.run(join_family(request, token_data))
        
        # Property: Invalid invite code should be rejected with 400 error
        assert exc_info.value.status_code == 400, \
            f"Expected 400 Bad Request, got {exc_info.value.status_code}"
        assert "invalid" in exc_info.value.detail.lower(), \
            "Error message should mention invalid code"


@settings(max_examples=100, deadline=None)
@given(
    user_id=user_id_strategy,
    email=email_strategy,
    display_name=display_name_strategy,
    invite_code=invite_code_strategy,
    family_id=family_id_strategy,
    owner_id=user_id_strategy
)
def test_family_membership_addition_property(user_id, email, display_name, invite_code, family_id, owner_id):
    """
    Property test: For any valid invite code provided by a user not already in a family,
    the Backend Service should add the user to the corresponding family group
    
    **Feature: gamified-activity-tracker, Property 5: Family membership addition**
    **Validates: Requirements 3.2**
    
    This test verifies that users are correctly added to families.
    """
    from routers.families import join_family, JoinFamilyRequest
    
    # Ensure user_id and owner_id are different
    if user_id == owner_id:
        owner_id = owner_id + "_owner"
    
    # Mock Firebase database
    mock_db = MagicMock()
    mock_user_ref = MagicMock()
    mock_user_doc = MagicMock()
    mock_family_doc = MagicMock()
    
    # Set up user document (not in a family)
    mock_user_doc.exists = True
    mock_user_doc.to_dict.return_value = {
        'uid': user_id,
        'email': email,
        'displayName': display_name,
        'role': 'child',
        'familyId': None
    }
    mock_user_ref.get.return_value = mock_user_doc
    
    # Set up family document
    initial_members = [owner_id]
    mock_family_doc.to_dict.return_value = {
        'id': family_id,
        'inviteCode': invite_code.upper(),
        'ownerId': owner_id,
        'members': initial_members.copy(),
        'createdAt': datetime.utcnow()
    }
    mock_family_doc.reference = MagicMock()
    
    # Configure mock database
    def collection_side_effect(name):
        if name == 'users':
            mock_users_collection = MagicMock()
            mock_users_collection.document.return_value = mock_user_ref
            return mock_users_collection
        elif name == 'families':
            mock_families_collection = MagicMock()
            mock_query = MagicMock()
            mock_query.stream.return_value = [mock_family_doc]
            mock_families_collection.where.return_value.limit.return_value = mock_query
            return mock_families_collection
    
    mock_db.collection.side_effect = collection_side_effect
    
    # Mock token data
    token_data = {
        'uid': user_id,
        'email': email,
        'name': display_name
    }
    
    # Create request
    request = JoinFamilyRequest(invite_code=invite_code)
    
    # Patch firebase_service
    with patch('routers.families.firebase_service') as mock_firebase_service:
        mock_firebase_service.get_db.return_value = mock_db
        
        # Call the join_family function
        import asyncio
        result = asyncio.run(join_family(request, token_data))
        
        # Property 1: User should be added to family members
        assert mock_family_doc.reference.update.called, \
            "Family members list should be updated"
        
        update_call = mock_family_doc.reference.update.call_args[0][0]
        updated_members = update_call['members']
        
        assert user_id in updated_members, \
            f"User {user_id} should be in updated members list"
        
        # Property 2: User's familyId should be updated
        assert mock_user_ref.update.called, "User's familyId should be updated"
        user_update = mock_user_ref.update.call_args[0][0]
        assert user_update['familyId'] == family_id, \
            f"User's familyId should be {family_id}, got {user_update['familyId']}"


@settings(max_examples=100, deadline=None)
@given(
    user_id=user_id_strategy,
    email=email_strategy,
    display_name=display_name_strategy,
    invite_code=invite_code_strategy,
    existing_family_id=family_id_strategy,
    new_family_id=family_id_strategy
)
def test_single_family_membership_constraint_property(
    user_id, email, display_name, invite_code, existing_family_id, new_family_id
):
    """
    Property test: For any user already in a family group, attempting to join
    another family should be prevented
    
    **Feature: gamified-activity-tracker, Property 6: Single family membership constraint**
    **Validates: Requirements 3.5**
    
    This test verifies that users can only be in one family at a time.
    """
    from routers.families import join_family, JoinFamilyRequest
    from fastapi import HTTPException
    
    # Ensure family IDs are different
    if existing_family_id == new_family_id:
        new_family_id = new_family_id + "_new"
    
    # Mock Firebase database
    mock_db = MagicMock()
    mock_user_ref = MagicMock()
    mock_user_doc = MagicMock()
    
    # Set up user document (already in a family)
    mock_user_doc.exists = True
    mock_user_doc.to_dict.return_value = {
        'uid': user_id,
        'email': email,
        'displayName': display_name,
        'role': 'child',
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
    
    # Create request
    request = JoinFamilyRequest(invite_code=invite_code)
    
    # Patch firebase_service
    with patch('routers.families.firebase_service') as mock_firebase_service:
        mock_firebase_service.get_db.return_value = mock_db
        
        # Call the join_family function
        import asyncio
        with pytest.raises(HTTPException) as exc_info:
            asyncio.run(join_family(request, token_data))
        
        # Property: User already in family should be rejected with 400 error
        assert exc_info.value.status_code == 400, \
            f"Expected 400 Bad Request, got {exc_info.value.status_code}"
        assert "already" in exc_info.value.detail.lower(), \
            "Error message should mention user is already in a family"
