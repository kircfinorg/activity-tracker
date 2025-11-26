"""
Property-based tests for log entry creation

Feature: gamified-activity-tracker
Tests Properties 11 and 12
"""
import pytest
from hypothesis import given, strategies as st, settings
from datetime import datetime, timedelta
from models.log_entry import LogEntry
from pydantic import ValidationError
import string


# Generators for property-based testing

@st.composite
def valid_log_entry_data(draw):
    """Generate valid log entry data"""
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
def invalid_units_log_entry_data(draw):
    """Generate log entry data with invalid (non-positive) units"""
    return {
        'id': draw(st.text(min_size=1, max_size=50, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd')))),
        'activity_id': draw(st.text(min_size=1, max_size=50, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd')))),
        'user_id': draw(st.text(min_size=1, max_size=50, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd')))),
        'family_id': draw(st.text(min_size=1, max_size=50, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd')))),
        'units': draw(st.integers(max_value=0)),
        'timestamp': datetime.utcnow(),
        'verification_status': 'pending',
        'verified_by': None,
        'verified_at': None
    }


class TestLogEntryCreationProperties:
    """Property-based tests for log entry creation"""
    
    @given(valid_log_entry_data())
    @settings(max_examples=100)
    def test_property_11_log_entry_creation_with_required_fields(self, log_data):
        """
        Feature: gamified-activity-tracker, Property 11: Log entry creation with required fields
        
        For any child user logging an activity, the Backend Service should create a log entry
        in Firebase containing the current timestamp, pending verification status, and references
        to both the child user and the activity.
        
        Validates: Requirements 6.1, 6.2
        """
        # Create log entry using Pydantic model
        log_entry = LogEntry(**log_data)
        
        # Verify all required fields are present and correct
        assert log_entry.id == log_data['id']
        assert log_entry.activity_id == log_data['activity_id']
        assert log_entry.user_id == log_data['user_id']
        assert log_entry.family_id == log_data['family_id']
        assert log_entry.units == log_data['units']
        assert log_entry.timestamp == log_data['timestamp']
        
        # Verify verification status is pending for new logs
        assert log_entry.verification_status == 'pending', \
            f"New log entry should have 'pending' status, got '{log_entry.verification_status}'"
        
        # Verify verification fields are None for pending logs
        assert log_entry.verified_by is None, \
            f"New log entry should have verified_by=None, got {log_entry.verified_by}"
        assert log_entry.verified_at is None, \
            f"New log entry should have verified_at=None, got {log_entry.verified_at}"
        
        # Verify timestamp is present (requirement 6.1)
        assert hasattr(log_entry, 'timestamp')
        assert log_entry.timestamp is not None
        assert isinstance(log_entry.timestamp, datetime)
        
        # Verify references to child user and activity (requirement 6.2)
        assert hasattr(log_entry, 'user_id')
        assert log_entry.user_id is not None
        assert len(log_entry.user_id) > 0
        
        assert hasattr(log_entry, 'activity_id')
        assert log_entry.activity_id is not None
        assert len(log_entry.activity_id) > 0
        
        # Verify family_id is present for family-based data isolation
        assert hasattr(log_entry, 'family_id')
        assert log_entry.family_id is not None
        assert len(log_entry.family_id) > 0
    
    @given(
        st.text(min_size=1, max_size=50, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'))),
        st.text(min_size=1, max_size=50, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'))),
        st.text(min_size=1, max_size=50, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'))),
        st.integers(min_value=1, max_value=1000),
        st.integers(min_value=2, max_value=10)
    )
    @settings(max_examples=100)
    def test_property_12_multiple_log_entry_independence(
        self, 
        activity_id, 
        user_id, 
        family_id, 
        units, 
        num_logs
    ):
        """
        Feature: gamified-activity-tracker, Property 12: Multiple log entry independence
        
        For any child logging the same activity multiple times, the Backend Service should
        maintain separate timestamped entries for each log, ensuring no logs are merged or
        overwritten.
        
        Validates: Requirements 6.3
        """
        # Create multiple log entries for the same activity
        log_entries = []
        base_time = datetime.utcnow()
        
        for i in range(num_logs):
            # Each log gets a unique ID and timestamp
            log_data = {
                'id': f'log_{activity_id}_{i}',
                'activity_id': activity_id,
                'user_id': user_id,
                'family_id': family_id,
                'units': units,
                'timestamp': base_time + timedelta(seconds=i),
                'verification_status': 'pending',
                'verified_by': None,
                'verified_at': None
            }
            
            log_entry = LogEntry(**log_data)
            log_entries.append(log_entry)
        
        # Verify we have the expected number of separate log entries
        assert len(log_entries) == num_logs, \
            f"Should have {num_logs} separate log entries, got {len(log_entries)}"
        
        # Verify each log entry has a unique ID
        log_ids = [log.id for log in log_entries]
        assert len(log_ids) == len(set(log_ids)), \
            "All log entries should have unique IDs"
        
        # Verify each log entry has a unique timestamp
        timestamps = [log.timestamp for log in log_entries]
        assert len(timestamps) == len(set(timestamps)), \
            "All log entries should have unique timestamps"
        
        # Verify all logs reference the same activity
        for log in log_entries:
            assert log.activity_id == activity_id, \
                f"All logs should reference activity {activity_id}"
        
        # Verify all logs reference the same user
        for log in log_entries:
            assert log.user_id == user_id, \
                f"All logs should reference user {user_id}"
        
        # Verify all logs are independent (changing one doesn't affect others)
        # Modify the first log entry's verification status
        log_entries[0].verification_status = 'approved'
        
        # Verify other logs remain unchanged
        for i in range(1, num_logs):
            assert log_entries[i].verification_status == 'pending', \
                f"Log {i} should remain 'pending' when log 0 is modified"
    
    @given(invalid_units_log_entry_data())
    @settings(max_examples=100)
    def test_non_positive_units_rejected(self, log_data):
        """
        Test that log entries with non-positive units are rejected
        Related to Property 11 - validates units requirement
        """
        # Attempt to create log entry with invalid units
        with pytest.raises(ValidationError) as exc_info:
            LogEntry(**log_data)
        
        # Verify that the error is related to the units field
        errors = exc_info.value.errors()
        assert any('units' in str(error['loc']) for error in errors), \
            f"Expected units validation error, got: {errors}"
        
        # Verify the error message indicates units must be positive
        error_messages = [error['msg'] for error in errors]
        assert any('greater than' in msg.lower() for msg in error_messages), \
            f"Expected 'greater than' in error message, got: {error_messages}"
    
    @given(
        st.text(min_size=1, max_size=50, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'))),
        st.text(min_size=1, max_size=50, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'))),
        st.text(min_size=1, max_size=50, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'))),
        st.text(min_size=1, max_size=50, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'))),
        st.integers(min_value=1, max_value=1000)
    )
    @settings(max_examples=100)
    def test_verification_status_must_be_valid(
        self, 
        log_id, 
        activity_id, 
        user_id, 
        family_id, 
        units
    ):
        """
        Test that verification_status must be one of: pending, approved, rejected
        Related to Property 11 - validates verification status requirement
        """
        valid_statuses = ['pending', 'approved', 'rejected']
        
        # Test each valid status
        for status in valid_statuses:
            log_entry = LogEntry(
                id=log_id,
                activity_id=activity_id,
                user_id=user_id,
                family_id=family_id,
                units=units,
                timestamp=datetime.utcnow(),
                verification_status=status,
                verified_by=None,
                verified_at=None
            )
            assert log_entry.verification_status == status
        
        # Test invalid status
        with pytest.raises(ValidationError) as exc_info:
            LogEntry(
                id=log_id,
                activity_id=activity_id,
                user_id=user_id,
                family_id=family_id,
                units=units,
                timestamp=datetime.utcnow(),
                verification_status='invalid_status',
                verified_by=None,
                verified_at=None
            )
        
        errors = exc_info.value.errors()
        assert any('verification_status' in str(error['loc']) for error in errors)
    
    @given(
        st.text(min_size=1, max_size=50, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'))),
        st.text(min_size=1, max_size=50, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'))),
        st.text(min_size=1, max_size=50, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'))),
        st.integers(min_value=1, max_value=1000),
        st.datetimes(min_value=datetime(2020, 1, 1), max_value=datetime(2030, 12, 31))
    )
    @settings(max_examples=100)
    def test_timestamp_preserved_across_multiple_logs(
        self, 
        activity_id, 
        user_id, 
        family_id, 
        units, 
        timestamp
    ):
        """
        Test that timestamps are preserved and not overwritten when creating multiple logs
        Related to Property 12 - validates timestamp independence
        """
        # Create first log with specific timestamp
        log1 = LogEntry(
            id='log1',
            activity_id=activity_id,
            user_id=user_id,
            family_id=family_id,
            units=units,
            timestamp=timestamp,
            verification_status='pending',
            verified_by=None,
            verified_at=None
        )
        
        # Create second log with different timestamp
        timestamp2 = timestamp + timedelta(hours=1)
        log2 = LogEntry(
            id='log2',
            activity_id=activity_id,
            user_id=user_id,
            family_id=family_id,
            units=units,
            timestamp=timestamp2,
            verification_status='pending',
            verified_by=None,
            verified_at=None
        )
        
        # Verify timestamps are different and preserved
        assert log1.timestamp == timestamp, \
            "First log timestamp should be preserved"
        assert log2.timestamp == timestamp2, \
            "Second log timestamp should be preserved"
        assert log1.timestamp != log2.timestamp, \
            "Log timestamps should be different"
