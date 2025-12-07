from .schema import GraphSchema
from .node import Node


class Graph:
    nodes: list[Node]
    neighbors: dict[str, list[Node]]

    def __init__(self, nodes: list[Node] | None = None, neighbors: dict[str, list[Node]] | None = None):
        # Recomenda-se que se utilize métodos de fábrica
        # para criar instâncias dessa classe, como o método from_schema.
        self.nodes = nodes if nodes is not None else []
        self.neighbors = neighbors if neighbors is not None else {}

    def __getitem__(self, name: str) -> Node | None:
        for node in self.nodes:
            if node.id == name:
                return node
        return None

    def __setitem__(self, name: str, value: Node) -> None:
        for i, node in enumerate(self.nodes):
            if node.id == name:
                self.nodes[i] = value
                return
        self.nodes.append(value)

    @classmethod
    def from_schema(cls, schema: GraphSchema) -> "Graph":
        unique_nodes = set()
        for edge in schema.edges:
            unique_nodes.add(edge[0])
            unique_nodes.add(edge[1])
        nodes = [Node(id=name) for name in unique_nodes]
        neighbors = {node.id: [] for node in nodes}
        for edge in schema.edges:
            neighbors[edge[0]].append(edge[1])
        for node in neighbors:
            if len(neighbors[node]) < schema.min_neighbors:
                raise ValueError(
                    f"Node {node} has less than min_neighbors ({schema.min_neighbors})"
                )
            if len(neighbors[node]) > schema.max_neighbors:
                raise ValueError(
                    f"Node {node} has more than max_neighbors ({schema.max_neighbors})"
                )
        instance = cls(nodes=nodes, neighbors=neighbors)
        return instance
