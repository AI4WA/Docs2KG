import argparse

from Docs2KG.rag.neo4j_rag import Neo4jRAG
from Docs2KG.utils.get_logger import get_logger

logger = get_logger(__name__)

if __name__ == "__main__":
    args = argparse.ArgumentParser()
    args.add_argument("--neo4j_uri", type=str, default="bolt://localhost:7687")
    args.add_argument("--neo4j_username", type=str, default="neo4j")
    args.add_argument("--neo4j_password", type=str, default="testpassword")
    args.add_argument("--query", type=str, default=None)

    args = args.parse_args()

    rag = Neo4jRAG(
        uri=args.neo4j_uri, user=args.neo4j_username, password=args.neo4j_password
    )
    """
    Here we are using the retrieval method to get the top k content based on the query
    We can have multiple strategies to get the top k content
    """
    result = rag.retrieval(query=args.query)
    logger.info(result)

    rag.retrieval_strategy_hops_away(
        uuids=result["top_k_content"],
        hops=3,
    )
