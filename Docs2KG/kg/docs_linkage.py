import json
from pathlib import Path
from typing import List

import pandas as pd

from Docs2KG.modules.llm.openai_call import openai_call
from Docs2KG.utils.get_logger import get_logger

logger = get_logger(__name__)
"""
Link documents within the same knowledge graph based on
- Temporal information
- Semantic information

"""


class DocsLinkage:
    def __init__(self, nodes_json: Path):
        """
        We will need to borrow LLM to do this.

        So the input should be a json file with a list of nodes.

        ```JSON
            [
                {
                "uuid": "0361cd85-c990-4060-a739-70bfdac317b8",
                "labels": [
                    "DOCUMENT"
                ],
                "properties": {
                    "format": "PDF 1.3",
                    "title": "Microsoft Word - WR_C19_2000_2006A.doc",
                    "author": "michelle",
                    "subject": "",
                    "keywords": "",
                    "creator": "PScript5.dll Version 5.2",
                    "producer": "GNU Ghostscript 7.06",
                    "creationDate": "2/7/2006 16:39:28",
                    "modDate": "",
                    "trapped": "",
                    "encryption": null,
                    "text_token": 25959,
                    "estimated_price_gpt35": 0.103836,
                    "estimated_price_gpt4o": 1.03836,
                    "estimated_price_4_turbo": 2.07672,
                    "file_path": "/Users/pascal/PhD/Docs2KG/data/input/tests_pdf/4.pdf",
                    "scanned_or_exported": "exported"
                    }
                },
                ...
            ]
        ```

        Then we will rely on the LLM to determine the links between the documents.
        """
        self.nodes_json = nodes_json
        self.nodes_df = pd.read_json(nodes_json)
        self.nodes_json = json.loads(open(nodes_json).read())
        self.nodes_json_str = json.dumps(self.nodes_json)
        # if len of nodes_df is less than 2, we cannot link documents
        if len(self.nodes_df) < 2:
            raise ValueError("There should be at least 2 documents to link")
        self.cost = 0

    def openai_link_docs(self) -> List:
        """
        Link documents based on the LLM model.
        Returns:

        """
        logger.info(self.nodes_json)
        try:
            messages = [
                {
                    "role": "system",
                    "content": """Link documents if they have obvious relationships,
                                  for example temporal or semantic relationships.
                                """,
                },
                {
                    "role": "user",
                    "content": f"""
                                Link the below array of nodes within a knowledge graph.

                                If they have obvious relationships, for example temporal or semantic relationships.

                                Create a relationship between the nodes.

                                Return a list in JSON under the format:

                                [{{
                                    "source_node_uuid": |uuid of the source node|,
                                    "target_node_uuid": |uuid of the target node|,
                                    "relationship": |description of the relationship|
                                }}]

                                Then given nodes are:
                                {self.nodes_json_str}
                                """,
                },
            ]
            openai_response, cost = openai_call(messages)
            self.cost += cost
            logger.info(openai_response)
            return self.extract_links(openai_response)
        except Exception as e:
            logger.exception(e)

    @staticmethod
    def extract_links(openai_response: str):
        """

        Args:
            openai_response (str): OpenAI response

        Returns:

        """
        try:
            rels = []
            openai_response = json.loads(openai_response)
            # if not list of links, transform to list
            if not isinstance(openai_response, list):
                openai_response = [openai_response]
            for link in openai_response:
                logger.info(link)
                source_node_uuid = link.get("source_node_uuid", None)
                target_node_uuid = link.get("target_node_uuid", None)
                relationship = link.get("relationship", None)
                logger.info(f"Source node: {source_node_uuid}")
                logger.info(f"Target node: {target_node_uuid}")
                logger.info(f"Relationship: {relationship}")
                if any(
                    [
                        source_node_uuid is None,
                        target_node_uuid is None,
                        relationship is None,
                    ]
                ):
                    logger.error(
                        "Missing source_node_uuid, target_node_uuid or relationship"
                    )
                    continue
                rels = {
                    "start_node": source_node_uuid,
                    "end_note": target_node_uuid,
                    "relationship": "DOCUMENT_LINK",
                }
            return rels

        except Exception as e:
            logger.exception(e)
