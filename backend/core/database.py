from neo4j import GraphDatabase
from core.config import settings
import logging

logger = logging.getLogger(__name__)

class Neo4jDB:
    def __init__(self):
        self._driver = None

    def connect(self):
        try:
            self._driver = GraphDatabase.driver(
                settings.neo4j_uri,
                auth=(settings.neo4j_username, settings.neo4j_password)
            )
            self._driver.verify_connectivity()
            logger.info("✅ Connected to Neo4j")
        except Exception as e:
            logger.error(f"❌ Neo4j connection failed: {e}")
            raise

    def close(self):
        if self._driver:
            self._driver.close()

    def run(self, query: str, **params):
        """Run a Cypher query and return all records as dicts."""
        with self._driver.session() as session:
            result = session.run(query, **params)
            return [dict(record) for record in result]

    def run_one(self, query: str, **params):
        """Run a query and return the first record, or None."""
        results = self.run(query, **params)
        return results[0] if results else None

    def run_write(self, query: str, **params):
        """Run a write query inside an explicit write transaction."""
        with self._driver.session() as session:
            result = session.execute_write(
                lambda tx: list(tx.run(query, **params))
            )
            return [dict(r) for r in result]

# Singleton instance used across the app
db = Neo4jDB()
