from server import database
import logging


def test_init_db(caplog, weaviate_client):
    """
    Test the database initialization
    """
    with caplog.at_level(logging.DEBUG):
        database.init_db()
        assert "Creating schema" in caplog.text

    caplog.clear()

    with caplog.at_level(logging.DEBUG):
        database.init_db()
        assert "Skipping schema creation" in caplog.text
