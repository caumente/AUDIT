import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))
import os
from pathlib import Path
from unittest.mock import patch

import pytest

from src.audit.utils.commons.file_manager import add_string_dirs
from src.audit.utils.commons.file_manager import add_string_files
from src.audit.utils.commons.file_manager import copy_files_by_extension
from src.audit.utils.commons.file_manager import create_project_structure
from src.audit.utils.commons.file_manager import delete_dirs_by_pattern
from src.audit.utils.commons.file_manager import delete_files_by_extension
from src.audit.utils.commons.file_manager import list_dirs
from src.audit.utils.commons.file_manager import list_files
from src.audit.utils.commons.file_manager import move_files_to_parent
from src.audit.utils.commons.file_manager import organize_files_into_dirs
from src.audit.utils.commons.file_manager import organize_subdirs_into_named_dirs
from src.audit.utils.commons.file_manager import rename_dirs
from src.audit.utils.commons.file_manager import rename_files


@pytest.fixture
def sample_structure(tmp_path):
    """
    Create a sample directory structure for testing.
    """
    # Directories
    dirs = ["dir1", "dir2/subdir1", "dir3"]
    for d in dirs:
        (tmp_path / d).mkdir(parents=True)

    # Files
    files = ["file1.txt", "file2.csv", "dir2/subdir1/file3.txt"]
    for f in files:
        f_path = tmp_path / f
        f_path.parent.mkdir(parents=True, exist_ok=True)
        f_path.write_text("sample content")

    return tmp_path


def test_create_project_structure_basic(tmp_path):
    base = tmp_path / "my_project"
    create_project_structure(base)

    expected_subfolders = ["datasets", "configs", "outputs", "logs"]
    for folder in expected_subfolders:
        folder_path = base / folder
        assert folder_path.exists() and folder_path.is_dir()


def test_create_project_structure_existing_dir(tmp_path):
    base = tmp_path / "existing"
    base.mkdir()
    create_project_structure(base)

    expected_subfolders = ["datasets", "configs", "outputs", "logs"]
    for folder in expected_subfolders:
        folder_path = base / folder
        assert folder_path.exists() and folder_path.is_dir()


def test_create_project_structure_base_is_file(tmp_path):
    base = tmp_path / "file.txt"
    base.write_text("I am a file")
    with pytest.raises(NotADirectoryError):
        create_project_structure(base)


def test_list_dirs_basic(tmp_path):
    # Create some subdirectories
    dirs = ["dir1", "dir2", "dir3"]
    for d in dirs:
        (tmp_path / d).mkdir()
    # Also create a file to ensure it’s ignored
    (tmp_path / "file.txt").write_text("content")

    result = list_dirs(tmp_path)
    assert result == sorted(dirs)  # Should return only directories


def test_list_dirs_recursive(tmp_path):
    # Nested directories
    (tmp_path / "dir1").mkdir()
    (tmp_path / "dir1" / "sub1").mkdir(parents=True)
    (tmp_path / "dir2").mkdir()

    result = list_dirs(tmp_path, recursive=True)
    expected = ["dir1", "dir2", "sub1"]
    assert sorted(result) == sorted(expected)


def test_list_dirs_full_path(tmp_path):
    dirs = ["a", "b"]
    for d in dirs:
        (tmp_path / d).mkdir()

    result = list_dirs(tmp_path, full_path=True)
    resolved = [str((tmp_path / d).resolve()) for d in dirs]
    assert sorted(result) == sorted(resolved)


def test_list_dirs_with_pattern(tmp_path):
    dirs = ["apple", "banana", "apricot", "berry"]
    for d in dirs:
        (tmp_path / d).mkdir()

    # Filter directories containing 'ap'
    result = list_dirs(tmp_path, pattern="ap")
    assert sorted(result) == sorted(["apple", "apricot"])


def test_list_dirs_path_not_exist(tmp_path):
    non_existent = tmp_path / "nope"
    with pytest.raises(FileNotFoundError):
        list_dirs(non_existent)


def test_list_dirs_path_is_file(tmp_path):
    f = tmp_path / "file.txt"
    f.write_text("test")
    with pytest.raises(NotADirectoryError):
        list_dirs(f)


def test_list_dirs_permission_denied(tmp_path, monkeypatch):
    # Create a directory
    d = tmp_path / "dir1"
    d.mkdir()
    # Patch os.access to simulate permission denied
    monkeypatch.setattr(os, "access", lambda path, mode: False)
    with pytest.raises(PermissionError):
        list_dirs(tmp_path)


