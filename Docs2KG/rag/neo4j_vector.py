import json

from neo4j import GraphDatabase
from tqdm import tqdm

from Docs2KG.modules.llm.openai_embedding import get_openai_embedding
from Docs2KG.utils.get_logger import get_logger

logger = get_logger(__name__)


class Neo4jVector:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def add_embedding(self):
        """
        Loop the whole graph
        For all nodes without embedding field, get the nodes out, and grab the embedding.

        Returns:

        """
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (n)
                WHERE n.content_embedding IS NULL
                RETURN n
                """
            )
            records = list(result)
            total_records = len(records)
            with tqdm(total=total_records, desc="Adding embedding") as pbar:
                for record in records:
                    node = record["n"]
                    logger.debug(node)
                    node_properties = dict(node.items())
                    logger.debug(node_properties)
                    content_embedding = get_openai_embedding(
                        node_properties.get("content", "")
                    )
                    meta_embedding = get_openai_embedding(json.dumps(node_properties))
                    logger.debug(content_embedding)
                    logger.debug(meta_embedding)
                    session.run(
                        """
                        MATCH (n)
                        WHERE id(n) = $id
                        SET n.content_embedding = $content_embedding
                        SET n.meta_embedding = $meta_embedding
                        """,
                        id=node.id,
                        content_embedding=content_embedding,
                        meta_embedding=meta_embedding,
                    )
                    pbar.update(1)
