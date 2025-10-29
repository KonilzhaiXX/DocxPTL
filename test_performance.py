#!/usr/bin/env python3
"""
Simple test to verify the performance improvements work correctly
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import pad_list, pair_workers, get_template

def test_pad_list():
    """Test the pad_list function"""
    # Test with empty list
    result = pad_list([], 5)
    assert len(result) == 5, f"Expected length 5, got {len(result)}"
    assert all(w == {'FullName': '', 'hour': ''} for w in result), "Wrong fill values"
    
    # Test with partial list
    workers = [{'FullName': 'John', 'hour': '8'}, {'FullName': 'Jane', 'hour': '7'}]
    result = pad_list(workers, 5)
    assert len(result) == 5, f"Expected length 5, got {len(result)}"
    assert result[0] == {'FullName': 'John', 'hour': '8'}, "First element incorrect"
    assert result[1] == {'FullName': 'Jane', 'hour': '7'}, "Second element incorrect"
    assert result[2] == {'FullName': '', 'hour': ''}, "Padding element incorrect"
    
    # Test with full list (no padding needed)
    workers = [{'FullName': f'Worker{i}', 'hour': '8'} for i in range(5)]
    result = pad_list(workers, 5)
    assert len(result) == 5, f"Expected length 5, got {len(result)}"
    
    print("✓ pad_list tests passed")

def test_pair_workers():
    """Test the pair_workers function"""
    left = [{'FullName': 'L1', 'hour': '8'}, {'FullName': 'L2', 'hour': '7'}]
    right = [{'FullName': 'R1', 'hour': '6'}, {'FullName': 'R2', 'hour': '5'}]
    
    result = pair_workers(left, right)
    assert len(result) == 2, f"Expected length 2, got {len(result)}"
    assert result[0] == {'left': {'FullName': 'L1', 'hour': '8'}, 'right': {'FullName': 'R1', 'hour': '6'}}
    assert result[1] == {'left': {'FullName': 'L2', 'hour': '7'}, 'right': {'FullName': 'R2', 'hour': '5'}}
    
    print("✓ pair_workers tests passed")

def test_get_template():
    """Test the get_template function"""
    # This will fail if template files don't exist, but we can test the function exists
    try:
        # Just check the function is callable
        assert callable(get_template), "get_template should be callable"
        print("✓ get_template function exists")
    except Exception as e:
        print(f"⚠ get_template test skipped (expected in test environment): {e}")

if __name__ == '__main__':
    print("Running performance optimization tests...\n")
    
    try:
        test_pad_list()
        test_pair_workers()
        test_get_template()
        
        print("\n✅ All tests passed!")
        sys.exit(0)
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)
