import pytest
from datetime import datetime
import sys
import os

# Add src/ and src/models to path for imports
dir_path = os.path.dirname(os.path.realpath(__file__))
src_path = os.path.abspath(os.path.join(dir_path, '../src'))
sys.path.insert(0, src_path)

from models.database import (
    generate_accession_number, validate_accession_number, parse_accession_number
)


def test_generate_accession_number():
    # Test known values - 2-letter species code (14 chars)
    acc = generate_accession_number('MM', 2025, 1)
    assert acc.startswith('MM2025000001')
    assert len(acc) == 14
    assert validate_accession_number(acc)
    parsed = parse_accession_number(acc)
    assert parsed['species_code'] == 'MM'
    assert parsed['year'] == 2025
    assert parsed['sequence'] == 1
    assert len(parsed['checksum']) == 2

    # Test 2-letter species code (14 chars)
    acc2 = generate_accession_number('RN', 2025, 42)
    assert acc2.startswith('RN2025000042')
    assert len(acc2) == 14
    assert validate_accession_number(acc2)
    parsed2 = parse_accession_number(acc2)
    assert parsed2['species_code'] == 'RN'
    assert parsed2['year'] == 2025
    assert parsed2['sequence'] == 42

    # Test 3-letter species code (15 chars)
    acc3 = generate_accession_number('MAC', 2025, 123)
    assert acc3.startswith('MAC2025000123')
    assert len(acc3) == 15
    assert validate_accession_number(acc3)
    parsed3 = parse_accession_number(acc3)
    assert parsed3['species_code'] == 'MAC'
    assert parsed3['year'] == 2025
    assert parsed3['sequence'] == 123


def test_invalid_accession_number():
    # Too short
    assert not validate_accession_number('MM20250001A5')
    # Wrong format
    assert not validate_accession_number('MM-001-2024')
    # Bad checksum
    bad = 'MM2025000001FF'
    assert not validate_accession_number(bad)


def test_debug_mac_accession():
    """Debug test to understand MAC accession number validation"""
    acc = generate_accession_number('MAC', 2025, 123)
    print(f"Generated MAC accession: {acc}")
    print(f"Length: {len(acc)}")
    print(f"First 3 chars: {acc[:3]}")
    print(f"Year part: {acc[3:7]}")
    print(f"Sequence part: {acc[7:13]}")
    print(f"Checksum part: {acc[13:]}")
    
    # Test validation step by step
    assert len(acc) == 15
    assert acc[:3].isalpha()  # MAC should be alpha
    assert acc[3:7].isdigit()  # 2025 should be digits
    assert acc[7:13].isdigit()  # 000123 should be digits
    assert len(acc[13:]) == 2  # Checksum should be 2 chars
    
    # Test the full validation
    assert validate_accession_number(acc)


def test_parse_accession_number():
    acc = generate_accession_number('MAC', 2025, 123)
    parsed = parse_accession_number(acc)
    assert parsed['species_code'] == 'MAC'
    assert parsed['year'] == 2025
    assert parsed['sequence'] == 123
    assert len(parsed['checksum']) == 2

    # Should raise on invalid
    with pytest.raises(ValueError):
        parse_accession_number('MM-001-2024')


def test_sequential_generation():
    # Simulate generating a sequence
    year = 2025
    for seq in range(1, 10):
        acc = generate_accession_number('MM', year, seq)
        assert validate_accession_number(acc)
        parsed = parse_accession_number(acc)
        assert parsed['sequence'] == seq 