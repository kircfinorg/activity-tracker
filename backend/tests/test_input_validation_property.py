"""
Property-based tests for input validation

Feature: gamified-activity-tracker, Property 27: Input validation and rejection
Validates: Requirements 17.1, 17.2
"""

import pytest
from hypothesis import given, strategies as st, assume
from pydantic import ValidationError
from models.activity import Activity
from models.log_entry import LogEntry
from utils.validation import sanitize_string, validate_role
from datetime import datetime


class TestInputValidationProperty:
    """Test that invalid inputs are properly rejected"""
    
    @given(
        name=st.text(min_size=0, max_size=5).filter(lambda x: x.strip() == ''),
        unit=st.text(min_size=1, max_size=20),
        rate=st.floats(min_value=0.01, max_value=1000.0)
    )
    def test_property_27_empty_activity_name_rejected(self, name, unit, rate):
        """
        **Feature: gamified-activity-tracker, Property 27: Input validation and rejection**
        **Validates: Requirements 17.1, 17.2**
        
        For any activity with empty or whitespace-only name, validation should reject it
        """
        with pytest.raises(ValidationError) as exc_info:
            Activity(
                id="test_id",
                family_id="test_family",
                name=name,
                unit=unit,
                rate=rate,
                created_by="test_user",
                created_at=datetime.utcnow()
            )
        
        # Verify the error is about the name field
        errors = exc_info.value.errors()
        assert any('name' in str(error.get('loc', [])) for error in errors)
    
    @given(
        name=st.text(min_size=1, max_size=50).filter(lambda x: x.strip() != ''),
        unit=st.text(min_size=0, max_size=5).filter(lambda x: x.strip() == ''),
        rate=st.floats(min_value=0.01, max_value=1000.0)
    )
    def test_property_27_empty_activity_unit_rejected(self, name, unit, rate):
        """
        **Feature: gamified-activity-tracker, Property 27: Input validation and rejection**
        **Validates: Requirements 17.1, 17.2**
        
        For any activity with empty or whitespace-only unit, validation should reject it
        """
        with pytest.raises(ValidationError) as exc_info:
            Activity(
                id="test_id",
                family_id="test_family",
                name=name,
                unit=unit,
                rate=rate,
                created_by="test_user",
                created_at=datetime.utcnow()
            )
        
        # Verify the error is about the unit field
        errors = exc_info.value.errors()
        assert any('unit' in str(error.get('loc', [])) for error in errors)
    
    @given(
        name=st.text(min_size=1, max_size=50).filter(lambda x: x.strip() != ''),
        unit=st.text(min_size=1, max_size=20).filter(lambda x: x.strip() != ''),
        rate=st.one_of(
            st.floats(max_value=0.0),
            st.floats(min_value=-1000.0, max_value=-0.01)
        )
    )
    def test_property_27_non_positive_rate_rejected(self, name, unit, rate):
        """
        **Feature: gamified-activity-tracker, Property 27: Input validation and rejection**
        **Validates: Requirements 17.1, 17.2**
        
        For any activity with non-positive rate, validation should reject it
        """
        assume(rate <= 0)
        
        with pytest.raises(ValidationError) as exc_info:
            Activity(
                id="test_id",
                family_id="test_family",
                name=name,
                unit=unit,
                rate=rate,
                created_by="test_user",
                created_at=datetime.utcnow()
            )
        
        # Verify the error is about the rate field
        errors = exc_info.value.errors()
        assert any('rate' in str(error.get('loc', [])) for error in errors)
    
    @given(
        units=st.one_of(
            st.integers(max_value=0),
            st.integers(min_value=-1000, max_value=-1)
        )
    )
    def test_property_27_non_positive_log_units_rejected(self, units):
        """
        **Feature: gamified-activity-tracker, Property 27: Input validation and rejection**
        **Validates: Requirements 17.1, 17.2**
        
        For any log entry with non-positive units, validation should reject it
        """
        assume(units <= 0)
        
        with pytest.raises(ValidationError) as exc_info:
            LogEntry(
                id="test_id",
                activity_id="test_activity",
                user_id="test_user",
                family_id="test_family",
                units=units,
                timestamp=datetime.utcnow(),
                verification_status="pending",
                verified_by=None,
                verified_at=None
            )
        
        # Verify the error is about the units field
        errors = exc_info.value.errors()
        assert any('units' in str(error.get('loc', [])) for error in errors)
    
    @given(
        role=st.text(min_size=1, max_size=20).filter(lambda x: x not in ['parent', 'child'])
    )
    def test_property_27_invalid_role_rejected(self, role):
        """
        **Feature: gamified-activity-tracker, Property 27: Input validation and rejection**
        **Validates: Requirements 17.1, 17.2**
        
        For any role that is not 'parent' or 'child', validation should reject it
        """
        with pytest.raises(ValueError) as exc_info:
            validate_role(role)
        
        assert 'role' in str(exc_info.value).lower()