def test_list_dirs_recursive_and_pattern(tmp_path):
    (tmp_path / "dir1").mkdir()
    (tmp_path / "dir1" / "sub1").mkdir(parents=True)
    (tmp_path / "dir1" / "sub2").mkdir(parents=True)
    (tmp_path / "dir2").mkdir()

    result = list_dirs(tmp_path, recursive=True, pattern="sub2")
    assert result == ["sub2"]


def test_list_files_basic(tmp_path):
    # Create files and directories
    (tmp_path / "file1.txt").write_text("a")
    (tmp_path / "file2.txt").write_text("b")
    (tmp_path / "dir").mkdir()
    (tmp_path / "dir" / "nested.txt").write_text("c")

    result = list_files(tmp_path)
    # Only top-level files
    assert sorted(result) == ["file1.txt", "file2.txt"]


def test_list_files_recursive(tmp_path):
    (tmp_path / "file1.txt").write_text("a")
    (tmp_path / "dir").mkdir()
    (tmp_path / "dir" / "nested.txt").write_text("b")

    result = list_files(tmp_path, recursive=True)
    assert sorted(result) == ["file1.txt", "nested.txt"]


def test_list_files_full_path(tmp_path):
    f1 = tmp_path / "file1.txt"
    f1.write_text("data")
    f2 = tmp_path / "file2.txt"
    f2.write_text("data")

    result = list_files(tmp_path, full_path=True)
    expected = [str(f1.resolve()), str(f2.resolve())]
    assert sorted(result) == sorted(expected)


def test_list_files_with_pattern(tmp_path):
    (tmp_path / "apple.txt").write_text("a")
    (tmp_path / "banana.txt").write_text("b")
    (tmp_path / "apricot.txt").write_text("c")

    result = list_files(tmp_path, pattern="ap")
    assert sorted(result) == ["apple.txt", "apricot.txt"]


def test_list_files_with_extensions(tmp_path):
    (tmp_path / "a.txt").write_text("1")
    (tmp_path / "b.csv").write_text("2")
    (tmp_path / "c.TXT").write_text("3")

    result = list_files(tmp_path, extensions=[".txt"])
    assert sorted(result) == ["a.txt", "c.TXT"]  # Case-insensitive


def test_list_files_recursive_and_pattern(tmp_path):
    (tmp_path / "dir1").mkdir()
    (tmp_path / "dir1" / "file1.txt").write_text("a")
    (tmp_path / "dir1" / "file2.csv").write_text("b")

    result = list_files(tmp_path, recursive=True, pattern="file1")
    assert result == ["file1.txt"]


def test_list_files_recursive_and_extensions(tmp_path):
    (tmp_path / "dir1").mkdir()
    (tmp_path / "dir1" / "file1.txt").write_text("a")
    (tmp_path / "dir1" / "file2.csv").write_text("b")

    result = list_files(tmp_path, recursive=True, extensions=[".csv"])
    assert result == ["file2.csv"]


def test_list_files_path_not_exist(tmp_path):
    non_existent = tmp_path / "nope"
    with pytest.raises(FileNotFoundError):
        list_files(non_existent)


def test_list_files_path_is_file(tmp_path):
    f = tmp_path / "file.txt"
    f.write_text("test")
    with pytest.raises(NotADirectoryError):
        list_files(f)


def test_list_files_permission_denied(tmp_path, monkeypatch):
    d = tmp_path / "dir"
    d.mkdir()
    monkeypatch.setattr(os, "access", lambda path, mode: False)
    with pytest.raises(PermissionError):
        list_files(tmp_path)


def test_rename_dirs_basic(tmp_path):
    # Setup directories
    old_dir = tmp_path / "to_rename_folder"
    old_dir.mkdir()
    keep_dir = tmp_path / "keep_folder"
    keep_dir.mkdir()

    # Rename 'old' to 'new'
    rename_dirs(tmp_path, old_name="to_rename", new_name="renamed", safe_mode=False)

    # Verify renaming
    renamed_dirs = [d.name for d in tmp_path.iterdir() if d.is_dir()]
    assert "renamed_folder" in renamed_dirs
    assert "keep_folder" in renamed_dirs


def test_rename_dirs_nested(tmp_path):
    parent = tmp_path / "parent_old"
    child = parent / "child_old"
    child.mkdir(parents=True)

    rename_dirs(tmp_path, old_name="_old", new_name="_new", safe_mode=False)

    assert (tmp_path / "parent_new").exists()
    assert (tmp_path / "parent_new" / "child_new").exists()
    assert not (tmp_path / "parent_old").exists()


