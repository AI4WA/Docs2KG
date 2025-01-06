from typing import List, Tuple

from pydantic import BaseModel


class Ontology(BaseModel):
    entity_types: List[str]
    relation_types: List[str]
    connections: List[Tuple[str, str, str]]


"""
# Example usage:
example_ontology = {
    "entity_types": ["Person", "Organization"],
    "relation_types": ["WorksFor", "Manages"],
    "connections": [
        ("WorksFor", "Person", "Organization"),
        ("Manages", "Person", "Person")
    ]
}

# Validate the data
ontology = Ontology(**example_ontology)
"""
