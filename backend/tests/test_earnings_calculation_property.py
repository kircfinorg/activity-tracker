"""
Property-based tests for earnings calculation

Feature: gamified-activity-tracker
Tests Properties 14 and 15
"""
import pytest
from hypothesis import given, strategies as st, settings, assume
from datetime import datetime, timedelta
from services.earnings_service import calculate_earnings_for_user
from unittest.mock import Mock, patch, MagicMock
import string


# Generators for property-based testing

@st.composite
def activity_with_rate(draw, activity_id=None):
    """Generate activity data with a positive rate"""
    if activity_id is None:
        activity_id = draw(st.text(min_size=5, max_size=50, alphabet=string.ascii_letters + string.digits))
    rate = draw(st.floats(min_value=0.01, max_value=100.0, allow_nan=False, allow_infinity=False))
    return {
        'id': activity_id,
        'rate': rate
    }


@st.composite
def log_entry_with_status(draw, activity_id, start_time, end_time):
    """Generate log entry data with specific verification status"""
    units = draw(st.integers(min_value=1, max_value=100))
    timestamp = draw(st.datetimes(
        min_value=start_time,
        max_value=end_time
    ))
    status = draw(st.sampled_from(['pending', 'approved', 'rejected']))
    
    return {
        'activityId': activity_id,
        'units': units,
        'timestamp': timestamp,
        'verificationStatus': status
    }