def test_rename_dirs_safe_mode(capsys, tmp_path):
    d = tmp_path / "folder_old"
    d.mkdir()

    rename_dirs(tmp_path, old_name="old", new_name="new", safe_mode=True)

    captured = capsys.readouterr()
    assert "[SAFE MODE]" in captured.out
    # Folder should not be actually renamed
    assert (tmp_path / "folder_old").exists()
    assert not (tmp_path / "folder_new").exists()


def test_rename_dirs_verbose_output(capsys, tmp_path):
    d = tmp_path / "folder_old"
    d.mkdir()

    rename_dirs(tmp_path, old_name="old", new_name="new", verbose=True, safe_mode=True)
    captured = capsys.readouterr()
    assert "Would rename" in captured.out


def test_rename_dirs_root_not_exist(tmp_path):
    with pytest.raises(FileNotFoundError):
        rename_dirs(tmp_path / "nonexistent", old_name="a", new_name="b")


def test_rename_dirs_root_is_file(tmp_path):
    f = tmp_path / "file.txt"
    f.write_text("data")
    with pytest.raises(NotADirectoryError):
        rename_dirs(f, old_name="a", new_name="b")


def test_rename_files_safe_mode(tmp_path, capsys):
    # Create files
    f1 = tmp_path / "file_old.txt"
    f1.write_text("content1")
    f2 = tmp_path / "file_keep.txt"
    f2.write_text("content2")

    # Safe mode
    rename_files(tmp_path, old_name="old", new_name="new", safe_mode=True)

    captured = capsys.readouterr()
    assert "[SAFE MODE] Would rename:" in captured.out

    # Files should not be renamed
    assert (tmp_path / "file_old.txt").exists()
    assert (tmp_path / "file_keep.txt").exists()


def test_rename_files_actual(tmp_path):
    # Create files
    f1 = tmp_path / "file_old.txt"
    f1.write_text("content1")
    f2 = tmp_path / "file_keep.txt"
    f2.write_text("content2")

    # Rename files
    rename_files(tmp_path, old_name="old", new_name="new", safe_mode=False)

    # Check renaming
    assert (tmp_path / "file_new.txt").exists()
    assert (tmp_path / "file_keep.txt").exists()
    # Old file no longer exists
    assert not (tmp_path / "file_old.txt").exists()


def test_rename_files_nested(tmp_path):
    # Create nested structure
    sub = tmp_path / "subdir"
    sub.mkdir()
    f = sub / "nested_old.txt"
    f.write_text("data")

    rename_files(tmp_path, old_name="old", new_name="new", safe_mode=False)
    assert (sub / "nested_new.txt").exists()
    assert not (sub / "nested_old.txt").exists()


def test_rename_files_no_match(tmp_path, capsys):
    f = tmp_path / "file.txt"
    f.write_text("data")

    rename_files(tmp_path, old_name="nomatch", new_name="replace", safe_mode=True)
    captured = capsys.readouterr()
    # No rename should be printed
    assert "[SAFE MODE] Would rename:" not in captured.out
    # Original file still exists
    assert (tmp_path / "file.txt").exists()


def test_rename_files_empty_old_name(tmp_path):
    # When old_name="" it should append new_name to all files
    f = tmp_path / "file.txt"
    f.write_text("data")

    with pytest.raises(ValueError):
        rename_files(tmp_path, old_name="", new_name="_new", safe_mode=False)


def test_rename_files_invalid_root(tmp_path):
    # Non-existent path
    with pytest.raises(FileNotFoundError):
        rename_files(tmp_path / "nonexistent", old_name="a", new_name="b")


def test_rename_files_not_a_directory(tmp_path):
    # Pass a file instead of directory
    f = tmp_path / "file.txt"
    f.write_text("data")
    with pytest.raises(NotADirectoryError):
        rename_files(f, old_name="a", new_name="b")


def test_add_string_dirs_basic(tmp_path):
    # Setup directories
    d1 = tmp_path / "folder1"
    d1.mkdir()
    d2 = tmp_path / "folder2"
    d2.mkdir()

    # Add prefix and suffix
    add_string_dirs(tmp_path, prefix="pre_", suffix="_suf", safe_mode=False)

    renamed_dirs = [d.name for d in tmp_path.iterdir() if d.is_dir()]
    assert "pre_folder1_suf" in renamed_dirs
    assert "pre_folder2_suf" in renamed_dirs


