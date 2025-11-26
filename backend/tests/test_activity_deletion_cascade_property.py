"""
Property-based tests for activity deletion cascade

**Feature: gamified-activity-tracker, Property 18: Activity deletion cascade**
**Validates: Requirements 11.1, 11.2**
"""
import pytest
from hypothesis import given, strategies as st, settings, assume
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime, timedelta
import string


# Strategy for generating valid IDs
id_strategy = st.text(
    alphabet=string.ascii_letters + string.digits,
    min_size=10,
    max_size=30
)

# Strategy for generating activity names
activity_name_strategy = st.text(
    alphabet=string.ascii_letters + string.digits + ' ',
    min_size=1,
    max_size=50
).map(str.strip).filter(lambda x: len(x) > 0)

# Strategy for generating units
unit_strategy = st.text(
    alphabet=string.ascii_letters + string.digits,
    min_size=1,
    max_size=20
).map(str.strip).filter(lambda x: len(x) > 0)

# Strategy for generating positive rates
rate_strategy = st.floats(min_value=0.01, max_value=1000.0, allow_nan=False, allow_infinity=False)

# Strategy for generating log entry counts
log_count_strategy = st.integers(min_value=0, max_value=20)

# Strategy for generating user counts
user_count_strategy = st.integers(min_value=1, max_value=5)


@settings(max_examples=100, deadline=None)
@given(
    activity_id=id_strategy,
    family_id=id_strategy,
    parent_id=id_strategy,
    activity_name=activity_name_strategy,
    unit=unit_strategy,
    rate=rate_strategy,
    log_count=log_count_strategy,
    user_count=user_count_strategy
)
def test_property_18_activity_deletion_cascade(
    activity_id, family_id, parent_id, activity_name, unit, rate, log_count, user_count
):
    """
    Property test: For any activity deleted by a parent, the Backend Service should
    remove both the activity and all associated log entries from Firebase, and
    recalculate earnings for all affected children.
    
    **Feature: gamified-activity-tracker, Property 18: Activity deletion cascade**
    **Validates: Requirements 11.1, 11.2**
    
    This test verifies that:
    1. The activity is deleted from Firebase
    2. All log entries associated with the activity are deleted (cascade)
    3. The deletion affects all users who had logs for this activity
    4. The operation succeeds for any number of associated log entries (0 to many)
    """
    from routers.activities import delete_activity
    from fastapi import HTTPException
    
    # Generate unique user IDs for the logs
    user_ids = [f"user_{i}_{parent_id[:5]}" for i in range(user_count)]
    
    # Mock Firebase database
    mock_db = MagicMock()
    mock_activity_ref = MagicMock()
    mock_activity_doc = MagicMock()
    mock_logs_collection = MagicMock()
    mock_logs_query = MagicMock()
    
    # Set up activity document
    mock_activity_doc.exists = True
    mock_activity_doc.to_dict.return_value = {
        'id': activity_id,
        'familyId': family_id,
        'name': activity_name,
        'unit': unit,
        'rate': rate,
        'createdBy': parent_id,
        'createdAt': datetime.utcnow()
    }
    mock_activity_ref.get.return_value = mock_activity_doc
    
    # Create mock log documents
    mock_log_docs = []
    affected_users_expected = set()
    
    for i in range(log_count):
        mock_log_doc = MagicMock()
        user_id = user_ids[i % user_count]  # Distribute logs among users
        affected_users_expected.add(user_id)
        
        mock_log_doc.to_dict.return_value = {
            'id': f'log_{i}_{activity_id[:5]}',
            'activityId': activity_id,
            'userId': user_id,
            'familyId': family_id,
            'units': i + 1,
            'timestamp': datetime.utcnow() - timedelta(days=i),
            'verificationStatus': 'pending' if i % 2 == 0 else 'approved',
            'verifiedBy': None if i % 2 == 0 else parent_id,
            'verifiedAt': None if i % 2 == 0 else datetime.utcnow()
        }
        mock_log_doc.reference = MagicMock()
        mock_log_docs.append(mock_log_doc)
    
    # Set up logs query to return the mock log documents
    mock_logs_query.stream.return_value = mock_log_docs
    mock_logs_collection.where.return_value = mock_logs_query
    
    # Configure mock database
    def collection_side_effect(name):
        if name == 'activities':
            mock_activities_collection = MagicMock()
            mock_activities_collection.document.return_value = mock_activity_ref
            return mock_activities_collection
        elif name == 'logs':
            return mock_logs_collection
    
    mock_db.collection.side_effect = collection_side_effect
    
    # Mock token data (parent user)
    token_data = {
        'uid': parent_id,
        'email': f'{parent_id}@example.com',
        'name': 'Parent User'
    }
    
    # Patch firebase_service
    with patch('routers.activities.firebase_service') as mock_firebase_service:
        mock_firebase_service.get_db.return_value = mock_db
        mock_firebase_service.verify_family_membership.return_value = True
        
        # Call the delete_activity function
        import asyncio
        result = asyncio.run(delete_activity(activity_id, token_data))
        
        # Property 1: Activity should be deleted
        assert mock_activity_ref.delete.called, \
            "Activity document should be deleted"
        
        # Property 2: All associated log entries should be deleted (cascade)
        assert mock_logs_collection.where.called, \
            "Should query for associated log entries"
        
        # Verify the query was for the correct activity
        where_call_args = mock_logs_collection.where.call_args
        assert where_call_args[0][0] == 'activityId', \
            "Should query logs by activityId"
        assert where_call_args[0][2] == activity_id, \
            f"Should query for activity {activity_id}"
        
        # Property 3: Each log entry should be deleted
        deleted_count = sum(1 for log_doc in mock_log_docs if log_doc.reference.delete.called)
        assert deleted_count == log_count, \
            f"Should delete all {log_count} log entries, deleted {deleted_count}"
        
        # Property 4: Response should indicate success
        assert result.success is True, \
            "Deletion should return success=True"
        
        # Property 5: Response should report the number of deleted logs
        assert str(log_count) in result.message, \
            f"Response message should mention {log_count} deleted logs"
        
        # Property 6: Family membership should be verified
        assert mock_firebase_service.verify_family_membership.called, \
            "Should verify family membership before deletion"
        verify_call_args = mock_firebase_service.verify_family_membership.call_args
        assert verify_call_args[0][0] == parent_id, \
            "Should verify membership for the requesting user"
        assert verify_call_args[0][1] == family_id, \
            "Should verify membership for the activity's family"


