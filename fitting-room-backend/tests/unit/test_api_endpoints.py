import pytest
from unittest.mock import Mock, patch, AsyncMock
from fastapi.testclient import TestClient
from PIL import Image
import io

# Import the app after mocking global variables
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestAPIEndpoints:
    """Test suite for FastAPI endpoints."""
    
    @pytest.fixture
    def client(self):
        """Create a test client with mocked dependencies."""
        # Mock the global services before importing main
        with patch('main.local_service', Mock()) as mock_local_service, \
             patch('main.ai_engine', Mock()) as mock_ai_engine:
            
            # Now import and create the app
            from main import app
            client = TestClient(app)
            
            # Store the mocks for use in tests
            client.mock_local_service = mock_local_service
            client.mock_ai_engine = mock_ai_engine
            
            yield client
    
    def test_get_clothes_endpoint(self, client):
        """Test GET /api/v1/clothes returns list of clothes."""
        # Setup mock
        mock_clothes = ["/static/clothes/shirt1.jpg", "/static/clothes/pants1.png"]
        client.mock_local_service.get_cloth_list.return_value = mock_clothes
        
        # Make request
        response = client.get("/api/v1/clothes")
        
        # Verify response
        assert response.status_code == 200
        assert response.json() == [
            "http://testserver/static/clothes/shirt1.jpg",
            "http://testserver/static/clothes/pants1.png"
        ]
        
        # Verify service was called
        client.mock_local_service.get_cloth_list.assert_called_once()
    
    def test_upload_cloth_endpoint(self, client):
        """Test POST /api/v1/clothes uploads and returns URL."""
        # Setup mock
        mock_file_path = "/static/clothes/test-uuid.jpg"
        client.mock_local_service.save_cloth.return_value = mock_file_path
        
        # Create a test file
        test_file = ("test.jpg", b"fake image data", "image/jpeg")
        
        # Make request
        response = client.post(
            "/api/v1/clothes",
            files={"file": test_file}
        )
        
        # Verify response
        assert response.status_code == 200
        assert response.json() == {"url": "http://testserver/static/clothes/test-uuid.jpg"}
        
        # Verify service was called with file object
        client.mock_local_service.save_cloth.assert_called_once()
        call_arg = client.mock_local_service.save_cloth.call_args[0][0]
        assert call_arg.filename == "test.jpg"
    
    def test_try_on_endpoint_success(self, client):
        """Test POST /api/v1/try-on performs virtual try-on successfully."""
        # Setup mocks
        mock_result_image = Mock(spec=Image.Image)
        mock_result_url = "/static/results/result-uuid.png"
        
        client.mock_local_service.get_absolute_path.return_value = "/absolute/path/to/cloth.jpg"
        client.mock_ai_engine.remove_background.return_value = Mock(spec=Image.Image)
        client.mock_ai_engine.virtual_try_on.return_value = mock_result_image
        client.mock_local_service.save_image_from_bytes.return_value = mock_result_url
        
        # Mock os.path.exists to return True
        with patch('main.os.path.exists', return_value=True):
            # Mock Image.open
            with patch('main.Image.open') as mock_image_open:
                mock_image_open.return_value = Mock(spec=Image.Image)
                
                # Create test files and data
                person_file = ("person.jpg", b"fake person image", "image/jpeg")
                
                # Make request
                response = client.post(
                    "/api/v1/try-on",
                    files={"person_image": person_file},
                    data={
                        "cloth_url": "http://testserver/static/clothes/shirt1.jpg",
                        "category": "upper_body"
                    }
                )
                
                # Verify response
                assert response.status_code == 200
                response_json = response.json()
                assert response_json["status"] == "success"
                assert response_json["result_image_url"] == "http://testserver/static/results/result-uuid.png"
                
                # Verify service calls
                client.mock_local_service.get_absolute_path.assert_called_once_with(
                    "/static/clothes/shirt1.jpg"
                )
                client.mock_ai_engine.remove_background.assert_called_once()
                client.mock_ai_engine.virtual_try_on.assert_called_once()
                client.mock_local_service.save_image_from_bytes.assert_called_once_with(mock_result_image)
    
    def test_try_on_endpoint_cloth_not_found(self, client):
        """Test POST /api/v1/try-on returns 404 when cloth not found."""
        # Setup mock for path exists to return False
        with patch('main.os.path.exists', return_value=False):
            # Mock Image.open to avoid errors with fake image bytes
            with patch('main.Image.open') as mock_image_open:
                # Create test files and data
                person_file = ("person.jpg", b"fake person image", "image/jpeg")
                
                # Make request
                response = client.post(
                    "/api/v1/try-on",
                    files={"person_image": person_file},
                    data={
                        "cloth_url": "http://testserver/static/clothes/nonexistent.jpg",
                        "category": "upper_body"
                    }
                )
                
                # Verify response
                assert response.status_code == 404
                assert "Cloth image not found" in response.json()["detail"]
    
    def test_try_on_endpoint_server_error(self, client):
        """Test POST /api/v1/try-on handles server errors gracefully."""
        # Setup mock to raise exception
        client.mock_local_service.get_absolute_path.return_value = "/absolute/path/to/cloth.jpg"
        
        with patch('main.os.path.exists', return_value=True):
            with patch('main.Image.open', side_effect=Exception("Test error")):
                # Create test files and data
                person_file = ("person.jpg", b"fake person image", "image/jpeg")
                
                # Make request
                response = client.post(
                    "/api/v1/try-on",
                    files={"person_image": person_file},
                    data={
                        "cloth_url": "http://testserver/static/clothes/shirt1.jpg",
                        "category": "upper_body"
                    }
                )
                
                # Verify response
                assert response.status_code == 500
                assert "Test error" in response.json()["detail"]
    
    def test_try_on_endpoint_different_categories(self, client):
        """Test POST /api/v1/try-on handles different clothing categories."""
        test_cases = [
            ("upper_body", "shirt"),
            ("lower_body", "trousers"),
            ("dresses", "dress"),
            ("outer", "dress"),
        ]
        
        for category, expected_vton_desc in test_cases:
            # Reset mocks for each test case
            client.mock_local_service.reset_mock()
            client.mock_ai_engine.reset_mock()
            
            # Setup mocks
            mock_result_image = Mock(spec=Image.Image)
            mock_result_url = "/static/results/result-uuid.png"
            
            client.mock_local_service.get_absolute_path.return_value = "/absolute/path/to/cloth.jpg"
            client.mock_ai_engine.remove_background.return_value = Mock(spec=Image.Image)
            client.mock_ai_engine.virtual_try_on.return_value = mock_result_image
            client.mock_local_service.save_image_from_bytes.return_value = mock_result_url
            
            with patch('main.os.path.exists', return_value=True):
                with patch('main.Image.open') as mock_image_open:
                    mock_image_open.return_value = Mock(spec=Image.Image)
                    
                    # Create test files and data
                    person_file = ("person.jpg", b"fake person image", "image/jpeg")
                    
                    # Make request
                    response = client.post(
                        "/api/v1/try-on",
                        files={"person_image": person_file},
                        data={
                            "cloth_url": "http://testserver/static/clothes/item.jpg",
                            "category": category
                        }
                    )
                    
                    # Verify response
                    assert response.status_code == 200
                    
                    # The virtual_try_on should be called with the category
                    # (Note: actual mapping happens inside virtual_try_on method)
                    client.mock_ai_engine.virtual_try_on.assert_called_once()