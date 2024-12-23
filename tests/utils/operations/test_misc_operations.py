import pytest
from src.utils.operations.misc_operations import add_prefix_dict
from src.utils.operations.misc_operations import capitalizer
from src.utils.operations.misc_operations import pretty_string
from src.utils.operations.misc_operations import snake_case


def test_add_prefix_dict():
    # Test with simple dictionary and prefix
    input_dict = {"a": 1, "b": 2, "c": 3}
    prefix = "prefix_"
    result = add_prefix_dict(input_dict, prefix)
    expected = {"prefix_a": 1, "prefix_b": 2, "prefix_c": 3}
    assert result == expected, f"Expected {expected}, but got {result}"

def test_add_prefix_dict_empty():
    # Test with an empty dictionary
    input_dict = {}
    prefix = "prefix_"
    result = add_prefix_dict(input_dict, prefix)
    expected = {}
    assert result == expected, f"Expected {expected}, but got {result}"

def test_add_prefix_dict_no_prefix():
    # Test with a prefix that is an empty string
    input_dict = {"a": 1, "b": 2}
    prefix = ""
    result = add_prefix_dict(input_dict, prefix)
    expected = {"a": 1, "b": 2}
    assert result == expected, f"Expected {expected}, but got {result}"


def test_capitalizer():
    # Test normal string
    text = "hello world"
    result = capitalizer(text)
    expected = "HELLO WORLD"
    assert result == expected, f"Expected {expected}, but got {result}"

def test_capitalizer_empty():
    # Test empty string
    text = ""
    result = capitalizer(text)
    expected = ""
    assert result == expected, f"Expected {expected}, but got {result}"

def test_capitalizer_mixed_case():
    # Test string with mixed case
    text = "HeLLo WoRLd"
    result = capitalizer(text)
    expected = "HELLO WORLD"
    assert result == expected, f"Expected {expected}, but got {result}"

def test_capitalizer_numbers_and_special_chars():
    # Test string with numbers and special characters
    text = "123_hello@world"
    result = capitalizer(text)
    expected = "123_HELLO@WORLD"
    assert result == expected, f"Expected {expected}, but got {result}"


def test_pretty_string():
    # Test normal string with underscores
    text = "hello_world_test"
    result = pretty_string(text)
    expected = "Hello World Test"
    assert result == expected, f"Expected {expected}, but got {result}"

def test_pretty_string_empty():
    # Test empty string
    text = ""
    result = pretty_string(text)
    expected = ""
    assert result == expected, f"Expected {expected}, but got {result}"

def test_pretty_string_with_custom_delimiter():
    # Test with a custom delimiter
    text = "hello-world-test"
    result = pretty_string(text, splitting_pattern="-")
    expected = "Hello World Test"
    assert result == expected, f"Expected {expected}, but got {result}"

def test_pretty_string_single_word():
    # Test with a single word
    text = "hello"
    result = pretty_string(text)
    expected = "Hello"
    assert result == expected, f"Expected {expected}, but got {result}"


def test_snake_case():
    # Test normal string with spaces
    text = "Hello World Test"
    result = snake_case(text)
    expected = "hello_world_test"
    assert result == expected, f"Expected {expected}, but got {result}"

def test_snake_case_empty():
    # Test empty string
    text = ""
    result = snake_case(text)
    expected = ""
    assert result == expected, f"Expected {expected}, but got {result}"

def test_snake_case_with_custom_delimiter():
    # Test with a custom delimiter
    text = "hello-world-test"
    result = snake_case(text, splitting_pattern="-")
    expected = "hello_world_test"
    assert result == expected, f"Expected {expected}, but got {result}"

def test_snake_case_single_word():
    # Test with a single word
    text = "hello"
    result = snake_case(text)
    expected = "hello"
    assert result == expected, f"Expected {expected}, but got {result}"

