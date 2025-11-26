"""
Tests for verification endpoints

Validates: Requirements 7.1, 7.2, 7.3, 9.3
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from main import app

client = TestClient(app)


class TestGetPendingLogs:
    """Tests for GET /api/logs/{family_id}/pending endpoint"""
    
    @patch('routers.logs.firebase_service')
    @patch('middleware.auth.firebase_service')
    def test_get_pending_logs_success(self, mock_auth_service, mock_logs_service):
        """Test successfully retrieving pending logs for a family"""
        # Mock authentication
        mock_auth = mock_auth_service.get_auth.return_value
        mock_auth.verify_id_token.return_value = {'uid': 'parent123'}
        
        # Mock user role check
        mock_user_doc = Mock()
        mock_user_doc.exists = True
        mock_user_doc.to_dict.return_value = {
            'role': 'parent',
            'familyId': 'family123'
        }
        mock_auth_service.get_db.return_value.collection.return_value.document.return_value.get.return_value = mock_user_doc
        
        # Mock family membership verification
        mock_auth_service.verify_family_membership.return_value = True
        mock_logs_service.verify_family_membership.return_value = True
        
        # Mock pending logs query
        mock_log1 = Mock()
        mock_log1.to_dict.return_value = {
            'id': 'log1',
            'activityId': 'activity1',
            'userId': 'child1',
            'familyId': 'family123',
            'units': 2,
            'timestamp': datetime(2024, 1, 1, 12, 0, 0),
            'verificationStatus': 'pending',
            'verifiedBy': None,
            'verifiedAt': None
        }
        
        mock_log2 = Mock()
        mock_log2.to_dict.return_value = {
            'id': 'log2',
            'activityId': 'activity2',
            'userId': 'child2',
            'familyId': 'family123',
            'units': 1,
            'timestamp': datetime(2024, 1, 1, 13, 0, 0),
            'verificationStatus': 'pending',
            'verifiedBy': None,
            'verifiedAt': None
        }
        
        mock_query = Mock()
        mock_query.stream.return_value = [mock_log1, mock_log2]
        
        mock_logs_ref = Mock()
        mock_logs_ref.where.return_value.where.return_value = mock_query
        
        mock_logs_service.get_db.return_value.collection.return_value = mock_logs_ref
        
        # Make request
        response = client.get(
            '/api/logs/family123/pending',
            headers={'Authorization': 'Bearer test_token'}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert 'logs' in data
        assert len(data['logs']) == 2
        assert data['logs'][0]['id'] == 'log1'
        assert data['logs'][1]['id'] == 'log2'
    
    @patch('routers.logs.firebase_service')
    @patch('middleware.auth.firebase_service')
    def test_get_pending_logs_not_family_member(self, mock_auth_service, mock_logs_service):
        """Test that non-family members cannot access pending logs"""
        # Mock authentication
        mock_auth = mock_auth_service.get_auth.return_value
        mock_auth.verify_id_token.return_value = {'uid': 'parent123'}
        
        # Mock user role check
        mock_user_doc = Mock()
        mock_user_doc.exists = True
        mock_user_doc.to_dict.return_value = {
            'role': 'parent',
            'familyId': 'family456'  # Different family
        }
        mock_auth_service.get_db.return_value.collection.return_value.document.return_value.get.return_value = mock_user_doc
        
        # Mock family membership verification - user not in family
        mock_logs_service.verify_family_membership.return_value = False
        
        # Make request
        response = client.get(
            '/api/logs/family123/pending',
            headers={'Authorization': 'Bearer test_token'}
        )
        
        assert response.status_code == 403
        assert 'Access denied' in response.json()['detail']
    
    @patch('routers.logs.firebase_service')
    @patch('middleware.auth.firebase_service')
    def test_get_pending_logs_child_rejected(self, mock_auth_service, mock_logs_service):
        """Test that children cannot access pending logs endpoint"""
        # Mock authentication
        mock_auth = mock_auth_service.get_auth.return_value
        mock_auth.verify_id_token.return_value = {'uid': 'child123'}
        
        # Mock user role check - child role
        mock_user_doc = Mock()
        mock_user_doc.exists = True
        mock_user_doc.to_dict.return_value = {
            'role': 'child',
            'familyId': 'family123'
        }
        mock_auth_service.get_db.return_value.collection.return_value.document.return_value.get.return_value = mock_user_doc
        
        # Make request
        response = client.get(
            '/api/logs/family123/pending',
            headers={'Authorization': 'Bearer test_token'}
        )
        
        assert response.status_code == 403
        assert 'parent' in response.json()['detail'].lower()


class TestVerifyLog:
    """Tests for PATCH /api/logs/{log_id}/verify endpoint"""
    
    @patch('routers.logs.firebase_service')
    @patch('middleware.auth.firebase_service')
    def test_verify_log_approve_success(self, mock_auth_service, mock_logs_service):
        """Test successfully approving a log entry"""
        # Mock authentication
        mock_auth = mock_auth_service.get_auth.return_value
        mock_auth.verify_id_token.return_value = {'uid': 'parent123'}
        
        # Mock user role check
        mock_user_doc = Mock()
        mock_user_doc.exists = True
        mock_user_doc.to_dict.return_value = {
            'role': 'parent',
            'familyId': 'family123'
        }
        mock_auth_service.get_db.return_value.collection.return_value.document.return_value.get.return_value = mock_user_doc
        
        # Mock family membership verification
        mock_logs_service.verify_family_membership.return_value = True
        
        # Mock log document
        mock_log_doc = Mock()
        mock_log_doc.exists = True
        mock_log_doc.to_dict.return_value = {
            'id': 'log1',
            'activityId': 'activity1',
            'userId': 'child1',
            'familyId': 'family123',
            'units': 2,
            'timestamp': datetime(2024, 1, 1, 12, 0, 0),
            'verificationStatus': 'pending',
            'verifiedBy': None,
            'verifiedAt': None
        }
        
        # Mock updated log document
        mock_updated_log_doc = Mock()
        mock_updated_log_doc.to_dict.return_value = {
            'id': 'log1',
            'activityId': 'activity1',
            'userId': 'child1',
            'familyId': 'family123',
            'units': 2,
            'timestamp': datetime(2024, 1, 1, 12, 0, 0),
            'verificationStatus': 'approved',
            'verifiedBy': 'parent123',
            'verifiedAt': datetime(2024, 1, 1, 14, 0, 0)
        }
        
        mock_log_ref = Mock()
        mock_log_ref.get.side_effect = [mock_log_doc, mock_updated_log_doc]
        mock_log_ref.update = Mock()
        
        mock_logs_service.get_db.return_value.collection.return_value.document.return_value = mock_log_ref
        
        # Make request
        response = client.patch(
            '/api/logs/log1/verify',
            json={'status': 'approved'},
            headers={'Authorization': 'Bearer test_token'}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data['log']['id'] == 'log1'
        assert data['log']['verification_status'] == 'approved'
        assert data['log']['verified_by'] == 'parent123'
        
        # Verify update was called
        mock_log_ref.update.assert_called_once()
    
    @patch('routers.logs.firebase_service')
    @patch('middleware.auth.firebase_service')
    def test_verify_log_reject_success(self, mock_auth_service, mock_logs_service):
        """Test successfully rejecting a log entry"""
        # Mock authentication
        mock_auth = mock_auth_service.get_auth.return_value
        mock_auth.verify_id_token.return_value = {'uid': 'parent123'}
        
        # Mock user role check
        mock_user_doc = Mock()
        mock_user_doc.exists = True
        mock_user_doc.to_dict.return_value = {
            'role': 'parent',
            'familyId': 'family123'
        }
        mock_auth_service.get_db.return_value.collection.return_value.document.return_value.get.return_value = mock_user_doc
        
        # Mock family membership verification
        mock_logs_service.verify_family_membership.return_value = True
        
        # Mock log document
        mock_log_doc = Mock()
        mock_log_doc.exists = True
        mock_log_doc.to_dict.return_value = {
            'id': 'log1',
            'activityId': 'activity1',
            'userId': 'child1',
            'familyId': 'family123',
            'units': 2,
            'timestamp': datetime(2024, 1, 1, 12, 0, 0),
            'verificationStatus': 'pending',
            'verifiedBy': None,
            'verifiedAt': None
        }
        
        # Mock updated log document
        mock_updated_log_doc = Mock()
        mock_updated_log_doc.to_dict.return_value = {
            'id': 'log1',
            'activityId': 'activity1',
            'userId': 'child1',
            'familyId': 'family123',
            'units': 2,
            'timestamp': datetime(2024, 1, 1, 12, 0, 0),
            'verificationStatus': 'rejected',
            'verifiedBy': 'parent123',
            'verifiedAt': datetime(2024, 1, 1, 14, 0, 0)
        }
        
        mock_log_ref = Mock()
        mock_log_ref.get.side_effect = [mock_log_doc, mock_updated_log_doc]
        mock_log_ref.update = Mock()
        
        mock_logs_service.get_db.return_value.collection.return_value.document.return_value = mock_log_ref
        
        # Make request
        response = client.patch(
            '/api/logs/log1/verify',
            json={'status': 'rejected'},
            headers={'Authorization': 'Bearer test_token'}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data['log']['verification_status'] == 'rejected'
    
    @patch('routers.logs.firebase_service')
    @patch('middleware.auth.firebase_service')
    def test_verify_log_not_found(self, mock_auth_service, mock_logs_service):
        """Test verifying a non-existent log entry"""
        # Mock authentication
        mock_auth = mock_auth_service.get_auth.return_value
        mock_auth.verify_id_token.return_value = {'uid': 'parent123'}
        
        # Mock user role check
        mock_user_doc = Mock()
        mock_user_doc.exists = True
        mock_user_doc.to_dict.return_value = {
            'role': 'parent',
            'familyId': 'family123'
        }
        mock_auth_service.get_db.return_value.collection.return_value.document.return_value.get.return_value = mock_user_doc
        
        # Mock log document - doesn't exist
        mock_log_doc = Mock()
        mock_log_doc.exists = False
        
        mock_log_ref = Mock()
        mock_log_ref.get.return_value = mock_log_doc
        
        mock_logs_service.get_db.return_value.collection.return_value.document.return_value = mock_log_ref
        
        # Make request
        response = client.patch(
            '/api/logs/nonexistent/verify',
            json={'status': 'approved'},
            headers={'Authorization': 'Bearer test_token'}
        )
        
        assert response.status_code == 404
        assert 'not found' in response.json()['detail'].lower()
    
    @patch('routers.logs.firebase_service')
    @patch('middleware.auth.firebase_service')
    def test_verify_log_already_verified(self, mock_auth_service, mock_logs_service):
        """Test verifying a log that's already been verified"""
        # Mock authentication
        mock_auth = mock_auth_service.get_auth.return_value
        mock_auth.verify_id_token.return_value = {'uid': 'parent123'}
        
        # Mock user role check
        mock_user_doc = Mock()
        mock_user_doc.exists = True
        mock_user_doc.to_dict.return_value = {
            'role': 'parent',
            'familyId': 'family123'
        }
        mock_auth_service.get_db.return_value.collection.return_value.document.return_value.get.return_value = mock_user_doc
        
        # Mock family membership verification
        mock_logs_service.verify_family_membership.return_value = True
        
        # Mock log document - already approved
        mock_log_doc = Mock()
        mock_log_doc.exists = True
        mock_log_doc.to_dict.return_value = {
            'id': 'log1',
            'activityId': 'activity1',
            'userId': 'child1',
            'familyId': 'family123',
            'units': 2,
            'timestamp': datetime(2024, 1, 1, 12, 0, 0),
            'verificationStatus': 'approved',  # Already approved
            'verifiedBy': 'parent456',
            'verifiedAt': datetime(2024, 1, 1, 13, 0, 0)
        }
        
        mock_log_ref = Mock()
        mock_log_ref.get.return_value = mock_log_doc
        
        mock_logs_service.get_db.return_value.collection.return_value.document.return_value = mock_log_ref
        
        # Make request
        response = client.patch(
            '/api/logs/log1/verify',
            json={'status': 'approved'},
            headers={'Authorization': 'Bearer test_token'}
        )
        
        assert response.status_code == 400
        assert 'already' in response.json()['detail'].lower()
    
    @patch('routers.logs.firebase_service')
    @patch('middleware.auth.firebase_service')
    def test_verify_log_child_rejected(self, mock_auth_service, mock_logs_service):
        """Test that children cannot verify logs"""
        # Mock authentication
        mock_auth = mock_auth_service.get_auth.return_value
        mock_auth.verify_id_token.return_value = {'uid': 'child123'}
        
        # Mock user role check - child role
        mock_user_doc = Mock()
        mock_user_doc.exists = True
        mock_user_doc.to_dict.return_value = {
            'role': 'child',
            'familyId': 'family123'
        }
        mock_auth_service.get_db.return_value.collection.return_value.document.return_value.get.return_value = mock_user_doc
        
        # Make request
        response = client.patch(
            '/api/logs/log1/verify',
            json={'status': 'approved'},
            headers={'Authorization': 'Bearer test_token'}
        )
        
        assert response.status_code == 403
        assert 'parent' in response.json()['detail'].lower()
    
    @patch('routers.logs.firebase_service')
    @patch('middleware.auth.firebase_service')
    def test_verify_log_cross_family_rejected(self, mock_auth_service, mock_logs_service):
        """Test that parents cannot verify logs from other families"""
        # Mock authentication
        mock_auth = mock_auth_service.get_auth.return_value
        mock_auth.verify_id_token.return_value = {'uid': 'parent123'}
        
        # Mock user role check
        mock_user_doc = Mock()
        mock_user_doc.exists = True
        mock_user_doc.to_dict.return_value = {
            'role': 'parent',
            'familyId': 'family123'
        }
        mock_auth_service.get_db.return_value.collection.return_value.document.return_value.get.return_value = mock_user_doc
        
        # Mock family membership verification - user not in log's family
        mock_logs_service.verify_family_membership.return_value = False
        
        # Mock log document from different family
        mock_log_doc = Mock()
        mock_log_doc.exists = True
        mock_log_doc.to_dict.return_value = {
            'id': 'log1',
            'activityId': 'activity1',
            'userId': 'child1',
            'familyId': 'family456',  # Different family
            'units': 2,
            'timestamp': datetime(2024, 1, 1, 12, 0, 0),
            'verificationStatus': 'pending',
            'verifiedBy': None,
            'verifiedAt': None
        }
        
        mock_log_ref = Mock()
        mock_log_ref.get.return_value = mock_log_doc
        
        mock_logs_service.get_db.return_value.collection.return_value.document.return_value = mock_log_ref
        
        # Make request
        response = client.patch(
            '/api/logs/log1/verify',
            json={'status': 'approved'},
            headers={'Authorization': 'Bearer test_token'}
        )
        
        assert response.status_code == 403
        assert 'Access denied' in response.json()['detail']
