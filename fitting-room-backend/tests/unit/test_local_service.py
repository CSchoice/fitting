import pytest
import os
import shutil
from unittest.mock import Mock, patch, mock_open
from PIL import Image
import io

from app.services.local_service import LocalFileService


class TestLocalFileService:
    """Test suite for LocalFileService class."""
    
    def test_init_creates_directories(self, temp_dir):
        """Test that directories are created on initialization."""
        with patch('app.services.local_service.os.makedirs') as mock_makedirs:
            service = LocalFileService()
            
            # Check that makedirs was called for both directories
            assert mock_makedirs.call_count == 2
            calls = mock_makedirs.call_args_list
            
            # Verify the directory paths
            assert any('static/clothes' in str(call) for call in calls)
            assert any('static/results' in str(call) for call in calls)
            assert all(call[1]['exist_ok'] is True for call in calls)
    
    def test_save_cloth_creates_unique_filename(self, temp_dir):
        """Test that save_cloth creates files with unique names."""
        # Mock dependencies
        mock_file = Mock()
        mock_file.filename = "test.jpg"
        mock_file.file = Mock()
        
        # Mock uuid to return a predictable value
        with patch('app.services.local_service.uuid.uuid4', return_value="test-uuid-123"):
            with patch('app.services.local_service.open', mock_open()) as mock_file_open:
                with patch('app.services.local_service.shutil.copyfileobj') as mock_copy:
                    service = LocalFileService()
                    
                    # Call the method
                    result = service.save_cloth(mock_file)
                    
                    # Verify the result
                    assert result == "/static/clothes/test-uuid-123.jpg"
                    
                    # Verify file was opened with correct path
                    expected_path = os.path.join("static/clothes", "test-uuid-123.jpg")
                    mock_file_open.assert_called_once_with(expected_path, "wb")
                    
                    # Verify copy was called
                    mock_copy.assert_called_once_with(mock_file.file, mock_file_open())
    
    def test_get_cloth_list_returns_sorted_files(self, temp_dir):
        """Test that get_cloth_list returns files sorted by modification time (newest first)."""
        # Mock glob to return test files
        test_files = [
            "static/clothes/file2.jpg",
            "static/clothes/file1.png",
            "static/clothes/file3.jpeg"
        ]
        
        with patch('app.services.local_service.glob') as mock_glob:
            with patch('app.services.local_service.os.path.getmtime') as mock_getmtime:
                # Setup mock returns
                mock_glob.return_value = test_files
                # Files are sorted by mtime in reverse order (newest first)
                # So file3.jpeg (mtime=300) should come first, then file1.png (200), then file2.jpg (100)
                mock_getmtime.side_effect = [100, 200, 300]  # Different mtimes
                
                service = LocalFileService()
                result = service.get_cloth_list()
                
                # Verify glob was called with correct pattern
                mock_glob.assert_called_once_with(os.path.join("static/clothes", "*"))
                
                # Verify result contains web paths sorted by mtime in reverse (newest first)
                # Since file3.jpeg has mtime=300 (newest), it should come first
                expected_paths = [
                    "/static/clothes/file3.jpeg",  # mtime=300 (newest)
                    "/static/clothes/file1.png",    # mtime=200
                    "/static/clothes/file2.jpg"     # mtime=100 (oldest)
                ]
                assert result == expected_paths
    
    def test_save_image_from_bytes_saves_image(self, temp_dir):
        """Test that save_image_from_bytes saves PIL Image correctly."""
        # Create a test image
        test_image = Image.new('RGB', (10, 10), color='red')
        
        # Mock uuid
        with patch('app.services.local_service.uuid.uuid4', return_value="image-uuid-456"):
            with patch('app.services.local_service.os.path.join') as mock_join:
                with patch.object(Image.Image, 'save') as mock_save:
                    mock_join.return_value = "static/results/image-uuid-456.png"
                    
                    service = LocalFileService()
                    result = service.save_image_from_bytes(test_image)
                    
                    # Verify the result
                    assert result == "/static/results/image-uuid-456.png"
                    
                    # Verify image was saved
                    mock_save.assert_called_once_with("static/results/image-uuid-456.png", format="PNG")
    
    def test_get_absolute_path_converts_web_path(self):
        """Test that get_absolute_path converts web path to absolute path."""
        service = LocalFileService()
        
        # Test with leading slash
        with patch('app.services.local_service.os.path.join') as mock_join:
            with patch('app.services.local_service.os.getcwd', return_value="/test/cwd"):
                result = service.get_absolute_path("/static/clothes/test.jpg")
                
                # Verify os.path.join was called with correct arguments
                mock_join.assert_called_once_with("/test/cwd", "static/clothes/test.jpg")
        
        # Test without leading slash
        with patch('app.services.local_service.os.path.join') as mock_join:
            with patch('app.services.local_service.os.getcwd', return_value="/test/cwd"):
                result = service.get_absolute_path("static/clothes/test.jpg")
                
                # Verify os.path.join was called with correct arguments
                mock_join.assert_called_once_with("/test/cwd", "static/clothes/test.jpg")
    
    def test_get_absolute_path_handles_empty_string(self):
        """Test that get_absolute_path handles empty string input."""
        service = LocalFileService()
        
        with patch('app.services.local_service.os.path.join') as mock_join:
            with patch('app.services.local_service.os.getcwd', return_value="/test/cwd"):
                result = service.get_absolute_path("")
                
                # Should join cwd with empty string
                mock_join.assert_called_once_with("/test/cwd", "")