@settings(max_examples=100, deadline=None)
@given(
    activity_id=id_strategy,
    family_id=id_strategy,
    parent_id=id_strategy,
    other_family_id=id_strategy
)
def test_activity_deletion_cross_family_prevention(
    activity_id, family_id, parent_id, other_family_id
):
    """
    Property test: For any parent attempting to delete an activity from a different
    family, the Backend Service should reject the request with a 403 Forbidden error.
    
    **Feature: gamified-activity-tracker, Property 18: Activity deletion cascade**
    **Validates: Requirements 11.1**
    
    This test verifies that cross-family data access is prevented during deletion.
    """
    # Ensure families are different
    assume(family_id != other_family_id)
    
    from routers.activities import delete_activity
    from fastapi import HTTPException
    
    # Mock Firebase database
    mock_db = MagicMock()
    mock_activity_ref = MagicMock()
    mock_activity_doc = MagicMock()
    
    # Set up activity document (belongs to different family)
    mock_activity_doc.exists = True
    mock_activity_doc.to_dict.return_value = {
        'id': activity_id,
        'familyId': other_family_id,  # Different family
        'name': 'Test Activity',
        'unit': 'Units',
        'rate': 1.0,
        'createdBy': 'other_user',
        'createdAt': datetime.utcnow()
    }
    mock_activity_ref.get.return_value = mock_activity_doc
    
    # Configure mock database
    mock_activities_collection = MagicMock()
    mock_activities_collection.document.return_value = mock_activity_ref
    mock_db.collection.return_value = mock_activities_collection
    
    # Mock token data (parent user from different family)
    token_data = {
        'uid': parent_id,
        'email': f'{parent_id}@example.com',
        'name': 'Parent User'
    }
    
    # Patch firebase_service
    with patch('routers.activities.firebase_service') as mock_firebase_service:
        mock_firebase_service.get_db.return_value = mock_db
        mock_firebase_service.verify_family_membership.return_value = False  # Not a member
        
        # Call the delete_activity function
        import asyncio
        with pytest.raises(HTTPException) as exc_info:
            asyncio.run(delete_activity(activity_id, token_data))
        
        # Verify it's a 403 Forbidden error
        assert exc_info.value.status_code == 403, \
            f"Expected 403 Forbidden, got {exc_info.value.status_code}"
        assert "access denied" in exc_info.value.detail.lower(), \
            "Error message should mention access denied"
        
        # Verify activity was NOT deleted
        assert not mock_activity_ref.delete.called, \
            "Activity should not be deleted when user is not a family member"


