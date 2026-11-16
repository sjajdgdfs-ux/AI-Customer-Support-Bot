"""
Unit Tests for app/rag.py
Tests: Data Existence, Embeddings Model, Knowledge Base Creation, Vector Search
"""
import os
import pytest

from app.rag import (
    ensure_data_exists,
    get_embeddings,
    get_vector_store,
    search_knowledge,
)


class TestRAGCore:

    @pytest.mark.unit
    def test_ensure_data_exists_creates_files(self, tmp_path, monkeypatch):
        data_dir = tmp_path / "data"
        policies_file = data_dir / "policies.md"
        products_file = data_dir / "products.json"

        monkeypatch.setattr("app.rag.DATA_DIR", str(data_dir))
        monkeypatch.setattr("app.rag.DATA_PATH", str(policies_file))
        monkeypatch.setattr("app.rag.PRODUCTS_PATH", str(products_file))

        ensure_data_exists()

        assert os.path.exists(policies_file)
        assert os.path.exists(products_file)

    @pytest.mark.unit
    def test_get_embeddings_cached(self):
        emb1 = get_embeddings()
        emb2 = get_embeddings()
        assert emb1 is emb2  # Verify LRU cache returns exact same instance

    @pytest.mark.unit
    def test_search_knowledge_shipping(self):
        result = search_knowledge("What is the shipping cost?")
        assert isinstance(result, str)
        assert len(result) > 0

    @pytest.mark.unit
    def test_search_knowledge_returns_policy(self):
        result = search_knowledge("returns and warranty policy")
        assert isinstance(result, str)
        assert "Return" in result or "Warranty" in result or "Policy" in result