from dataclasses import dataclass


@dataclass
class VisualizationStep:
    requester_id: str
    current_node_id: str | None
    visited_nodes: set[str]
    path: list[str]
    found: bool
    ttl: int
