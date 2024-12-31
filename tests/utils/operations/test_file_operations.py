import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))
from unittest import mock

from src.audit.utils.commons.file_manager import list_dirs
from src.audit.utils.commons.file_manager import list_files


# Sample directories and files structure for testing
def test_ls_dirs_basic():
    # Simulate a directory structure
    with mock.patch("os.scandir") as mock_scandir:
        mock_scandir.return_value = [
            mock.Mock(is_dir=lambda: True, path="/mock/path/dir1"),
            mock.Mock(is_dir=lambda: True, path="/mock/path/dir2"),
            mock.Mock(is_dir=lambda: True, path="/mock/path/dir3"),
            mock.Mock(is_dir=lambda: False, path="/mock/path/file1.txt"),  # Non-directory file
        ]

        path = "/mock/path"
        result = list_dirs(path)

        expected = ["dir1", "dir2", "dir3"]
        assert result == expected, f"Expected {expected}, but got {result}"


def test_ls_dirs_empty_directory():
    # Test with an empty directory (no subdirectories)
    with mock.patch("os.scandir") as mock_scandir:
        mock_scandir.return_value = []

        path = "/mock/path"
        result = list_dirs(path)

        expected = []
        assert result == expected, f"Expected {expected}, but got {result}"


def test_ls_dirs_with_non_directory_files():
    # Test directory with both directories and files (ensure non-directories are excluded)
    with mock.patch("os.scandir") as mock_scandir:
        mock_scandir.return_value = [
            mock.Mock(is_dir=lambda: True, path="/mock/path/dir3"),
            mock.Mock(is_dir=lambda: True, path="/mock/path/dir1"),
            mock.Mock(is_dir=lambda: False, path="/mock/path/file1.txt"),
            mock.Mock(is_dir=lambda: True, path="/mock/path/dir2"),
        ]

        path = "/mock/path"
        result = list_dirs(path)

        expected = ["dir1", "dir2", "dir3"]
        assert result == expected, f"Expected {expected}, but got {result}"


def test_ls_dirs_no_directories():
    # Test with a directory containing no subdirectories, only files
    with mock.patch("os.scandir") as mock_scandir:
        mock_scandir.return_value = [
            mock.Mock(is_dir=lambda: False, path="/mock/path/file1.txt"),
            mock.Mock(is_dir=lambda: False, path="/mock/path/file2.txt"),
        ]

        path = "/mock/path"
        result = list_dirs(path)

        expected = []
        assert result == expected, f"Expected {expected}, but got {result}"


def test_ls_dirs_sorted_order():
    # Test if the directories are returned in sorted order
    with mock.patch("os.scandir") as mock_scandir:
        mock_scandir.return_value = [
            mock.Mock(is_dir=lambda: True, path="/mock/path/dir3"),
            mock.Mock(is_dir=lambda: True, path="/mock/path/dir1"),
            mock.Mock(is_dir=lambda: True, path="/mock/path/dir2"),
        ]

        path = "/mock/path"
        result = list_dirs(path)

        expected = ["dir1", "dir2", "dir3"]
        assert result == expected, f"Expected {expected}, but got {result}"


def test_ls_files_valid_path():
    # Mock the behavior of os.scandir to return files
    mock_files = [
        mock.Mock(path="/mock/path/file1.txt", is_file=mock.Mock(return_value=True)),
        mock.Mock(path="/mock/path/file2.txt", is_file=mock.Mock(return_value=True)),
    ]

    with mock.patch("os.scandir", return_value=mock_files):
        result = list_files("/mock/path")
        assert result == ["file1.txt", "file2.txt"], "Files in the directory do not match the expected list."


def test_ls_files_valid_path_no_files():
    # Mock os.scandir to return an empty directory
    mock_files = []

    with mock.patch("os.scandir", return_value=mock_files):
        result = list_files("/mock/path")
        assert result == [], "Expected an empty list when no files are found."


def test_ls_files_invalid_path_not_exist():
    # Simulate FileNotFoundError when path does not exist
    with mock.patch("os.scandir", side_effect=FileNotFoundError):
        result = list_files("/mock/invalid_path")
        assert result == [], "Expected an empty list when the path does not exist."


def test_ls_files_invalid_path_permission_denied():
    # Simulate PermissionError when permission is denied
    with mock.patch("os.scandir", side_effect=PermissionError):
        result = list_files("/mock/no_permission_path")
        assert result == [], "Expected an empty list when permission is denied."


def test_ls_files_empty_path():
    # Test when the path is an empty string
    with mock.patch("os.scandir", side_effect=FileNotFoundError):
        result = list_files("")
        assert result == [], "Expected an empty list when the path is empty."


def test_ls_files_path_with_mixed_file_types():
    # Mock the behavior of os.scandir with a mix of files and directories
    mock_files = [
        mock.Mock(path="/mock/path/file1.txt", is_file=mock.Mock(return_value=True)),
        mock.Mock(path="/mock/path/file2.txt", is_file=mock.Mock(return_value=True)),
        mock.Mock(path="/mock/path/subdir", is_file=mock.Mock(return_value=False)),
    ]

    with mock.patch("os.scandir", return_value=mock_files):
        result = list_files("/mock/path")
        assert result == ["file1.txt", "file2.txt"], "Only files should be returned, not directories."
