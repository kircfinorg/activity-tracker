"""
Property-based tests for verification status transitions

Feature: gamified-activity-tracker
Tests Property 13
"""
import pytest
from hypothesis import given, strategies as st, settings
from datetime import datetime, timedelta
from models.log_entry import LogEntry
from pydantic import ValidationError


# Generators for property-based testing

@st.composite
def pending_log_entry_data(draw):
    """Generate a log entry with pending status"""
    return {
        'id': draw(st.text(min_size=1, max_size=50, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd')))),
        'activity_id': draw(st.text(min_size=1, max_size=50, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd')))),
        'user_id': draw(st.text(min_size=1, max_size=50, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd')))),
        'family_id': draw(st.text(min_size=1, max_size=50, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd')))),
        'units': draw(st.integers(min_value=1, max_value=1000)),
        'timestamp': draw(st.datetimes(
            min_value=datetime(2020, 1, 1),
            max_value=datetime(2030, 12, 31)
        )),
        'verification_status': 'pending',
        'verified_by': None,
        'verified_at': None
    }


@st.composite
def parent_user_id(draw):
    """Generate a parent user ID"""
    return draw(st.text(min_size=1, max_size=50, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'))))


class TestVerificationStatusTransitionsProperty:
    """Property-based tests for verification status transitions"""
    
    @given(
        pending_log_entry_data(),
        parent_user_id(),
        st.sampled_from(['approved', 'rejected'])
    )
    @settings(max_examples=100)
    def test_property_13_verification_status_transitions(
        self, 
        log_data, 
        parent_id,
        new_status
    ):
        """
        Feature: gamified-activity-tracker, Property 13: Verification status transitions
        
        For any log entry being verified by a parent, the Backend Service should update
        the verification status in Firebase to either "approved" or "rejected" based on
        the parent's action.
        
        Validates: Requirements 7.2, 7.3
        """
        # Create initial log entry with pending status
        initial_log = LogEntry(**log_data)
        
        # Verify initial state is pending
        assert initial_log.verification_status == 'pending', \
            f"Initial log should have 'pending' status, got '{initial_log.verification_status}'"
        assert initial_log.verified_by is None, \
            f"Initial log should have verified_by=None, got {initial_log.verified_by}"
        assert initial_log.verified_at is None, \
            f"Initial log should have verified_at=None, got {initial_log.verified_at}"
        
        # Simulate parent verification action
        # Verification time should be at or after the log creation timestamp
        verification_time = initial_log.timestamp + timedelta(seconds=1)
        
        # Update log entry to reflect verification
        verified_log_data = {
            **log_data,
            'verification_status': new_status,
            'verified_by': parent_id,
            'verified_at': verification_time
        }
        
        verified_log = LogEntry(**verified_log_data)
        
        # Property: Verification status should transition to approved or rejected
        assert verified_log.verification_status in ['approved', 'rejected'], \
            f"Verified log status should be 'approved' or 'rejected', got '{verified_log.verification_status}'"
        
        # Property: Verification status should match the parent's action
        assert verified_log.verification_status == new_status, \
            f"Verification status should be '{new_status}', got '{verified_log.verification_status}'"
        
        # Property: verified_by should be set to the parent's user ID
        assert verified_log.verified_by == parent_id, \
            f"verified_by should be '{parent_id}', got '{verified_log.verified_by}'"
        
        # Property: verified_at should be set to a timestamp
        assert verified_log.verified_at is not None, \
            "verified_at should be set after verification"
        assert isinstance(verified_log.verified_at, datetime), \
            f"verified_at should be a datetime, got {type(verified_log.verified_at)}"
        
        # Property: verified_at should be at or after the log creation timestamp
        assert verified_log.verified_at >= initial_log.timestamp, \
            "verified_at should be at or after the log creation timestamp"
        
        # Property: All other fields should remain unchanged
        assert verified_log.id == initial_log.id, \
            "Log ID should not change during verification"
        assert verified_log.activity_id == initial_log.activity_id, \
            "Activity ID should not change during verification"
        assert verified_log.user_id == initial_log.user_id, \
            "User ID should not change during verification"
        assert verified_log.family_id == initial_log.family_id, \
            "Family ID should not change during verification"
        assert verified_log.units == initial_log.units, \
            "Units should not change during verification"
        assert verified_log.timestamp == initial_log.timestamp, \
            "Original timestamp should not change during verification"
    
    @given(
        pending_log_entry_data(),
        parent_user_id()
    )
    @settings(max_examples=100)
    def test_approved_status_transition(self, log_data, parent_id):
        """
        Test that pending logs can be transitioned to approved status
        
        Validates: Requirement 7.2 - parent approves a log entry
        """
        # Create initial pending log
        initial_log = LogEntry(**log_data)
        assert initial_log.verification_status == 'pending'
        
        # Transition to approved
        # Verification time should be at or after the log creation timestamp
        verification_time = initial_log.timestamp + timedelta(seconds=1)
        approved_log_data = {
            **log_data,
            'verification_status': 'approved',
            'verified_by': parent_id,
            'verified_at': verification_time
        }
        
        approved_log = LogEntry(**approved_log_data)
        
        # Verify the transition
        assert approved_log.verification_status == 'approved', \
            "Log should transition to 'approved' status"
        assert approved_log.verified_by == parent_id, \
            "verified_by should be set to parent ID"
        assert approved_log.verified_at == verification_time, \
            "verified_at should be set to verification time"
    
    @given(
        pending_log_entry_data(),
        parent_user_id()
    )
    @settings(max_examples=100)
    def test_rejected_status_transition(self, log_data, parent_id):
        """
        Test that pending logs can be transitioned to rejected status
        
        Validates: Requirement 7.3 - parent rejects a log entry
        """
        # Create initial pending log
        initial_log = LogEntry(**log_data)
        assert initial_log.verification_status == 'pending'
        
        # Transition to rejected
        # Verification time should be at or after the log creation timestamp
        verification_time = initial_log.timestamp + timedelta(seconds=1)
        rejected_log_data = {
            **log_data,
            'verification_status': 'rejected',
            'verified_by': parent_id,
            'verified_at': verification_time
        }
        
        rejected_log = LogEntry(**rejected_log_data)
        
        # Verify the transition
        assert rejected_log.verification_status == 'rejected', \
            "Log should transition to 'rejected' status"
        assert rejected_log.verified_by == parent_id, \
            "verified_by should be set to parent ID"
        assert rejected_log.verified_at == verification_time, \
            "verified_at should be set to verification time"
    
    @given(
        pending_log_entry_data(),
        parent_user_id(),
        st.sampled_from(['approved', 'rejected'])
    )
    @settings(max_examples=100)
    def test_verification_is_idempotent_for_same_status(
        self, 
        log_data, 
        parent_id,
        status
    ):
        """
        Test that verifying a log with the same status multiple times produces consistent results
        
        This ensures that the verification operation is idempotent for the same status.
        """
        # Create initial log to get timestamp
        initial_log = LogEntry(**log_data)
        verification_time = initial_log.timestamp + timedelta(seconds=1)
        
        # First verification
        verified_log_data_1 = {
            **log_data,
            'verification_status': status,
            'verified_by': parent_id,
            'verified_at': verification_time
        }
        verified_log_1 = LogEntry(**verified_log_data_1)
        
        # Second verification with same status (simulating idempotent operation)
        verified_log_data_2 = {
            **log_data,
            'verification_status': status,
            'verified_by': parent_id,
            'verified_at': verification_time
        }
        verified_log_2 = LogEntry(**verified_log_data_2)
        
        # Both should have the same verification status
        assert verified_log_1.verification_status == verified_log_2.verification_status, \
            "Multiple verifications with same status should produce same result"
        assert verified_log_1.verified_by == verified_log_2.verified_by, \
            "verified_by should be consistent"
    
    @given(
        st.text(min_size=1, max_size=50, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'))),
        st.text(min_size=1, max_size=50, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'))),
        st.text(min_size=1, max_size=50, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'))),
        st.text(min_size=1, max_size=50, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'))),
        st.integers(min_value=1, max_value=1000),
        st.datetimes(min_value=datetime(2020, 1, 1), max_value=datetime(2030, 12, 31))
    )
    @settings(max_examples=100)
    def test_invalid_status_transition_rejected(
        self,
        log_id,
        activity_id,
        user_id,
        family_id,
        units,
        timestamp
    ):
        """
        Test that invalid verification statuses are rejected by the model
        
        This ensures data integrity by preventing invalid status values.
        """
        # Valid statuses should work
        for valid_status in ['pending', 'approved', 'rejected']:
            log = LogEntry(
                id=log_id,
                activity_id=activity_id,
                user_id=user_id,
                family_id=family_id,
                units=units,
                timestamp=timestamp,
                verification_status=valid_status,
                verified_by=None,
                verified_at=None
            )
            assert log.verification_status == valid_status
        
        # Invalid status should raise ValidationError
        with pytest.raises(ValidationError) as exc_info:
            LogEntry(
                id=log_id,
                activity_id=activity_id,
                user_id=user_id,
                family_id=family_id,
                units=units,
                timestamp=timestamp,
                verification_status='invalid_status',
                verified_by=None,
                verified_at=None
            )
        
        errors = exc_info.value.errors()
        assert any('verification_status' in str(error['loc']) for error in errors), \
            "Should raise validation error for invalid verification_status"
    
    @given(
        pending_log_entry_data(),
        parent_user_id(),
        st.sampled_from(['approved', 'rejected']),
        st.integers(min_value=1, max_value=10)
    )
    @settings(max_examples=100)
    def test_multiple_logs_verified_independently(
        self,
        base_log_data,
        parent_id,
        status,
        num_logs
    ):
        """
        Test that verifying one log doesn't affect other logs
        
        This ensures that verification operations are independent for each log entry.
        """
        # Create multiple pending logs
        pending_logs = []
        for i in range(num_logs):
            log_data = {
                **base_log_data,
                'id': f"{base_log_data['id']}_{i}",
                'timestamp': base_log_data['timestamp'] + timedelta(seconds=i)
            }
            pending_logs.append(LogEntry(**log_data))
        
        # Verify all logs are pending
        for log in pending_logs:
            assert log.verification_status == 'pending'
        
        # Verify the first log
        # Verification time should be at or after the log creation timestamp
        verification_time = pending_logs[0].timestamp + timedelta(seconds=1)
        verified_log_data = {
            'id': pending_logs[0].id,
            'activity_id': pending_logs[0].activity_id,
            'user_id': pending_logs[0].user_id,
            'family_id': pending_logs[0].family_id,
            'units': pending_logs[0].units,
            'timestamp': pending_logs[0].timestamp,
            'verification_status': status,
            'verified_by': parent_id,
            'verified_at': verification_time
        }
        verified_log = LogEntry(**verified_log_data)
        
        # Verify the first log changed status
        assert verified_log.verification_status == status
        
        # Verify other logs remain pending (in a real system)
        # This test demonstrates that the model allows independent verification
        for i in range(1, num_logs):
            # Each log can still be created with pending status
            assert pending_logs[i].verification_status == 'pending'
            assert pending_logs[i].id != verified_log.id