class TestEarningsCalculationProperties:
    """Property-based tests for earnings calculation"""
    
    @given(
        st.integers(min_value=1, max_value=10),
        st.integers(min_value=1, max_value=50)
    )
    @settings(max_examples=100)
    def test_property_14_earnings_calculation_based_on_verification(self, num_activities, num_logs):
        """
        Feature: gamified-activity-tracker, Property 14: Earnings calculation based on verification
        
        For any log entry, the calculated earnings should be included in the child's verified totals
        if and only if the verification status is "approved", and excluded if "rejected" or "pending".
        
        Validates: Requirements 7.4, 7.5
        """
        # Setup test data
        user_id = 'test_user_123'
        family_id = 'test_family_456'
        start_time = datetime(2024, 1, 1)
        end_time = datetime(2024, 1, 31)
        
        # Generate unique activities with unique IDs
        activities = []
        for i in range(num_activities):
            rate = (i + 1) * 0.5  # 0.5, 1.0, 1.5, etc.
            activities.append({
                'id': f'activity_{i}',
                'rate': rate
            })
        
        # Create mock Firestore data
        mock_logs = []
        expected_pending = 0.0
        expected_verified = 0.0
        
        # Create activity rate lookup
        activity_rates = {activity['id']: activity['rate'] for activity in activities}
        
        # Generate logs with different statuses
        for i in range(num_logs):
            activity = activities[i % len(activities)]
            units = (i % 10) + 1  # 1-10 units
            status = ['pending', 'approved', 'rejected'][i % 3]
            
            log_earnings = units * activity['rate']
            
            mock_log = {
                'activityId': activity['id'],
                'units': units,
                'timestamp': start_time + timedelta(days=i % 30),
                'verificationStatus': status
            }
            mock_logs.append(mock_log)
            
            # Calculate expected earnings based on status
            if status == 'approved':
                expected_verified += log_earnings
            elif status == 'pending':
                expected_pending += log_earnings
            # rejected logs don't count
        
        # Mock Firestore queries
        with patch('services.earnings_service.firebase_service') as mock_firebase:
            mock_db = MagicMock()
            mock_firebase.get_db.return_value = mock_db
            
            # Mock logs query
            mock_logs_collection = MagicMock()
            mock_db.collection.return_value = mock_logs_collection
            
            # Create mock query chain for logs
            mock_logs_query = MagicMock()
            mock_logs_collection.where.return_value.where.return_value.where.return_value.where.return_value = mock_logs_query
            
            # Mock log documents
            mock_log_docs = []
            for log_data in mock_logs:
                mock_doc = MagicMock()
                mock_doc.to_dict.return_value = log_data
                mock_log_docs.append(mock_doc)
            
            mock_logs_query.stream.return_value = mock_log_docs
            
            # Mock activities query
            mock_activities_query = MagicMock()
            
            # Create a side effect function to return different mocks based on collection name
            def collection_side_effect(collection_name):
                if collection_name == 'logs':
                    return mock_logs_collection
                elif collection_name == 'activities':
                    mock_activities_collection = MagicMock()
                    mock_activities_where = MagicMock()
                    mock_activities_collection.where.return_value = mock_activities_where
                    
                    # Mock activity documents
                    mock_activity_docs = []
                    for activity in activities:
                        mock_doc = MagicMock()
                        mock_doc.to_dict.return_value = activity
                        mock_activity_docs.append(mock_doc)
                    
                    mock_activities_where.stream.return_value = mock_activity_docs
                    return mock_activities_collection
                return MagicMock()
            
            mock_db.collection.side_effect = collection_side_effect
            
            # Calculate earnings
            pending, verified = calculate_earnings_for_user(
                user_id, family_id, start_time, end_time
            )
            
            # Verify earnings match expected values
            assert abs(pending - expected_pending) < 0.01, \
                f"Pending earnings mismatch: expected {expected_pending}, got {pending}"
            assert abs(verified - expected_verified) < 0.01, \
                f"Verified earnings mismatch: expected {expected_verified}, got {verified}"
    
    @given(
        st.integers(min_value=1, max_value=5),
        st.integers(min_value=5, max_value=30)
    )
    @settings(max_examples=100)
    def test_property_15_time_windowed_earnings_filtering(self, num_activities, num_days):
        """
        Feature: gamified-activity-tracker, Property 15: Time-windowed earnings filtering
        
        For any time window (today or last 7 days) and set of log entries, the earnings calculation
        should include only approved log entries with timestamps falling within the specified window.
        
        Validates: Requirements 8.5
        """
        # Setup test data
        user_id = 'test_user_123'
        family_id = 'test_family_456'
        
        # Define time window
        end_time = datetime(2024, 6, 15, 23, 59, 59)
        start_time = datetime(2024, 6, 1, 0, 0, 0)
        
        # Generate unique activities with unique IDs
        activities = []
        for i in range(num_activities):
            rate = (i + 1) * 0.5  # 0.5, 1.0, 1.5, etc.
            activities.append({
                'id': f'activity_{i}',
                'rate': rate
            })
        
        # Create logs both inside and outside the time window
        mock_logs = []
        expected_verified_in_window = 0.0
        
        # Create activity rate lookup
        activity_rates = {activity['id']: activity['rate'] for activity in activities}
        
        for i in range(num_days):
            activity = activities[i % len(activities)]
            units = (i % 10) + 1
            
            # Create logs at different times
            # Some before window, some in window, some after
            if i < num_days // 3:
                # Before window
                timestamp = start_time - timedelta(days=i + 1)
            elif i < 2 * num_days // 3:
                # Inside window
                timestamp = start_time + timedelta(days=i % 14)
            else:
                # After window
                timestamp = end_time + timedelta(days=i + 1)
            
            # All logs are approved for this test
            status = 'approved'
            
            log_earnings = units * activity['rate']
            
            mock_log = {
                'activityId': activity['id'],
                'units': units,
                'timestamp': timestamp,
                'verificationStatus': status
            }
            mock_logs.append(mock_log)
            
            # Only count logs inside the time window
            if start_time <= timestamp <= end_time:
                expected_verified_in_window += log_earnings
        
        # Mock Firestore queries
        with patch('services.earnings_service.firebase_service') as mock_firebase:
            mock_db = MagicMock()
            mock_firebase.get_db.return_value = mock_db
            
            # Mock logs query - filter logs by time window
            mock_logs_collection = MagicMock()
            mock_db.collection.return_value = mock_logs_collection
            
            # Create mock query chain for logs
            mock_logs_query = MagicMock()
            mock_logs_collection.where.return_value.where.return_value.where.return_value.where.return_value = mock_logs_query
            
            # Filter logs to only those in the time window (simulating Firestore filtering)
            filtered_logs = [
                log for log in mock_logs
                if start_time <= log['timestamp'] <= end_time
            ]
            
            # Mock log documents
            mock_log_docs = []
            for log_data in filtered_logs:
                mock_doc = MagicMock()
                mock_doc.to_dict.return_value = log_data
                mock_log_docs.append(mock_doc)
            
            mock_logs_query.stream.return_value = mock_log_docs
            
            # Mock activities query
            def collection_side_effect(collection_name):
                if collection_name == 'logs':
                    return mock_logs_collection
                elif collection_name == 'activities':
                    mock_activities_collection = MagicMock()
                    mock_activities_where = MagicMock()
                    mock_activities_collection.where.return_value = mock_activities_where
                    
                    # Mock activity documents
                    mock_activity_docs = []
                    for activity in activities:
                        mock_doc = MagicMock()
                        mock_doc.to_dict.return_value = activity
                        mock_activity_docs.append(mock_doc)
                    
                    mock_activities_where.stream.return_value = mock_activity_docs
                    return mock_activities_collection
                return MagicMock()
            
            mock_db.collection.side_effect = collection_side_effect
            
            # Calculate earnings for the time window
            pending, verified = calculate_earnings_for_user(
                user_id, family_id, start_time, end_time
            )
            
            # Verify only logs within the time window are counted
            assert abs(verified - expected_verified_in_window) < 0.01, \
                f"Time-windowed earnings mismatch: expected {expected_verified_in_window}, got {verified}"
            
            # Pending should be 0 since all logs are approved
            assert pending == 0.0, \
                f"Expected no pending earnings, got {pending}"
    
    def test_rejected_logs_excluded_from_earnings(self):
        """
        Test that rejected logs are never included in earnings calculations.
        This is an edge case for Property 14.
        """
        user_id = 'test_user_123'
        family_id = 'test_family_456'
        start_time = datetime(2024, 1, 1)
        end_time = datetime(2024, 1, 31)
        
        # Create logs with only rejected status
        mock_logs = [
            {
                'activityId': 'activity1',
                'units': 10,
                'timestamp': datetime(2024, 1, 15),
                'verificationStatus': 'rejected'
            },
            {
                'activityId': 'activity1',
                'units': 5,
                'timestamp': datetime(2024, 1, 20),
                'verificationStatus': 'rejected'
            }
        ]
        
        activities = [{'id': 'activity1', 'rate': 2.0}]
        
        # Mock Firestore queries
        with patch('services.earnings_service.firebase_service') as mock_firebase:
            mock_db = MagicMock()
            mock_firebase.get_db.return_value = mock_db
            
            mock_logs_collection = MagicMock()
            mock_logs_query = MagicMock()
            mock_logs_collection.where.return_value.where.return_value.where.return_value.where.return_value = mock_logs_query
            
            mock_log_docs = []
            for log_data in mock_logs:
                mock_doc = MagicMock()
                mock_doc.to_dict.return_value = log_data
                mock_log_docs.append(mock_doc)
            
            mock_logs_query.stream.return_value = mock_log_docs
            
            def collection_side_effect(collection_name):
                if collection_name == 'logs':
                    return mock_logs_collection
                elif collection_name == 'activities':
                    mock_activities_collection = MagicMock()
                    mock_activities_where = MagicMock()
                    mock_activities_collection.where.return_value = mock_activities_where
                    
                    mock_activity_docs = []
                    for activity in activities:
                        mock_doc = MagicMock()
                        mock_doc.to_dict.return_value = activity
                        mock_activity_docs.append(mock_doc)
                    
                    mock_activities_where.stream.return_value = mock_activity_docs
                    return mock_activities_collection
                return MagicMock()
            
            mock_db.collection.side_effect = collection_side_effect
            
            # Calculate earnings
            pending, verified = calculate_earnings_for_user(
                user_id, family_id, start_time, end_time
            )
            
            # Both should be 0 since all logs are rejected
            assert pending == 0.0, f"Expected no pending earnings, got {pending}"
            assert verified == 0.0, f"Expected no verified earnings, got {verified}"
