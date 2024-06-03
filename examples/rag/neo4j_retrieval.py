from Docs2KG.rag.neo4j_rag import Neo4jRAG
from Docs2KG.utils.get_logger import get_logger

logger = get_logger(__name__)

if __name__ == "__main__":
    uri = "bolt://localhost:7687"
    username = "neo4j"
    password = "testpassword"

    rag = Neo4jRAG(uri, username, password)
    query = "What is the capital of France?"
    result = rag.retrieval(query)
    logger.info(result)

    rag.retrieval_strategy_hops_away(
        uuids=result["top_k_content"],
        hops=2,
    )
