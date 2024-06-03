from Docs2KG.rag.neo4j_vector import Neo4jVector

if __name__ == "__main__":
    uri = "bolt://localhost:7687"
    username = "neo4j"
    password = "testpassword"

    neo4j_vector = Neo4jVector(uri, username, password)
    neo4j_vector.add_embedding()
    neo4j_vector.close()
