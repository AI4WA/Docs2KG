import json
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from sklearn.metrics.pairwise import cosine_similarity
from transformers import BertModel, BertTokenizer

from Docs2KG.kg.constants import HTML_TAGS
from Docs2KG.utils.get_logger import get_logger

logger = get_logger(__name__)


class DynamicSchema:
    """
    For the unified knowledge graph, especially the semantic part, the schema is dynamic.

    So which will require two things:

    - From top-down methodological perspective, we can use ontology based way to implement the schema.
        - However, it will require quite a lot of pre-work before we can embrace the usage of LLM
    - So we use it from another perspective, which is bottom-up.
        - We will have the defined schema first, and then merge the schema
        - The merge process will include two parts:
            - Machine based, automatic merge
                - Frequency based merge
                - Similarity based merge
                - Other strategies
            - Human based, manual merge

    """

    def __init__(
        self, kg_json_file: Path, merge_freq: int = 10, merge_similarity: float = 0.98
    ):
        """
        Initialize the dynamic schema class
        Args:
            kg_json_file (Path): The path of the knowledge graph json file
            merge_freq (int): The frequency of the label, if it is lower than this, we will ignore it
            merge_similarity (float): The similarity threshold for the merge

        Returns:

        """
        self.kg_json_file = kg_json_file
        self.kg_json = json.load(kg_json_file.open())
        self.merge_freq = merge_freq
        self.merge_similarity = merge_similarity
        self.nodes_freq = {}
        # use bert to calculate the similarity
        self.similarity_model = None
        self.tokenizer = None

    def schema_extraction(self):
        """
        Extract the schema from the knowledge graph
        """
        nodes = self.kg_json["nodes"]

        node_df = pd.DataFrame(nodes)
        # extract the unique labels and its occurrence (labels is a list field)
        unique_labels = node_df["labels"].explode().value_counts()
        logger.info(f"Unique labels: {unique_labels}")
        self.nodes_freq = unique_labels.to_dict()

    def schema_freq_merge(self) -> dict:
        """
        Replace the label under the threshold into text_block label

        Returns:
            merge_mapping (dict): The mapping of the merge, key is the original label, value is the new label
        """

        # for the one with lower occurrence, we can ignore them
        merge_mapping = {}
        for key, value in self.nodes_freq.items():
            if key.lower() in HTML_TAGS:
                continue
            if value < self.merge_freq:
                merge_mapping[key] = "text_block"
        logger.debug(f"Merge mapping: {merge_mapping} based on frequency")
        return merge_mapping

    def schema_similarity_merge(self) -> dict:
        """
        Merge the schema based on the similarity

        Returns:
            merge_mapping (dict): The mapping of the merge, key is the original label, value is the new label
        """
        merge_mapping = {}
        # calculate the pairwise similarity for all the labels using the sentence transformer
        # for the one with high similarity, we can merge them
        # so, we should first construct a 2D matrix
        if self.similarity_model is None:
            # use bert to calculate the key similarity
            self.similarity_model = BertModel.from_pretrained("bert-base-uncased")
            self.tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")

        def encode_label(label):
            inputs = self.tokenizer(label, return_tensors="pt")
            with torch.no_grad():
                outputs = self.similarity_model(**inputs)
            return outputs.last_hidden_state[:, 0, :].numpy().flatten()

        labels = list(self.nodes_freq.keys())
        logger.debug(labels)
        label_matrix = [encode_label([label]) for label in labels]
        label_matrix = np.array(label_matrix)

        for i in range(len(labels)):
            for j in range(len(labels)):
                if i == j:
                    continue
                if (
                    cosine_similarity(
                        label_matrix[i].reshape(1, -1), label_matrix[j].reshape(1, -1)
                    )
                    > self.merge_similarity
                ):
                    if labels[i].lower() in HTML_TAGS or labels[j].lower() in HTML_TAGS:
                        continue
                    merge_mapping[labels[i]] = labels[j]

        # then we can calculate the similarity
        logger.info(f"Merge mapping: {merge_mapping} based on similarity")
        return merge_mapping

    def human_in_the_loop_input(self) -> dict:
        """
        Convert the schema into the dict
        {
            key: number of occurrence
            ...
        }

        Then human will do the decision based on the value, to do the mapping
        """
        logger.info(f"Schema: {self.nodes_freq}")
        return self.nodes_freq
