import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from main import app

client = TestClient(app)


class TestCreateLog:
    """Test suite for POST /api/logs endpoint"""
    
    @patch('routers.logs.firebase_service')
    @patch('middleware.auth.firebase_service')
    def test_create_log_success(self, mock_auth_firebase, mock_logs_firebase):
        """Test successful log entry creation by child user"""
        # Mock authentication
        mock_auth = Mock()
        mock_auth.verify_id_token.return_value = {'uid': 'child123', 'email': 'child@test.com'}
        mock_auth_firebase.get_auth.return_value = mock_auth
        
        # Mock user document (child role)
        mock_user_doc = Mock()
        mock_user_doc.exists = True
        mock_user_doc.to_dict.return_value = {
            'role': 'child',
            'familyId': 'family123'
        }
        
        # Mock activity document
        mock_activity_doc = Mock()
        mock_activity_doc.exists = True
        mock_activity_doc.to_dict.return_value = {
            'id': 'activity123',
            'familyId': 'family123',
            'name': 'Reading',
            'unit': 'Pages',
            'rate': 0.10
        }
        
        # Mock log document
        mock_log_ref = Mock()
        mock_log_ref.id = 'log123'
        
        # Mock Firestore
        mock_db = Mock()
        mock_users_collection = Mock()
        mock_activities_collection = Mock()
        mock_logs_collection = Mock()
        
        mock_users_collection.document.return_value.get.return_value = mock_user_doc
        mock_activities_collection.document.return_value.get.return_value = mock_activity_doc
        mock_logs_collection.document.return_value = mock_log_ref
        
        mock_db.collection.side_effect = lambda name: {
            'users': mock_users_collection,
            'activities': mock_activities_collection,
            'logs': mock_logs_collection
        }[name]
        
        mock_auth_firebase.get_db.return_value = mock_db
        mock_logs_firebase.get_db.return_value = mock_db
        mock_logs_firebase.verify_family_membership.return_value = True
        
        # Make request
        response = client.post(
            "/api/logs",
            json={
                "activity_id": "activity123",
                "units": 5
            },
            headers={"Authorization": "Bearer valid_token"}
        )
        
        assert response.status_code == 201
        data = response.json()
        assert 'log' in data
        assert data['log']['activity_id'] == 'activity123'
        assert data['log']['user_id'] == 'child123'
        assert data['log']['family_id'] == 'family123'
        assert data['log']['units'] == 5
        assert data['log']['verification_status'] == 'pending'
        assert data['log']['verified_by'] is None
        assert data['log']['verified_at'] is None
    
    @patch('routers.logs.firebase_service')
    @patch('middleware.auth.firebase_service')
    def test_create_log_activity_not_found(self, mock_auth_firebase, mock_logs_firebase):
        """Test log creation fails when activity doesn't exist"""
        # Mock authentication
        mock_auth = Mock()
        mock_auth.verify_id_token.return_value = {'uid': 'child123', 'email': 'child@test.com'}
        mock_auth_firebase.get_auth.return_value = mock_auth
        
        # Mock user document (child role)
        mock_user_doc = Mock()
        mock_user_doc.exists = True
        mock_user_doc.to_dict.return_value = {
            'role': 'child',
            'familyId': 'family123'
        }
        
        # Mock activity document (not found)
        mock_activity_doc = Mock()
        mock_activity_doc.exists = False
        
        # Mock Firestore
        mock_db = Mock()
        mock_users_collection = Mock()
        mock_activities_collection = Mock()
        
        mock_users_collection.document.return_value.get.return_value = mock_user_doc
        mock_activities_collection.document.return_value.get.return_value = mock_activity_doc
        
        mock_db.collection.side_effect = lambda name: {
            'users': mock_users_collection,
            'activities': mock_activities_collection
        }[name]
        
        mock_auth_firebase.get_db.return_value = mock_db
        mock_logs_firebase.get_db.return_value = mock_db
        
        # Make request
        response = client.post(
            "/api/logs",
            json={
                "activity_id": "nonexistent",
                "units": 5
            },
            headers={"Authorization": "Bearer valid_token"}
        )
        
        assert response.status_code == 404
        assert "Activity not found" in response.json()['detail']
    
    @patch('routers.logs.firebase_service')
    @patch('middleware.auth.firebase_service')
    def test_create_log_invalid_units(self, mock_auth_firebase, mock_logs_firebase):
        """Test log creation fails with zero or negative units"""
        # Mock authentication
        mock_auth = Mock()
        mock_auth.verify_id_token.return_value = {'uid': 'child123', 'email': 'child@test.com'}
        mock_auth_firebase.get_auth.return_value = mock_auth
        
        # Mock user document (child role)
        mock_user_doc = Mock()
        mock_user_doc.exists = True
        mock_user_doc.to_dict.return_value = {
            'role': 'child',
            'familyId': 'family123'
        }
        
        mock_db = Mock()
        mock_users_collection = Mock()
        mock_users_collection.document.return_value.get.return_value = mock_user_doc
        mock_db.collection.return_value = mock_users_collection
        
        mock_auth_firebase.get_db.return_value = mock_db
        
        # Test with zero units
        response = client.post(
            "/api/logs",
            json={
                "activity_id": "activity123",
                "units": 0
            },
            headers={"Authorization": "Bearer valid_token"}
        )
        
        assert response.status_code == 422  # Validation error
        
        # Test with negative units
        response = client.post(
            "/api/logs",
            json={
                "activity_id": "activity123",
                "units": -5
            },
            headers={"Authorization": "Bearer valid_token"}
        )
        
        assert response.status_code == 422  # Validation error
    
    @patch('routers.logs.firebase_service')
    @patch('middleware.auth.firebase_service')
    def test_create_log_parent_rejected(self, mock_auth_firebase, mock_logs_firebase):
        """Test that parent users cannot create log entries"""
        # Mock authentication
        mock_auth = Mock()
        mock_auth.verify_id_token.return_value = {'uid': 'parent123', 'email': 'parent@test.com'}
        mock_auth_firebase.get_auth.return_value = mock_auth
        
        # Mock user document (parent role)
        mock_user_doc = Mock()
        mock_user_doc.exists = True
        mock_user_doc.to_dict.return_value = {
            'role': 'parent',
            'familyId': 'family123'
        }
        
        mock_db = Mock()
        mock_users_collection = Mock()
        mock_users_collection.document.return_value.get.return_value = mock_user_doc
        mock_db.collection.return_value = mock_users_collection
        
        mock_auth_firebase.get_db.return_value = mock_db
        
        # Make request
        response = client.post(
            "/api/logs",
            json={
                "activity_id": "activity123",
                "units": 5
            },
            headers={"Authorization": "Bearer valid_token"}
        )
        
        assert response.status_code == 403
        assert "child" in response.json()['detail'].lower()
    
    @patch('routers.logs.firebase_service')
    @patch('middleware.auth.firebase_service')
    def test_create_log_cross_family_rejected(self, mock_auth_firebase, mock_logs_firebase):
        """Test that users cannot log activities from other families"""
        # Mock authentication
        mock_auth = Mock()
        mock_auth.verify_id_token.return_value = {'uid': 'child123', 'email': 'child@test.com'}
        mock_auth_firebase.get_auth.return_value = mock_auth
        
        # Mock user document (child role in family123)
        mock_user_doc = Mock()
        mock_user_doc.exists = True
        mock_user_doc.to_dict.return_value = {
            'role': 'child',
            'familyId': 'family123'
        }
        
        # Mock activity document (belongs to family456)
        mock_activity_doc = Mock()
        mock_activity_doc.exists = True
        mock_activity_doc.to_dict.return_value = {
            'id': 'activity123',
            'familyId': 'family456',  # Different family
            'name': 'Reading',
            'unit': 'Pages',
            'rate': 0.10
        }
        
        # Mock Firestore
        mock_db = Mock()
        mock_users_collection = Mock()
        mock_activities_collection = Mock()
        
        mock_users_collection.document.return_value.get.return_value = mock_user_doc
        mock_activities_collection.document.return_value.get.return_value = mock_activity_doc
        
        mock_db.collection.side_effect = lambda name: {
            'users': mock_users_collection,
            'activities': mock_activities_collection
        }[name]
        
        mock_auth_firebase.get_db.return_value = mock_db
        mock_logs_firebase.get_db.return_value = mock_db
        mock_logs_firebase.verify_family_membership.return_value = False
        
        # Make request
        response = client.post(
            "/api/logs",
            json={
                "activity_id": "activity123",
                "units": 5
            },
            headers={"Authorization": "Bearer valid_token"}
        )
        
        assert response.status_code == 403
        assert "Access denied" in response.json()['detail']
    
    @patch('routers.logs.firebase_service')
    @patch('middleware.auth.firebase_service')
    def test_create_log_multiple_entries_independence(self, mock_auth_firebase, mock_logs_firebase):
        """Test that multiple log entries for the same activity are independent"""
        # Mock authentication
        mock_auth = Mock()
        mock_auth.verify_id_token.return_value = {'uid': 'child123', 'email': 'child@test.com'}
        mock_auth_firebase.get_auth.return_value = mock_auth
        
        # Mock user document (child role)
        mock_user_doc = Mock()
        mock_user_doc.exists = True
        mock_user_doc.to_dict.return_value = {
            'role': 'child',
            'familyId': 'family123'
        }
        
        # Mock activity document
        mock_activity_doc = Mock()
        mock_activity_doc.exists = True
        mock_activity_doc.to_dict.return_value = {
            'id': 'activity123',
            'familyId': 'family123',
            'name': 'Reading',
            'unit': 'Pages',
            'rate': 0.10
        }
        
        # Mock log documents with different IDs
        log_ids = ['log123', 'log456', 'log789']
        log_id_index = [0]
        
        def get_log_ref():
            mock_log_ref = Mock()
            mock_log_ref.id = log_ids[log_id_index[0]]
            log_id_index[0] += 1
            return mock_log_ref
        
        # Mock Firestore
        mock_db = Mock()
        mock_users_collection = Mock()
        mock_activities_collection = Mock()
        mock_logs_collection = Mock()
        
        mock_users_collection.document.return_value.get.return_value = mock_user_doc
        mock_activities_collection.document.return_value.get.return_value = mock_activity_doc
        mock_logs_collection.document.side_effect = get_log_ref
        
        mock_db.collection.side_effect = lambda name: {
            'users': mock_users_collection,
            'activities': mock_activities_collection,
            'logs': mock_logs_collection
        }[name]
        
        mock_auth_firebase.get_db.return_value = mock_db
        mock_logs_firebase.get_db.return_value = mock_db
        mock_logs_firebase.verify_family_membership.return_value = True
        
        # Create multiple log entries
        log_entries = []
        for i in range(3):
            response = client.post(
                "/api/logs",
                json={
                    "activity_id": "activity123",
                    "units": i + 1
                },
                headers={"Authorization": "Bearer valid_token"}
            )
            
            assert response.status_code == 201
            log_entries.append(response.json()['log'])
        
        # Verify each log entry is independent
        assert len(log_entries) == 3
        assert log_entries[0]['id'] != log_entries[1]['id']
        assert log_entries[1]['id'] != log_entries[2]['id']
        assert log_entries[0]['units'] == 1
        assert log_entries[1]['units'] == 2
        assert log_entries[2]['units'] == 3
