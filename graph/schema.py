"""
{
    "num_nodes": "int",
    "min_neighbors": "int",
    "max_neighbors": "int",
    "resources": {
        "n1": ["str"]
    },
    "edges": [["str", "str"]]
}
"""

from dataclasses import dataclass


@dataclass
class GraphSchema:
    num_nodes: int
    min_neighbors: int
    max_neighbors: int
    resources: dict[str, list[str]]
    edges: list[list[str]]

    @classmethod
    def from_dict(cls, data: dict) -> "GraphSchema":
        return cls(
            num_nodes=data["num_nodes"],
            min_neighbors=data["min_neighbors"],
            max_neighbors=data["max_neighbors"],
            resources=data["resources"],
            edges=data["edges"],
        )
