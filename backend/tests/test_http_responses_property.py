"""
Property-based tests for HTTP response correctness

Feature: gamified-activity-tracker, Property 25 & 26: HTTP status code correctness and error response descriptiveness
Validates: Requirements 15.4, 15.5
"""

import pytest
from hypothesis import given, strategies as st
from fastapi.testclient import TestClient
from main import app
from unittest.mock import Mock, patch
from datetime import datetime


client = TestClient(app)


class TestHTTPResponseProperties:
    """Test that HTTP responses have correct status codes and descriptive messages"""
    
    def test_property_25_successful_operations_return_2xx(self):
        """
        **Feature: gamified-activity-tracker, Property 25: HTTP status code correctness**
        **Validates: Requirements 15.4, 15.5**
        
        For any successful operation, the response should have a 2xx status code
        """
        # Test guest login (should succeed)
        response = client.post(
            "/api/auth/guest-login",
            json={"role": "parent", "display_name": "Test Parent"}
        )
        
        # Should return 201 Created
        assert 200 <= response.status_code < 300
        assert response.status_code == 201
    
    def test_property_25_not_found_returns_404(self):
        """
        **Feature: gamified-activity-tracker, Property 25: HTTP status code correctness**
        **Validates: Requirements 15.4, 15.5**
        
        For any request to a non-existent resource, the response should be 404
        """
        # Mock authentication
        with patch('middleware.auth.verify_token') as mock_verify:
            mock_verify.return_value = {
                'uid': 'test_user',
                'email': 'test@example.com',
                'name': 'Test User'
            }
            
            with patch('services.firebase_service.firebase_service.get_db') as mock_db:
                mock_firestore = Mock()
                mock_db.return_value = mock_firestore
                
                # Mock user document with family
                mock_user_doc = Mock()
                mock_user_doc.exists = True
                mock_user_doc.to_dict.return_value = {
                    'uid': 'test_user',
                    'role': 'parent',
                    'familyId': 'test_family'
                }
                
                # Mock activity document (not found)
                mock_activity_doc = Mock()
                mock_activity_doc.exists = False
                
                # Set up the mock chain
                def mock_collection(name):
                    collection_mock = Mock()
                    def mock_document(doc_id):
                        doc_mock = Mock()
                        if name == 'users':
                            doc_mock.get.return_value = mock_user_doc
                        elif name == 'activities':
                            doc_mock.get.return_value = mock_activity_doc
                        return doc_mock
                    collection_mock.document = mock_document
                    return collection_mock
                
                mock_firestore.collection = mock_collection
                
                # Try to delete non-existent activity
                response = client.delete(
                    "/api/activities/nonexistent_activity_id",
                    headers={"Authorization": "Bearer test_token"}
                )
                
                assert response.status_code == 404
    
    def test_property_25_unauthorized_returns_401_or_403(self):
        """
        **Feature: gamified-activity-tracker, Property 25: HTTP status code correctness**
        **Validates: Requirements 15.4, 15.5**
        
        For any request without valid authentication, the response should be 401 or 403
        """
        # Try to access protected endpoint without token
        response = client.get("/api/auth/profile")
        
        # FastAPI returns 403 for missing authentication
        assert response.status_code in [401, 403]
    
    def test_property_25_forbidden_returns_403(self):
        """
        **Feature: gamified-activity-tracker, Property 25: HTTP status code correctness**
        **Validates: Requirements 15.4, 15.5**
        
        For any request with insufficient permissions, the response should be 403
        """
        # Mock authentication as child trying to access parent endpoint
        with patch('middleware.auth.verify_token') as mock_verify:
            mock_verify.return_value = {
                'uid': 'test_child',
                'email': 'child@example.com',
                'name': 'Test Child'
            }
            
            with patch('services.firebase_service.firebase_service.get_db') as mock_db:
                mock_firestore = Mock()
                mock_db.return_value = mock_firestore
                
                # Mock user document with child role
                mock_user_doc = Mock()
                mock_user_doc.exists = True
                mock_user_doc.to_dict.return_value = {
                    'uid': 'test_child',
                    'role': 'child',
                    'familyId': 'test_family'
                }
                mock_firestore.collection.return_value.document.return_value.get.return_value = mock_user_doc
                
                # Try to create activity (parent-only operation)
                response = client.post(
                    "/api/activities",
                    json={
                        "name": "Test Activity",
                        "unit": "times",
                        "rate": 1.0,
                        "family_id": "test_family"
                    },
                    headers={"Authorization": "Bearer test_token"}
                )
                
                assert response.status_code == 403
    
    @given(
        name=st.text(min_size=0, max_size=5).filter(lambda x: x.strip() == '')
    )
    def test_property_25_validation_errors_return_400(self, name):
        """
        **Feature: gamified-activity-tracker, Property 25: HTTP status code correctness**
        **Validates: Requirements 15.4, 15.5**
        
        For any request with invalid data, the response should be 400
        """
        # Mock authentication
        with patch('middleware.auth.verify_token') as mock_verify:
            mock_verify.return_value = {
                'uid': 'test_user',
                'email': 'test@example.com',
                'name': 'Test User'
            }
            
            with patch('services.firebase_service.firebase_service.get_db') as mock_db:
                mock_firestore = Mock()
                mock_db.return_value = mock_firestore
                
                # Mock user document
                mock_user_doc = Mock()
                mock_user_doc.exists = True
                mock_user_doc.to_dict.return_value = {
                    'uid': 'test_user',
                    'role': 'parent',
                    'familyId': 'test_family'
                }
                mock_firestore.collection.return_value.document.return_value.get.return_value = mock_user_doc
                
                # Try to create activity with invalid name
                response = client.post(
                    "/api/activities",
                    json={
                        "name": name,
                        "unit": "times",
                        "rate": 1.0,
                        "family_id": "test_family"
                    },
                    headers={"Authorization": "Bearer test_token"}
                )
                
                assert response.status_code == 400 or response.status_code == 422
    
    def test_property_26_error_responses_contain_detail(self):
        """
        **Feature: gamified-activity-tracker, Property 26: Error response descriptiveness**
        **Validates: Requirements 15.4, 15.5**
        
        For any error response, it should contain a descriptive detail message
        """
        # Try to access protected endpoint without token
        response = client.get("/api/auth/profile")
        
        assert response.status_code in [401, 403]
        data = response.json()
        
        # Should have a detail field with descriptive message
        assert 'detail' in data or 'message' in data
        
        detail = data.get('detail') or data.get('message')
        assert detail is not None
        assert len(detail) > 0
        assert isinstance(detail, str)
    
    def test_property_26_validation_errors_are_descriptive(self):
        """
        **Feature: gamified-activity-tracker, Property 26: Error response descriptiveness**
        **Validates: Requirements 15.4, 15.5**
        
        For any validation error, the response should describe what went wrong
        """
        # Mock authentication
        with patch('middleware.auth.verify_token') as mock_verify:
            mock_verify.return_value = {
                'uid': 'test_user',
                'email': 'test@example.com',
                'name': 'Test User'
            }
            
            with patch('services.firebase_service.firebase_service.get_db') as mock_db:
                mock_firestore = Mock()
                mock_db.return_value = mock_firestore
                
                # Mock user document
                mock_user_doc = Mock()
                mock_user_doc.exists = True
                mock_user_doc.to_dict.return_value = {
                    'uid': 'test_user',
                    'role': 'parent',
                    'familyId': 'test_family'
                }
                mock_firestore.collection.return_value.document.return_value.get.return_value = mock_user_doc
                
                # Try to create activity with negative rate
                response = client.post(
                    "/api/activities",
                    json={
                        "name": "Test Activity",
                        "unit": "times",
                        "rate": -1.0,
                        "family_id": "test_family"
                    },
                    headers={"Authorization": "Bearer test_token"}
                )
                
                assert response.status_code in [400, 422]
                data = response.json()
                
                # Should have descriptive error information
                assert 'detail' in data or 'message' in data
