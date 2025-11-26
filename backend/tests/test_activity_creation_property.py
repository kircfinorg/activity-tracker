"""
Property-based tests for activity creation and validation
Feature: gamified-activity-tracker
Tests Properties 9 and 10
"""
import pytest
from hypothesis import given, strategies as st, settings
from datetime import datetime
from models.activity import Activity
from pydantic import ValidationError


# Generators for property-based testing

@st.composite
def valid_activity_data(draw):
    """Generate valid activity data"""
    return {
        'id': draw(st.text(min_size=1, max_size=50, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd')))),
        'family_id': draw(st.text(min_size=1, max_size=50, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd')))),
        'name': draw(st.text(min_size=1, max_size=100).filter(lambda x: x.strip())),
        'unit': draw(st.text(min_size=1, max_size=50).filter(lambda x: x.strip())),
        'rate': draw(st.floats(min_value=0.01, max_value=1000.0, allow_nan=False, allow_infinity=False)),
        'created_by': draw(st.text(min_size=1, max_size=50, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd')))),
        'created_at': datetime.utcnow()
    }


@st.composite
def invalid_rate_activity_data(draw):
    """Generate activity data with invalid (non-positive) rate"""
    return {
        'id': draw(st.text(min_size=1, max_size=50, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd')))),
        'family_id': draw(st.text(min_size=1, max_size=50, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd')))),
        'name': draw(st.text(min_size=1, max_size=100).filter(lambda x: x.strip())),
        'unit': draw(st.text(min_size=1, max_size=50).filter(lambda x: x.strip())),
        'rate': draw(st.floats(max_value=0.0, allow_nan=False, allow_infinity=False)),
        'created_by': draw(st.text(min_size=1, max_size=50, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd')))),
        'created_at': datetime.utcnow()
    }


class TestActivityCreationProperties:
    """Property-based tests for activity creation"""
    
    @given(valid_activity_data())
    @settings(max_examples=100)
    def test_property_9_activity_creation_with_family_association(self, activity_data):
        """
        Feature: gamified-activity-tracker, Property 9: Activity creation with family association
        
        For any parent user submitting a valid activity (non-empty name and unit, positive rate),
        the Backend Service should create the activity in Firebase and correctly associate it
        with the user's family group.
        
        Validates: Requirements 5.1
        """
        # Create activity using Pydantic model
        activity = Activity(**activity_data)
        
        # Verify activity was created with correct data
        assert activity.id == activity_data['id']
        assert activity.family_id == activity_data['family_id']
        assert activity.name == activity_data['name'].strip()
        assert activity.unit == activity_data['unit'].strip()
        assert activity.rate == activity_data['rate']
        assert activity.created_by == activity_data['created_by']
        
        # Verify family association is correct
        assert activity.family_id is not None
        assert len(activity.family_id) > 0
        
        # Verify all required fields are present
        assert hasattr(activity, 'id')
        assert hasattr(activity, 'family_id')
        assert hasattr(activity, 'name')
        assert hasattr(activity, 'unit')
        assert hasattr(activity, 'rate')
        assert hasattr(activity, 'created_by')
        assert hasattr(activity, 'created_at')
    
    @given(invalid_rate_activity_data())
    @settings(max_examples=100)
    def test_property_10_activity_rate_validation(self, activity_data):
        """
        Feature: gamified-activity-tracker, Property 10: Activity rate validation
        
        For any activity submission with a non-positive rate value (zero or negative),
        the Backend Service should reject the submission and return a validation error.
        
        Validates: Requirements 5.4
        """
        # Attempt to create activity with invalid rate
        with pytest.raises(ValidationError) as exc_info:
            Activity(**activity_data)
        
        # Verify that the error is related to the rate field
        errors = exc_info.value.errors()
        assert any('rate' in str(error['loc']) for error in errors), \
            f"Expected rate validation error, got: {errors}"
        
        # Verify the error message indicates the rate must be positive
        error_messages = [error['msg'] for error in errors]
        assert any('greater than' in msg.lower() for msg in error_messages), \
            f"Expected 'greater than' in error message, got: {error_messages}"
    
    @given(
        st.text(min_size=1, max_size=50, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'))),
        st.text(min_size=1, max_size=50, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'))),
        st.text(min_size=0, max_size=100),  # Can be empty
        st.text(min_size=1, max_size=50).filter(lambda x: x.strip()),
        st.floats(min_value=0.01, max_value=1000.0, allow_nan=False, allow_infinity=False)
    )
    @settings(max_examples=100)
    def test_empty_name_rejected(self, activity_id, family_id, name, unit, rate):
        """
        Test that empty or whitespace-only names are rejected
        Related to Property 9 - validates name requirement
        """
        if not name.strip():
            # Empty or whitespace-only name should be rejected
            with pytest.raises(ValidationError) as exc_info:
                Activity(
                    id=activity_id,
                    family_id=family_id,
                    name=name,
                    unit=unit,
                    rate=rate,
                    created_by='user123',
                    created_at=datetime.utcnow()
                )
            
            errors = exc_info.value.errors()
            assert any('name' in str(error['loc']) for error in errors)
        else:
            # Valid name should be accepted
            activity = Activity(
                id=activity_id,
                family_id=family_id,
                name=name,
                unit=unit,
                rate=rate,
                created_by='user123',
                created_at=datetime.utcnow()
            )
            assert activity.name == name.strip()
    
    @given(
        st.text(min_size=1, max_size=50, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'))),
        st.text(min_size=1, max_size=50, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'))),
        st.text(min_size=1, max_size=100).filter(lambda x: x.strip()),
        st.text(min_size=0, max_size=50),  # Can be empty
        st.floats(min_value=0.01, max_value=1000.0, allow_nan=False, allow_infinity=False)
    )
    @settings(max_examples=100)
    def test_empty_unit_rejected(self, activity_id, family_id, name, unit, rate):
        """
        Test that empty or whitespace-only units are rejected
        Related to Property 9 - validates unit requirement
        """
        if not unit.strip():
            # Empty or whitespace-only unit should be rejected
            with pytest.raises(ValidationError) as exc_info:
                Activity(
                    id=activity_id,
                    family_id=family_id,
                    name=name,
                    unit=unit,
                    rate=rate,
                    created_by='user123',
                    created_at=datetime.utcnow()
                )
            
            errors = exc_info.value.errors()
            assert any('unit' in str(error['loc']) for error in errors)
        else:
            # Valid unit should be accepted
            activity = Activity(
                id=activity_id,
                family_id=family_id,
                name=name,
                unit=unit,
                rate=rate,
                created_by='user123',
                created_at=datetime.utcnow()
            )
            assert activity.unit == unit.strip()
    
    @given(
        st.text(min_size=1, max_size=50, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'))),
        st.text(min_size=1, max_size=50, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'))),
        st.text(min_size=1, max_size=100).filter(lambda x: x.strip()),
        st.text(min_size=1, max_size=50).filter(lambda x: x.strip()),
        st.floats(allow_nan=False, allow_infinity=False)
    )
    @settings(max_examples=100)
    def test_rate_boundary_validation(self, activity_id, family_id, name, unit, rate):
        """
        Test rate validation across all possible float values
        Related to Property 10 - comprehensive rate validation
        """
        if rate > 0:
            # Positive rate should be accepted
            activity = Activity(
                id=activity_id,
                family_id=family_id,
                name=name,
                unit=unit,
                rate=rate,
                created_by='user123',
                created_at=datetime.utcnow()
            )
            assert activity.rate == rate
        else:
            # Zero or negative rate should be rejected
            with pytest.raises(ValidationError) as exc_info:
                Activity(
                    id=activity_id,
                    family_id=family_id,
                    name=name,
                    unit=unit,
                    rate=rate,
                    created_by='user123',
                    created_at=datetime.utcnow()
                )
            
            errors = exc_info.value.errors()
            assert any('rate' in str(error['loc']) for error in errors)
