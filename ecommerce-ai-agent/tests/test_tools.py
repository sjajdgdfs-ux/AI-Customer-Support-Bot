"""
Tests for AI Agent Tools
"""
import json
import pytest
from app.agent import search_products_fast, extract_text


class TestRealTools:

    @pytest.mark.unit
    def test_search_products_returns_valid_json(self):
        result = search_products_fast("headphones")
        assert isinstance(result, str)
        parsed = json.loads(result)
        assert isinstance(parsed, list)

    @pytest.mark.unit
    def test_extract_text_helper(self):
        assert extract_text("test") == "test"
        assert extract_text([{"text": "a"}, {"text": "b"}]) == "a b"