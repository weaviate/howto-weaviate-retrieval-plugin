from server.embedding import get_embedding
import pytest


@pytest.mark.expensive
def test_get_embedding():
    """
    Test the get_embedding function
    """
    ADA_002_DIM = 1536
    text = "This is a test"
    results = get_embedding(text)
    assert isinstance(results, list)
    assert len(results) == ADA_002_DIM
