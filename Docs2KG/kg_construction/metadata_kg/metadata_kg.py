from pathlib import Path
from typing import Any, Dict, List, Union

import pandas as pd

from Docs2KG.kg_construction.base import KGConstructionBase
from Docs2KG.utils.config import PROJECT_CONFIG


class MetadataKGConstruction(KGConstructionBase):
    """
    The input should be a csv file with the following columns:
    - name: the name of the document
    - other columns: metadata fields, what we will do is to extract all unique values in each column and create a node for each value
    - and then create a relationship between the document and the metadata value
    - for columns is continuous, we will ignore it and put them as the property of the document node
    """

    def __init__(self, project_id: str):

        super().__init__(project_id)
        self.document_id_column = "name"
        self.continuous_columns = []
        self.categorical_columns = []

    @staticmethod
    def _is_continuous(series: pd.Series, threshold: float = 0.5) -> bool:
        """
        Determine if a column should be treated as continuous based on unique value ratio

        Args:
            series: pandas Series to check
            threshold: ratio threshold to determine if continuous

        Returns:
            bool: True if the column should be treated as continuous
        """
        unique_ratio = len(series.unique()) / len(series)
        return unique_ratio > threshold and pd.api.types.is_numeric_dtype(series)

    def _identify_column_types(self, df: pd.DataFrame) -> None:
        """
        Identify continuous and categorical columns in the dataframe

        Args:
            df: input dataframe
        """
        for column in df.columns:
            if column == self.document_id_column:
                continue
            if self._is_continuous(df[column]):
                self.continuous_columns.append(column)
            else:
                self.categorical_columns.append(column)

    def _create_document_nodes(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Create document nodes with continuous properties

        Args:
            df: input dataframe

        Returns:
            List of document nodes with properties
        """
        document_nodes = []
        for _, row in df.iterrows():
            properties = {
                col: row[col] for col in self.continuous_columns if pd.notna(row[col])
            }
            node = {
                "id": f"doc_{row[self.document_id_column]}",
                "type": "Document",
                "properties": {
                    self.document_id_column: row[self.document_id_column],
                    **properties,
                },
            }
            document_nodes.append(node)
        return document_nodes

    def _create_metadata_nodes(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Create nodes for unique categorical metadata values

        Args:
            df: input dataframe

        Returns:
            List of metadata value nodes
        """
        metadata_nodes = []
        for column in self.categorical_columns:
            unique_values = df[column].dropna().unique()
            for value in unique_values:
                node = {
                    "id": f"{column}_{value}",
                    "type": column,
                    "properties": {"value": value},
                }
                metadata_nodes.append(node)
        return metadata_nodes

    def _create_relationships(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Create relationships between documents and their metadata values

        Args:
            df: input dataframe

        Returns:
            List of relationships
        """
        relationships = []
        for _, row in df.iterrows():
            doc_id = f"doc_{row[self.document_id_column]}"
            for column in self.categorical_columns:
                if pd.notna(row[column]):
                    relationship = {
                        "source": doc_id,
                        "target": f"{column}_{row[column]}",
                        "type": f"HAS_{column.upper()}",
                    }
                    relationships.append(relationship)
        return relationships

    def construct(
        self, docs: Union[str, pd.DataFrame], document_id_column: str = "name"
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Construct knowledge graph from document metadata

        Args:
            docs: Either path to CSV file or pandas DataFrame containing document metadata
            document_id_column: Name of the column containing document IDs

        Returns:
            Dictionary containing nodes and relationships for the knowledge graph
        """
        # Load data if string path provided
        if isinstance(docs, str) or isinstance(docs, Path):
            df = pd.read_csv(docs)
        else:
            df = docs.copy()

        # remove unamed columns
        df = df.loc[:, ~df.columns.str.contains("^Unnamed")]

        # Validate required columns
        if document_id_column not in df.columns:
            raise ValueError(f"Input data must contain '{document_id_column}' column")
        self.document_id_column = document_id_column
        # Identify column types
        self._identify_column_types(df)

        # Create nodes and relationships
        document_nodes = self._create_document_nodes(df)
        metadata_nodes = self._create_metadata_nodes(df)
        relationships = self._create_relationships(df)

        metadata_kg = {
            "nodes": document_nodes + metadata_nodes,
            "relationships": relationships,
        }

        # export to metadata_kg.json
        self.export_json(metadata_kg, "metadata_kg.json")

        return metadata_kg


# Example usage
if __name__ == "__main__":
    example_project_id = "wamex"
    metadata_kg_construction = MetadataKGConstruction(example_project_id)
    metadata_kg_construction.construct(
        PROJECT_CONFIG.data.input_dir / "wamex_reports.csv",
        document_id_column="ANumber",
    )