def test_add_string_dirs_safe_mode(tmp_path, capsys):
    d1 = tmp_path / "folder1"
    d1.mkdir()

    add_string_dirs(tmp_path, prefix="pre_", safe_mode=True)
    captured = capsys.readouterr()
    assert "[SAFE MODE] Would rename" in captured.out

    # Ensure original folder still exists
    assert (tmp_path / "folder1").exists()


def test_add_string_dirs_verbose(tmp_path, capsys):
    d1 = tmp_path / "folder1"
    d1.mkdir()

    add_string_dirs(tmp_path, suffix="_suf", safe_mode=False, verbose=True)
    captured = capsys.readouterr()
    assert "Renamed:" in captured.out
    assert (tmp_path / "folder1_suf").exists()


def test_add_string_dirs_nested(tmp_path):
    parent = tmp_path / "parent"
    parent.mkdir()
    child = parent / "child"
    child.mkdir()

    add_string_dirs(tmp_path, prefix="X_", safe_mode=False)

    renamed_dirs = [d.name for d in tmp_path.iterdir()]
    assert "X_parent" in renamed_dirs
    renamed_child = list((tmp_path / "X_parent").iterdir())[0].name
    assert renamed_child == "X_child"


def test_add_string_dirs_invalid_path(tmp_path):
    invalid_path = tmp_path / "nonexistent"

    with pytest.raises(FileNotFoundError):
        add_string_dirs(invalid_path)


def test_add_string_dirs_not_directory(tmp_path):
    f = tmp_path / "file.txt"
    f.write_text("data")

    with pytest.raises(NotADirectoryError):
        add_string_dirs(f)


def test_add_string_files_basic(tmp_path):
    f1 = tmp_path / "file1.txt"
    f1.write_text("data")
    f2 = tmp_path / "file2.txt"
    f2.write_text("data")

    add_string_files(tmp_path, prefix="pre_", suffix="_suf", safe_mode=False)

    renamed_files = [f.name for f in tmp_path.iterdir() if f.is_file()]
    assert "pre_file1_suf.txt" in renamed_files
    assert "pre_file2_suf.txt" in renamed_files


def test_add_string_files_safe_mode(tmp_path, capsys):
    f = tmp_path / "file.txt"
    f.write_text("data")

    add_string_files(tmp_path, prefix="X_", safe_mode=True)
    captured = capsys.readouterr()
    assert "[SAFE MODE] Would rename" in captured.out
    # Original file should still exist
    assert (tmp_path / "file.txt").exists()


def test_add_string_files_verbose(tmp_path, capsys):
    f = tmp_path / "file.txt"
    f.write_text("data")

    add_string_files(tmp_path, suffix="_end", safe_mode=False, verbose=True)
    captured = capsys.readouterr()
    assert "Renamed:" in captured.out
    assert (tmp_path / "file_end.txt").exists()


def test_add_string_files_nested(tmp_path):
    folder = tmp_path / "folder"
    folder.mkdir()
    f = folder / "file.txt"
    f.write_text("data")

    add_string_files(tmp_path, prefix="X_", safe_mode=False)

    renamed_file = list((tmp_path / "folder").iterdir())[0].name
    assert renamed_file == "X_file.txt"


def test_add_string_files_with_ext(tmp_path):
    f1 = tmp_path / "file1.nii.gz"
    f1.write_text("data")
    f2 = tmp_path / "file2.txt"
    f2.write_text("data")

    # Only rename .nii.gz
    add_string_files(tmp_path, suffix="_new", ext=".nii.gz", safe_mode=False)

    assert (tmp_path / "file1_new.nii.gz").exists()
    assert (tmp_path / "file2.txt").exists()  # untouched


def test_add_string_files_invalid_path(tmp_path):
    invalid = tmp_path / "nonexistent"
    with pytest.raises(FileNotFoundError):
        add_string_files(invalid)


def test_add_string_files_not_directory(tmp_path):
    f = tmp_path / "file.txt"
    f.write_text("data")
    with pytest.raises(NotADirectoryError):
        add_string_files(f)


def test_add_string_files_file_exists(tmp_path):
    f = tmp_path / "file.txt"
    f.write_text("data")
    f_new = tmp_path / "pre_file.txt"
    f_new.write_text("other")

    with pytest.raises(FileExistsError):
        add_string_files(tmp_path, prefix="pre_", safe_mode=False)


def test_copy_files_basic(tmp_path):
    src = tmp_path / "src"
    dst = tmp_path / "dst"
    src.mkdir()
    dst.mkdir()
    # Create files
    (src / "a.txt").write_text("A")
    (src / "b.txt").write_text("B")
    (src / "c.md").write_text("C")

    copy_files_by_extension(src, dst, ".txt", safe_mode=False)

    copied = list(dst.iterdir())
    copied_names = sorted([f.name for f in copied])
    assert copied_names == ["a.txt", "b.txt"]


