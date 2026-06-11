"""Tests for src/validation — shared validation utilities."""
import pytest
from src.validation import SUFFIX_RE


@pytest.mark.parametrize("valid", ["q4", "Q4_Report", "my-suffix", "abc123", "a_b-c"])
def test_suffix_re_accepts_valid_values(valid):
    assert SUFFIX_RE.match(valid)


@pytest.mark.parametrize("invalid", ["", "has space", "slash/bad", "dot.bad", "bang!"])
def test_suffix_re_rejects_invalid_values(invalid):
    assert not SUFFIX_RE.match(invalid)
