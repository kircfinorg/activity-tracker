"""
Property-based tests for pending verification display

Feature: gamified-activity-tracker
Tests Property 16
"""
import pytest
from hypothesis import given, strategies as st, settings
from datetime import datetime
from models.log_entry import LogEntry
from models.activity import Activity
from models.user import User


# Generators for property-based testing

@st.composite
def valid_user_data(draw):
    """Generate valid user data"""
    return {
        'uid': draw(st.text(min_size=1, max_size=50, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd')))),
        'email': draw(st.emails()),
        'display_name': draw(st.text(min_size=1, max_size=100, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd', 'Zs')))),
        'photo_url': draw(st.text(min_size=10, max_size=200)),
        'role': 'child',
        'family_id': draw(st.text(min_size=1, max_size=50, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd')))),
        'theme': 'deep-ocean'
    }


@st.composite
def valid_activity_data(draw):
    """Generate valid activity data"""
    # Generate name and unit that are not just whitespace
    name = draw(st.text(min_size=1, max_size=100, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd')))).strip()
    if not name:
        name = "Activity"
    
    unit = draw(st.text(min_size=1, max_size=50, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd')))).strip()
    if not unit:
        unit = "Unit"
    
    return {
        'id': draw(st.text(min_size=1, max_size=50, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd')))),
        'family_id': draw(st.text(min_size=1, max_size=50, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd')))),
        'name': name,
        'unit': unit,
        'rate': draw(st.floats(min_value=0.01, max_value=1000.0)),
        'created_by': draw(st.text(min_size=1, max_size=50, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd')))),
        'created_at': draw(st.datetimes(
            min_value=datetime(2020, 1, 1),
            max_value=datetime(2030, 12, 31)
        ))
    }


@st.composite
def valid_pending_log_data(draw):
    """Generate valid pending log entry data"""
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


def format_pending_verification_display(log_entry: LogEntry, activity: Activity, user: User) -> str:
    """
    Format a pending log entry for display in the verification interface.
    
    This function represents the display logic that should include all required information
    as specified in Requirements 9.3.
    
    Args:
        log_entry: The pending log entry
        activity: The activity associated with the log
        user: The child user who created the log
        
    Returns:
        A formatted string containing all required display information
    """
    # Format timestamp for display
    timestamp_str = log_entry.timestamp.strftime("%Y-%m-%d %H:%M:%S")
    
    # Create display string with all required information
    display = (
        f"Activity: {activity.name} | "
        f"Units: {log_entry.units} {activity.unit} | "
        f"Timestamp: {timestamp_str} | "
        f"Child: {user.display_name}"
    )
    
    return display


class TestPendingVerificationDisplayProperty:
    """Property-based tests for pending verification display"""
    
    @given(
        valid_pending_log_data(),
        valid_activity_data(),
        valid_user_data()
    )
    @settings(max_examples=100)
    def test_property_16_pending_verification_display_completeness(
        self,
        log_data,
        activity_data,
        user_data
    ):
        """
        Feature: gamified-activity-tracker, Property 16: Pending verification display completeness
        
        For any pending log entry displayed in the verification interface, the rendered output
        should contain the activity name, units logged, timestamp, and child name.
        
        Validates: Requirements 9.3
        """
        # Ensure the log, activity, and user are from the same family
        family_id = log_data['family_id']
        activity_data['family_id'] = family_id
        user_data['family_id'] = family_id
        
        # Ensure the log references the correct activity and user
        activity_data['id'] = log_data['activity_id']
        user_data['uid'] = log_data['user_id']
        
        # Create model instances
        log_entry = LogEntry(**log_data)
        activity = Activity(**activity_data)
        user = User(**user_data)
        
        # Verify the log entry is pending
        assert log_entry.verification_status == 'pending', \
            "Test should only run on pending log entries"
        
        # Format the display output
        display_output = format_pending_verification_display(log_entry, activity, user)
        
        # Verify all required information is present in the display output
        
        # 1. Activity name must be present
        assert activity.name in display_output, \
            f"Display output must contain activity name '{activity.name}', got: {display_output}"
        
        # 2. Units logged must be present
        assert str(log_entry.units) in display_output, \
            f"Display output must contain units '{log_entry.units}', got: {display_output}"
        
        # 3. Timestamp must be present (in some formatted form)
        # We check for year, month, day components to be flexible with formatting
        timestamp_components = [
            str(log_entry.timestamp.year),
            str(log_entry.timestamp.month).zfill(2),
            str(log_entry.timestamp.day).zfill(2)
        ]
        assert any(component in display_output for component in timestamp_components), \
            f"Display output must contain timestamp information from {log_entry.timestamp}, got: {display_output}"
        
        # 4. Child name must be present
        assert user.display_name in display_output, \
            f"Display output must contain child name '{user.display_name}', got: {display_output}"
        
        # Additional verification: ensure the display is not empty
        assert len(display_output) > 0, \
            "Display output must not be empty"
        
        # Verify that the display contains meaningful content (not just whitespace)
        assert display_output.strip() != "", \
            "Display output must contain meaningful content"
    
    @given(
        st.lists(
            st.tuples(
                valid_pending_log_data(),
                valid_activity_data(),
                valid_user_data()
            ),
            min_size=1,
            max_size=10
        )
    )
    @settings(max_examples=100)
    def test_multiple_pending_verifications_all_contain_required_info(self, verification_data_list):
        """
        Test that when displaying multiple pending verifications, each one contains
        all required information.
        
        Related to Property 16 - validates completeness across multiple entries
        """
        for log_data, activity_data, user_data in verification_data_list:
            # Ensure consistency
            family_id = log_data['family_id']
            activity_data['family_id'] = family_id
            user_data['family_id'] = family_id
            activity_data['id'] = log_data['activity_id']
            user_data['uid'] = log_data['user_id']
            
            # Create model instances
            log_entry = LogEntry(**log_data)
            activity = Activity(**activity_data)
            user = User(**user_data)
            
            # Format display
            display_output = format_pending_verification_display(log_entry, activity, user)
            
            # Verify all required information is present
            assert activity.name in display_output, \
                f"Each display must contain activity name"
            assert str(log_entry.units) in display_output, \
                f"Each display must contain units"
            assert user.display_name in display_output, \
                f"Each display must contain child name"
            
            # Verify timestamp is present
            timestamp_components = [
                str(log_entry.timestamp.year),
                str(log_entry.timestamp.month).zfill(2),
                str(log_entry.timestamp.day).zfill(2)
            ]
            assert any(component in display_output for component in timestamp_components), \
                f"Each display must contain timestamp information"
    
    @given(
        valid_pending_log_data(),
        valid_activity_data(),
        valid_user_data()
    )
    @settings(max_examples=100)
    def test_display_distinguishes_different_log_entries(
        self,
        log_data,
        activity_data,
        user_data
    ):
        """
        Test that different log entries produce distinguishable display outputs.
        
        Related to Property 16 - validates that display information is specific to each log
        """
        # Ensure consistency
        family_id = log_data['family_id']
        activity_data['family_id'] = family_id
        user_data['family_id'] = family_id
        activity_data['id'] = log_data['activity_id']
        user_data['uid'] = log_data['user_id']
        
        # Create first log entry
        log_entry1 = LogEntry(**log_data)
        activity1 = Activity(**activity_data)
        user1 = User(**user_data)
        
        display1 = format_pending_verification_display(log_entry1, activity1, user1)
        
        # Create a second log entry with different data
        log_data2 = log_data.copy()
        log_data2['id'] = log_data['id'] + '_different'
        log_data2['units'] = log_data['units'] + 1
        
        activity_data2 = activity_data.copy()
        activity_data2['name'] = activity_data['name'] + ' Modified'
        
        log_entry2 = LogEntry(**log_data2)
        activity2 = Activity(**activity_data2)
        user2 = User(**user_data)
        
        display2 = format_pending_verification_display(log_entry2, activity2, user2)
        
        # Verify that the displays are different (they contain different information)
        assert display1 != display2, \
            "Different log entries should produce different display outputs"
        
        # Verify that each display contains its specific information
        assert activity1.name in display1, \
            "Display 1 should contain activity1 name"
        assert activity2.name in display2, \
            "Display 2 should contain activity2 name"
        
        # Verify the modified name is only in display2
        assert " Modified" in display2 and " Modified" not in display1, \
            "Display 2 should contain the modified activity name"
        
        assert str(log_entry1.units) in display1, \
            "Display 1 should contain log1 units"
        assert str(log_entry2.units) in display2, \
            "Display 2 should contain log2 units"
    
    @given(
        valid_pending_log_data(),
        valid_activity_data(),
        valid_user_data()
    )
    @settings(max_examples=100)
    def test_display_only_for_pending_status(
        self,
        log_data,
        activity_data,
        user_data
    ):
        """
        Test that the display function is intended for pending log entries.
        
        Related to Property 16 - validates that this applies to pending verifications
        """
        # Ensure consistency
        family_id = log_data['family_id']
        activity_data['family_id'] = family_id
        user_data['family_id'] = family_id
        activity_data['id'] = log_data['activity_id']
        user_data['uid'] = log_data['user_id']
        
        # Create pending log entry
        log_entry = LogEntry(**log_data)
        activity = Activity(**activity_data)
        user = User(**user_data)
        
        # Verify the log is pending
        assert log_entry.verification_status == 'pending', \
            "This test is for pending log entries"
        
        # Format display
        display_output = format_pending_verification_display(log_entry, activity, user)
        
        # Verify display is created successfully for pending logs
        assert display_output is not None, \
            "Display should be created for pending log entries"
        assert len(display_output) > 0, \
            "Display should contain content for pending log entries"