def test_copy_files_safe_mode(tmp_path, capsys):
    src = tmp_path / "src"
    dst = tmp_path / "dst"
    src.mkdir()
    dst.mkdir()
    (src / "a.txt").write_text("A")

    copy_files_by_extension(src, dst, ".txt", safe_mode=True)
    captured = capsys.readouterr()
    assert "[SAFE MODE] Would copy" in captured.out
    # Destination folder should still be empty
    assert not list(dst.iterdir())


def test_copy_files_overwrite(tmp_path):
    src = tmp_path / "src"
    dst = tmp_path / "dst"
    src.mkdir()
    dst.mkdir()
    # Existing file in destination
    (dst / "a.txt").write_text("OLD")
    (src / "a.txt").write_text("NEW")

    # Without overwrite, file should not change
    copy_files_by_extension(src, dst, ".txt", safe_mode=False, overwrite=False)
    assert (dst / "a.txt").read_text() == "OLD"

    # With overwrite, file should be replaced
    copy_files_by_extension(src, dst, ".txt", safe_mode=False, overwrite=True)
    assert (dst / "a.txt").read_text() == "NEW"


def test_copy_files_no_matching_files(tmp_path, capsys):
    src = tmp_path / "src"
    dst = tmp_path / "dst"
    src.mkdir()
    dst.mkdir()
    (src / "file.md").write_text("Hello")

    copy_files_by_extension(src, dst, ".txt", safe_mode=False, verbose=True)
    captured = capsys.readouterr()
    assert "No files with the extension '.txt' were found" in captured.out
    assert list(dst.iterdir()) == []


def test_copy_files_recursive(tmp_path):
    src = tmp_path / "src"
    dst = tmp_path / "dst"
    sub = src / "subfolder"
    sub.mkdir(parents=True)
    dst.mkdir()
    (sub / "a.txt").write_text("A")

    copy_files_by_extension(src, dst, ".txt", safe_mode=False)
    assert (dst / "a.txt").exists()


import os
import shutil
from pathlib import Path

import pytest

from src.audit.utils.commons.file_manager import move_files_to_parent


def test_move_files_basic(tmp_path):
    sub = tmp_path / "subdir"
    sub.mkdir()
    f = sub / "file.txt"
    f.write_text("data")

    move_files_to_parent(tmp_path, levels_up=1, safe_mode=False)

    # File should be moved to tmp_path
    assert (tmp_path / "file.txt").exists()
    assert not f.exists()


def test_move_files_safe_mode(tmp_path, capsys):
    sub = tmp_path / "subdir"
    sub.mkdir()
    f = sub / "file.txt"
    f.write_text("data")

    move_files_to_parent(tmp_path, levels_up=1, safe_mode=True)

    captured = capsys.readouterr()
    assert "[SAFE MODE] Would move:" in captured.out
    # Original file should still exist
    assert f.exists()


def test_move_files_with_extension(tmp_path):
    sub = tmp_path / "subdir"
    sub.mkdir()
    (sub / "keep.md").write_text("keep")
    (sub / "move.txt").write_text("move")

    move_files_to_parent(tmp_path, levels_up=1, ext=".txt", safe_mode=False)

    assert (tmp_path / "move.txt").exists()
    assert not (sub / "move.txt").exists()
    # Non-matching extension should remain
    assert (sub / "keep.md").exists()


def test_move_files_levels_up(tmp_path):
    level1 = tmp_path / "level1"
    level2 = level1 / "level2"
    level2.mkdir(parents=True)
    f = level2 / "file.txt"
    f.write_text("data")

    move_files_to_parent(tmp_path, levels_up=2, safe_mode=False)

    # File should move up two levels to tmp_path
    assert (tmp_path / "file.txt").exists()
    assert not f.exists()


def test_move_files_invalid_root(tmp_path):
    with pytest.raises(FileNotFoundError):
        move_files_to_parent(tmp_path / "nonexistent", safe_mode=False)


def test_move_files_invalid_levels(tmp_path):
    sub = tmp_path / "subdir"
    sub.mkdir()
    (sub / "file.txt").write_text("data")

    with pytest.raises(ValueError):
        move_files_to_parent(tmp_path, levels_up=0, safe_mode=False)


def test_move_files_no_files(tmp_path, capsys):
    move_files_to_parent(tmp_path, safe_mode=True, verbose=True)
    captured = capsys.readouterr()
    assert "Safe mode enabled" in captured.out