@settings(max_examples=100, deadline=None)
@given(
    activity_id=id_strategy,
    parent_id=id_strategy
)
def test_activity_deletion_not_found(activity_id, parent_id):
    """
    Property test: For any activity ID that doesn't exist, attempting to delete it
    should return a 404 Not Found error.
    
    **Feature: gamified-activity-tracker, Property 18: Activity deletion cascade**
    **Validates: Requirements 11.1**
    
    This test verifies proper error handling for non-existent activities.
    """
    from routers.activities import delete_activity
    from fastapi import HTTPException
    
    # Mock Firebase database
    mock_db = MagicMock()
    mock_activity_ref = MagicMock()
    mock_activity_doc = MagicMock()
    
    # Set up activity document as non-existent
    mock_activity_doc.exists = False
    mock_activity_ref.get.return_value = mock_activity_doc
    
    # Configure mock database
    mock_activities_collection = MagicMock()
    mock_activities_collection.document.return_value = mock_activity_ref
    mock_db.collection.return_value = mock_activities_collection
    
    # Mock token data
    token_data = {
        'uid': parent_id,
        'email': f'{parent_id}@example.com',
        'name': 'Parent User'
    }
    
    # Patch firebase_service
    with patch('routers.activities.firebase_service') as mock_firebase_service:
        mock_firebase_service.get_db.return_value = mock_db
        
        # Call the delete_activity function
        import asyncio
        with pytest.raises(HTTPException) as exc_info:
            asyncio.run(delete_activity(activity_id, token_data))
        
        # Verify it's a 404 Not Found error
        assert exc_info.value.status_code == 404, \
            f"Expected 404 Not Found, got {exc_info.value.status_code}"
        assert "not found" in exc_info.value.detail.lower(), \
            "Error message should mention activity not found"


@settings(max_examples=100, deadline=None)
@given(
    activity_id=id_strategy,
    family_id=id_strategy,
    parent_id=id_strategy,
    log_count=st.integers(min_value=1, max_value=10)
)
def test_activity_deletion_cascade_completeness(
    activity_id, family_id, parent_id, log_count
):
    """
    Property test: For any activity with associated log entries, deletion should
    remove ALL log entries, leaving none behind.
    
    **Feature: gamified-activity-tracker, Property 18: Activity deletion cascade**
    **Validates: Requirements 11.2**
    
    This test verifies the completeness of the cascade deletion.
    """
    from routers.activities import delete_activity
    
    # Mock Firebase database
    mock_db = MagicMock()
    mock_activity_ref = MagicMock()
    mock_activity_doc = MagicMock()
    mock_logs_collection = MagicMock()
    mock_logs_query = MagicMock()
    
    # Set up activity document
    mock_activity_doc.exists = True
    mock_activity_doc.to_dict.return_value = {
        'id': activity_id,
        'familyId': family_id,
        'name': 'Test Activity',
        'unit': 'Units',
        'rate': 1.0,
        'createdBy': parent_id,
        'createdAt': datetime.utcnow()
    }
    mock_activity_ref.get.return_value = mock_activity_doc
    
    # Create mock log documents with different verification statuses
    mock_log_docs = []
    for i in range(log_count):
        mock_log_doc = MagicMock()
        # Mix of pending, approved, and rejected logs
        status = ['pending', 'approved', 'rejected'][i % 3]
        
        mock_log_doc.to_dict.return_value = {
            'id': f'log_{i}',
            'activityId': activity_id,
            'userId': f'user_{i}',
            'familyId': family_id,
            'units': 1,
            'timestamp': datetime.utcnow(),
            'verificationStatus': status,
            'verifiedBy': None if status == 'pending' else parent_id,
            'verifiedAt': None if status == 'pending' else datetime.utcnow()
        }
        mock_log_doc.reference = MagicMock()
        mock_log_docs.append(mock_log_doc)
    
    # Set up logs query
    mock_logs_query.stream.return_value = mock_log_docs
    mock_logs_collection.where.return_value = mock_logs_query
    
    # Configure mock database
    def collection_side_effect(name):
        if name == 'activities':
            mock_activities_collection = MagicMock()
            mock_activities_collection.document.return_value = mock_activity_ref
            return mock_activities_collection
        elif name == 'logs':
            return mock_logs_collection
    
    mock_db.collection.side_effect = collection_side_effect
    
    # Mock token data
    token_data = {
        'uid': parent_id,
        'email': f'{parent_id}@example.com',
        'name': 'Parent User'
    }
    
    # Patch firebase_service
    with patch('routers.activities.firebase_service') as mock_firebase_service:
        mock_firebase_service.get_db.return_value = mock_db
        mock_firebase_service.verify_family_membership.return_value = True
        
        # Call the delete_activity function
        import asyncio
        result = asyncio.run(delete_activity(activity_id, token_data))
        
        # Property: ALL log entries should be deleted, regardless of verification status
        for i, log_doc in enumerate(mock_log_docs):
            assert log_doc.reference.delete.called, \
                f"Log entry {i} (status: {log_doc.to_dict()['verificationStatus']}) should be deleted"
        
        # Verify the count matches
        total_deleted = sum(1 for log_doc in mock_log_docs if log_doc.reference.delete.called)
        assert total_deleted == log_count, \
            f"Should delete all {log_count} log entries, deleted {total_deleted}"
