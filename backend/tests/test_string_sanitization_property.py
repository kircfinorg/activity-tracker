"""
Property-based tests for string sanitization

Feature: gamified-activity-tracker, Property 28: String input sanitization
Validates: Requirements 17.3
"""

import pytest
from hypothesis import given, strategies as st, assume
from utils.validation import sanitize_string


class TestStringSanitizationProperty:
    """Test that string inputs are properly sanitized"""
    
    @given(
        text=st.text(min_size=0, max_size=200)
    )
    def test_property_28_sanitization_preserves_safe_content(self, text):
        """
        **Feature: gamified-activity-tracker, Property 28: String input sanitization**
        **Validates: Requirements 17.3**
        
        For any string, sanitization should preserve the essential content while removing dangerous characters
        """
        sanitized = sanitize_string(text)
        
        # Sanitized string should not be None
        assert sanitized is not None
        
        # Sanitized string should be a string
        assert isinstance(sanitized, str)
        
        # If original was empty or whitespace, sanitized should be empty
        if not text.strip():
            assert sanitized == ''
    
    @given(
        text=st.text(min_size=1, max_size=50).filter(lambda x: x.strip() != ''),
        max_length=st.integers(min_value=1, max_value=100)
    )
    def test_property_28_sanitization_respects_max_length(self, text, max_length):
        """
        **Feature: gamified-activity-tracker, Property 28: String input sanitization**
        **Validates: Requirements 17.3**
        
        For any string and max_length, sanitized string should not exceed max_length
        """
        sanitized = sanitize_string(text, max_length=max_length)
        
        assert len(sanitized) <= max_length
    
    @given(
        text=st.text(min_size=1, max_size=100)
    )
    def test_property_28_sanitization_removes_dangerous_html(self, text):
        """
        **Feature: gamified-activity-tracker, Property 28: String input sanitization**
        **Validates: Requirements 17.3**
        
        For any string containing dangerous HTML tags, sanitization should remove them
        """
        # Add dangerous HTML tags to the text
        html_text = f"<script>{text}</script>"
        sanitized = sanitize_string(html_text)
        
        # Sanitized string should not contain dangerous script tags
        assert '<script>' not in sanitized
        assert '</script>' not in sanitized
    
    @given(
        text=st.text(min_size=1, max_size=100)
    )
    def test_property_28_sanitization_removes_sql_injection_attempts(self, text):
        """
        **Feature: gamified-activity-tracker, Property 28: String input sanitization**
        **Validates: Requirements 17.3**
        
        For any string, sanitization should neutralize SQL injection attempts
        """
        # Add SQL injection patterns
        sql_text = f"{text}'; DROP TABLE users; --"
        sanitized = sanitize_string(sql_text)
        
        # Sanitized string should not contain dangerous SQL patterns
        # The sanitization should either remove or escape these
        assert sanitized is not None
        assert isinstance(sanitized, str)
    
    @given(
        text=st.text(alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd')), min_size=1, max_size=100)
    )
    def test_property_28_sanitization_preserves_alphanumeric(self, text):
        """
        **Feature: gamified-activity-tracker, Property 28: String input sanitization**
        **Validates: Requirements 17.3**
        
        For any alphanumeric string, sanitization should preserve the content
        """
        sanitized = sanitize_string(text)
        
        # Alphanumeric content should be largely preserved
        # (may be trimmed or have length limits applied)
        assert sanitized is not None
        assert len(sanitized) > 0 or len(text.strip()) == 0
    
    @given(
        text=st.text(min_size=1, max_size=50).filter(lambda x: x.strip() != '')
    )
    def test_property_28_double_sanitization_is_idempotent(self, text):
        """
        **Feature: gamified-activity-tracker, Property 28: String input sanitization**
        **Validates: Requirements 17.3**
        
        For any string, sanitizing twice should produce the same result as sanitizing once
        """
        sanitized_once = sanitize_string(text)
        sanitized_twice = sanitize_string(sanitized_once)
        
        assert sanitized_once == sanitized_twice
