import argparse

from Docs2KG.rag.neo4j_vector import Neo4jVector

if __name__ == "__main__":
    args = argparse.ArgumentParser()
    args.add_argument("--neo4j_uri", type=str, default="bolt://localhost:7687")
    args.add_argument("--neo4j_username", type=str, default="neo4j")
    args.add_argument("--neo4j_password", type=str, default="testpassword")

    args = args.parse_args()

    neo4j_vector = Neo4jVector(
        uri=args.neo4j_uri, user=args.neo4j_username, password=args.neo4j_password
    )
    neo4j_vector.add_embedding()
    neo4j_vector.close()
