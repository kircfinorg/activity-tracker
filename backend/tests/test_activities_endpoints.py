"""
Unit tests for activity endpoints
Tests Requirements 5.1, 5.2, 5.3, 5.4, 11.1
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from main import app

client = TestClient(app)


@pytest.fixture
def mock_firebase():
    """Mock Firebase service for testing"""
    with patch('routers.activities.firebase_service') as mock_service:
        # Mock database
        mock_db = Mock()
        mock_service.get_db.return_value = mock_db
        
        # Mock verify_family_membership
        mock_service.verify_family_membership.return_value = True
        
        yield mock_service, mock_db


@pytest.fixture
def mock_auth_parent():
    """Mock authentication for parent user"""
    with patch('middleware.auth.firebase_service') as mock_service:
        mock_db = Mock()
        mock_service.get_db.return_value = mock_db
        
        # Mock user document
        mock_user_doc = Mock()
        mock_user_doc.exists = True
        mock_user_doc.to_dict.return_value = {
            'uid': 'parent123',
            'role': 'parent',
            'familyId': 'family123'
        }
        
        mock_user_ref = Mock()
        mock_user_ref.get.return_value = mock_user_doc
        mock_db.collection.return_value.document.return_value = mock_user_ref
        
        # Mock token verification
        mock_auth = Mock()
        mock_auth.verify_id_token.return_value = {
            'uid': 'parent123',
            'email': 'parent@test.com'
        }
        mock_service.get_auth.return_value = mock_auth
        
        yield mock_service


class TestCreateActivity:
    """Test activity creation endpoint"""
    
    def test_create_valid_activity(self, mock_firebase, mock_auth_parent):
        """Test creating a valid activity"""
        mock_service, mock_db = mock_firebase
        
        # Mock activity document creation
        mock_activity_ref = Mock()
        mock_activity_ref.id = 'activity123'
        mock_db.collection.return_value.document.return_value = mock_activity_ref
        
        response = client.post(
            "/api/activities",
            json={
                "family_id": "family123",
                "name": "Reading",
                "unit": "Pages",
                "rate": 0.10
            },
            headers={"Authorization": "Bearer valid_token"}
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data['activity']['name'] == 'Reading'
        assert data['activity']['unit'] == 'Pages'
        assert data['activity']['rate'] == 0.10
    
    def test_create_activity_empty_name(self, mock_firebase, mock_auth_parent):
        """Test Requirement 5.2: Empty name should be rejected"""
        response = client.post(
            "/api/activities",
            json={
                "family_id": "family123",
                "name": "",
                "unit": "Pages",
                "rate": 0.10
            },
            headers={"Authorization": "Bearer valid_token"}
        )
        
        assert response.status_code == 422  # Validation error
    
    def test_create_activity_empty_unit(self, mock_firebase, mock_auth_parent):
        """Test Requirement 5.3: Empty unit should be rejected"""
        response = client.post(
            "/api/activities",
            json={
                "family_id": "family123",
                "name": "Reading",
                "unit": "",
                "rate": 0.10
            },
            headers={"Authorization": "Bearer valid_token"}
        )
        
        assert response.status_code == 422  # Validation error
    
    def test_create_activity_zero_rate(self, mock_firebase, mock_auth_parent):
        """Test Requirement 5.4: Zero rate should be rejected"""
        response = client.post(
            "/api/activities",
            json={
                "family_id": "family123",
                "name": "Reading",
                "unit": "Pages",
                "rate": 0.0
            },
            headers={"Authorization": "Bearer valid_token"}
        )
        
        assert response.status_code == 422  # Validation error
    
    def test_create_activity_negative_rate(self, mock_firebase, mock_auth_parent):
        """Test Requirement 5.4: Negative rate should be rejected"""
        response = client.post(
            "/api/activities",
            json={
                "family_id": "family123",
                "name": "Reading",
                "unit": "Pages",
                "rate": -0.10
            },
            headers={"Authorization": "Bearer valid_token"}
        )
        
        assert response.status_code == 422  # Validation error


class TestGetActivities:
    """Test get activities endpoint"""
    
    def test_get_activities_success(self, mock_firebase, mock_auth_parent):
        """Test retrieving activities for a family"""
        mock_service, mock_db = mock_firebase
        
        # Mock activity documents
        mock_activity_doc = Mock()
        mock_activity_doc.to_dict.return_value = {
            'id': 'activity123',
            'familyId': 'family123',
            'name': 'Reading',
            'unit': 'Pages',
            'rate': 0.10,
            'createdBy': 'parent123',
            'createdAt': datetime.utcnow()
        }
        
        mock_query = Mock()
        mock_query.stream.return_value = [mock_activity_doc]
        
        mock_activities_ref = Mock()
        mock_activities_ref.where.return_value = mock_query
        mock_db.collection.return_value = mock_activities_ref
        
        response = client.get(
            "/api/activities/family123",
            headers={"Authorization": "Bearer valid_token"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data['activities']) == 1
        assert data['activities'][0]['name'] == 'Reading'


class TestDeleteActivity:
    """Test delete activity endpoint"""
    
    def test_delete_activity_success(self, mock_firebase, mock_auth_parent):
        """Test Requirement 11.1: Delete activity successfully"""
        mock_service, mock_db = mock_firebase
        
        # Mock activity document
        mock_activity_doc = Mock()
        mock_activity_doc.exists = True
        mock_activity_doc.to_dict.return_value = {
            'id': 'activity123',
            'familyId': 'family123',
            'name': 'Reading'
        }
        
        mock_activity_ref = Mock()
        mock_activity_ref.get.return_value = mock_activity_doc
        
        # Mock logs query for cascade deletion
        mock_log_doc = Mock()
        mock_log_doc.to_dict.return_value = {
            'userId': 'child123',
            'activityId': 'activity123'
        }
        mock_log_doc.reference = Mock()
        
        mock_logs_query = Mock()
        mock_logs_query.stream.return_value = [mock_log_doc]
        
        mock_logs_ref = Mock()
        mock_logs_ref.where.return_value = mock_logs_query
        
        # Setup collection routing
        def collection_side_effect(name):
            if name == 'activities':
                mock_activities_ref = Mock()
                mock_activities_ref.document.return_value = mock_activity_ref
                return mock_activities_ref
            elif name == 'logs':
                return mock_logs_ref
            return Mock()
        
        mock_db.collection.side_effect = collection_side_effect
        
        response = client.delete(
            "/api/activities/activity123",
            headers={"Authorization": "Bearer valid_token"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
        assert '1 log entries removed' in data['message']
        mock_activity_ref.delete.assert_called_once()
        mock_log_doc.reference.delete.assert_called_once()
    
    def test_delete_activity_not_found(self, mock_firebase, mock_auth_parent):
        """Test deleting non-existent activity"""
        mock_service, mock_db = mock_firebase
        
        # Mock activity not found
        mock_activity_doc = Mock()
        mock_activity_doc.exists = False
        
        mock_activity_ref = Mock()
        mock_activity_ref.get.return_value = mock_activity_doc
        mock_db.collection.return_value.document.return_value = mock_activity_ref
        
        response = client.delete(
            "/api/activities/nonexistent",
            headers={"Authorization": "Bearer valid_token"}
        )
        
        assert response.status_code == 404
    
    def test_delete_activity_cascade_multiple_logs(self, mock_firebase, mock_auth_parent):
        """Test Requirement 11.2: Cascade delete multiple log entries"""
        mock_service, mock_db = mock_firebase
        
        # Mock activity document
        mock_activity_doc = Mock()
        mock_activity_doc.exists = True
        mock_activity_doc.to_dict.return_value = {
            'id': 'activity123',
            'familyId': 'family123',
            'name': 'Reading'
        }
        
        mock_activity_ref = Mock()
        mock_activity_ref.get.return_value = mock_activity_doc
        
        # Mock multiple log documents
        mock_log_docs = []
        for i in range(3):
            mock_log_doc = Mock()
            mock_log_doc.to_dict.return_value = {
                'userId': f'child{i}',
                'activityId': 'activity123'
            }
            mock_log_doc.reference = Mock()
            mock_log_docs.append(mock_log_doc)
        
        mock_logs_query = Mock()
        mock_logs_query.stream.return_value = mock_log_docs
        
        mock_logs_ref = Mock()
        mock_logs_ref.where.return_value = mock_logs_query
        
        # Setup collection routing
        def collection_side_effect(name):
            if name == 'activities':
                mock_activities_ref = Mock()
                mock_activities_ref.document.return_value = mock_activity_ref
                return mock_activities_ref
            elif name == 'logs':
                return mock_logs_ref
            return Mock()
        
        mock_db.collection.side_effect = collection_side_effect
        
        response = client.delete(
            "/api/activities/activity123",
            headers={"Authorization": "Bearer valid_token"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
        assert '3 log entries removed' in data['message']
        
        # Verify all logs were deleted
        for log_doc in mock_log_docs:
            log_doc.reference.delete.assert_called_once()
