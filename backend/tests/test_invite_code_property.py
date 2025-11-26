"""
Property-based tests for invite code generation

**Feature: gamified-activity-tracker, Property 2: Invite code uniqueness**
**Validates: Requirements 2.4**
"""
import pytest
from hypothesis import given, strategies as st, settings
from routers.families import generate_invite_code
import string


@settings(max_examples=100)
@given(st.integers(min_value=1, max_value=100))
def test_invite_code_uniqueness_property(num_codes):
    """
    Property test: For any set of generated invite codes, no two codes should be identical
    
    **Feature: gamified-activity-tracker, Property 2: Invite code uniqueness**
    **Validates: Requirements 2.4**
    
    This test generates multiple invite codes and verifies that each one is unique.
    While the generation function itself is random, we test that the probability
    of collisions is extremely low by generating many codes.
    """
    # Generate multiple invite codes
    codes = [generate_invite_code() for _ in range(num_codes)]
    
    # Verify all codes are unique (no duplicates)
    unique_codes = set(codes)
    
    # The property: number of unique codes should equal total codes generated
    # Note: Due to randomness, there's a tiny probability of collision,
    # but with 6 characters from 36 options (26 letters + 10 digits),
    # we have 36^6 = 2,176,782,336 possible codes, so collisions are extremely rare
    assert len(unique_codes) == len(codes), \
        f"Found duplicate codes: {len(codes) - len(unique_codes)} duplicates in {len(codes)} codes"


@settings(max_examples=100)
@given(st.integers(min_value=1, max_value=1000))
def test_invite_code_format_property(seed):
    """
    Property test: For any generated invite code, it should be exactly 6 characters
    and contain only uppercase letters and digits
    
    **Feature: gamified-activity-tracker, Property 2: Invite code uniqueness**
    **Validates: Requirements 2.1**
    
    This test verifies the format constraints of invite codes.
    """
    code = generate_invite_code()
    
    # Verify length is exactly 6
    assert len(code) == 6, f"Invite code length should be 6, got {len(code)}"
    
    # Verify all characters are uppercase letters or digits
    valid_chars = set(string.ascii_uppercase + string.digits)
    code_chars = set(code)
    
    assert code_chars.issubset(valid_chars), \
        f"Invite code contains invalid characters: {code_chars - valid_chars}"
    
    # Verify code is uppercase (no lowercase letters)
    assert code == code.upper(), "Invite code should be all uppercase"


@settings(max_examples=100)
@given(st.integers(min_value=1, max_value=50))
def test_invite_code_collision_rate(batch_size):
    """
    Property test: Verify that collision rate is acceptably low
    
    **Feature: gamified-activity-tracker, Property 2: Invite code uniqueness**
    **Validates: Requirements 2.4**
    
    With 36^6 possible codes, the probability of collision in small batches
    should be negligible. This test verifies that property.
    """
    # Generate a batch of codes
    codes = [generate_invite_code() for _ in range(batch_size)]
    unique_codes = set(codes)
    
    # For small batches (< 1000), we expect no collisions
    # This is a probabilistic test, but the probability of failure is extremely low
    collision_rate = 1 - (len(unique_codes) / len(codes))
    
    # With 36^6 possible codes and small batch sizes, collision rate should be 0
    assert collision_rate == 0, \
        f"Unexpected collision rate: {collision_rate:.4%} in batch of {batch_size}"
