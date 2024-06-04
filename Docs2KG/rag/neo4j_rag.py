from typing import List

import numpy as np
import pandas as pd
from neo4j import GraphDatabase
from tqdm import tqdm

from Docs2KG.modules.llm.openai_embedding import get_openai_embedding
from Docs2KG.utils.get_logger import get_logger

logger = get_logger(__name__)


class Neo4jRAG:
    def __init__(self, uri: str, user: str, password: str):
        """

        Args:
            uri (str): uri of the graph database
            user (str): username of the graph database
            password (str): password of the graph database
        """
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def retrieval(self, query: str, top_k: int = 10) -> dict:
        """
        Retrieve the best matching node from the graph based on the query

        We choose to use our way to do the similarity calculation, which will be slow

        However, it is just a demonstration about how should you do it.
        Args:
            query (str): query string
            top_k (int): number of results to return

        Returns:

        """
        query_embedding = get_openai_embedding(query)
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (n)
                RETURN n
                """
            )
            nodes = []

            for record in result:
                node = record["n"]
                logger.debug(node)
                node_properties = dict(node.items())

                logger.debug(node_properties)
                nodes.append(node_properties)

        df = pd.DataFrame(nodes)

        # calculate the similarity
        # using tqdm to show the progress bar
        tqdm.pandas()
        logger.info("Calculating the Content similarity")
        df["content_similarity"] = df["content_embedding"].progress_apply(
            lambda x: self.cosine_similarity(x, query_embedding)
        )
        logger.info("Calculating the meta similarity")
        df["meta_similarity"] = df["meta_embedding"].progress_apply(
            lambda x: self.cosine_similarity(x, query_embedding)
        )

        # get top k content similarity
        top_k_content = df.sort_values("content_similarity", ascending=False).head(
            top_k
        )
        # log the content value
        top_k_meta = df.sort_values("meta_similarity", ascending=False).head(top_k)
        return {
            "top_k_content": top_k_content["uuid"].tolist(),
            "top_k_meta": top_k_meta["uuid"].tolist(),
        }

    @staticmethod
    def cosine_similarity(embedding1, embedding2):
        """
        Calculate the cosine similarity between two embeddings

        Args:
            embedding1 (list): embedding 1
            embedding2 (list): embedding 2

        Returns:
            float: similarity score
        """
        vec1 = np.array(embedding1)
        vec2 = np.array(embedding2)
        return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

    def retrieval_strategy_hops_away(self, uuids: List[str], hops: int = 1):
        """
        Match all nodes and relationships that are `hops` away from the given uuids

        the node will have a property `uuid`

        Args:
            uuids (List[str]): list of uuids
            hops (int): number of hops away

        Returns:

        """
        """
          Retrieves nodes connected within a given number of hops from nodes with specified UUIDs.

          Args:
              uuids (list): List of UUIDs to query from.
              hops (int): Number of hops to consider in the relationship.

          Returns:
              list: A list of dictionaries where each dictionary contains properties of a node.
          """

        nodes = []

        query = f"""
            MATCH (startNode)-[*1..{hops}]->(endNode)
            WHERE startNode.uuid IN {uuids}
            RETURN endNode
            """
        logger.info(query)
        try:
            with self.driver.session() as session:
                result = session.run(query)
                for record in result:
                    logger.debug(record)
                    node = record["endNode"]
                    node_properties = dict(node.items())
                    logger.info(node_properties.keys())

                    nodes.append(
                        {
                            "uuid": node_properties["uuid"],
                            "content": node_properties.get("content", ""),
                        }
                    )
        except Exception as e:
            logger.error("Failed to fetch connected nodes: %s", e)
            raise
        logger.info(nodes)
        return nodes
