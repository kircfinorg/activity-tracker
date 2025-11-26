"""
Unit tests for Activity model validation
Tests Requirements 5.2, 5.3, 5.4
"""
import pytest
from datetime import datetime
from pydantic import ValidationError
from models.activity import Activity


class TestActivityValidation:
    """Test Activity model validation rules"""
    
    def test_valid_activity_creation(self):
        """Test that a valid activity can be created"""
        activity = Activity(
            id="activity123",
            family_id="family123",
            name="Reading",
            unit="Pages",
            rate=0.10,
            created_by="user123",
            created_at=datetime.now()
        )
        assert activity.name == "Reading"
        assert activity.unit == "Pages"
        assert activity.rate == 0.10
    
    def test_empty_name_rejected(self):
        """Test Requirement 5.2: Empty name field should be rejected"""
        with pytest.raises(ValidationError) as exc_info:
            Activity(
                id="activity123",
                family_id="family123",
                name="",
                unit="Pages",
                rate=0.10,
                created_by="user123",
                created_at=datetime.now()
            )
        
        errors = exc_info.value.errors()
        assert any('name' in str(error['loc']) for error in errors)
    
    def test_whitespace_only_name_rejected(self):
        """Test Requirement 5.2: Whitespace-only name should be rejected"""
        with pytest.raises(ValidationError) as exc_info:
            Activity(
                id="activity123",
                family_id="family123",
                name="   ",
                unit="Pages",
                rate=0.10,
                created_by="user123",
                created_at=datetime.now()
            )
        
        errors = exc_info.value.errors()
        assert any('name' in str(error['loc']) for error in errors)
    
    def test_empty_unit_rejected(self):
        """Test Requirement 5.3: Empty unit field should be rejected"""
        with pytest.raises(ValidationError) as exc_info:
            Activity(
                id="activity123",
                family_id="family123",
                name="Reading",
                unit="",
                rate=0.10,
                created_by="user123",
                created_at=datetime.now()
            )
        
        errors = exc_info.value.errors()
        assert any('unit' in str(error['loc']) for error in errors)
    
    def test_whitespace_only_unit_rejected(self):
        """Test Requirement 5.3: Whitespace-only unit should be rejected"""
        with pytest.raises(ValidationError) as exc_info:
            Activity(
                id="activity123",
                family_id="family123",
                name="Reading",
                unit="   ",
                rate=0.10,
                created_by="user123",
                created_at=datetime.now()
            )
        
        errors = exc_info.value.errors()
        assert any('unit' in str(error['loc']) for error in errors)
    
    def test_zero_rate_rejected(self):
        """Test Requirement 5.4: Zero rate should be rejected"""
        with pytest.raises(ValidationError) as exc_info:
            Activity(
                id="activity123",
                family_id="family123",
                name="Reading",
                unit="Pages",
                rate=0.0,
                created_by="user123",
                created_at=datetime.now()
            )
        
        errors = exc_info.value.errors()
        assert any('rate' in str(error['loc']) for error in errors)
    
    def test_negative_rate_rejected(self):
        """Test Requirement 5.4: Negative rate should be rejected"""
        with pytest.raises(ValidationError) as exc_info:
            Activity(
                id="activity123",
                family_id="family123",
                name="Reading",
                unit="Pages",
                rate=-0.10,
                created_by="user123",
                created_at=datetime.now()
            )
        
        errors = exc_info.value.errors()
        assert any('rate' in str(error['loc']) for error in errors)
    
    def test_name_whitespace_trimmed(self):
        """Test that leading/trailing whitespace in name is trimmed"""
        activity = Activity(
            id="activity123",
            family_id="family123",
            name="  Reading  ",
            unit="Pages",
            rate=0.10,
            created_by="user123",
            created_at=datetime.now()
        )
        assert activity.name == "Reading"
    
    def test_unit_whitespace_trimmed(self):
        """Test that leading/trailing whitespace in unit is trimmed"""
        activity = Activity(
            id="activity123",
            family_id="family123",
            name="Reading",
            unit="  Pages  ",
            rate=0.10,
            created_by="user123",
            created_at=datetime.now()
        )
        assert activity.unit == "Pages"
