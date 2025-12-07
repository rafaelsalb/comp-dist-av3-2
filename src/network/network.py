from graph import Graph, GraphSchema
from .network_node import NetworkNode
from search import NetworkSearch


class Network:
    graph: Graph

    def __init__(self, graph: Graph):
        self.graph = graph

    def __getitem__(self, name: str) -> Graph:
        return self.graph[name]

    def __setitem__(self, name: str, value: NetworkNode) -> None:
        self.graph[name] = value

    @property
    def neighbors(self) -> dict[str, list[str]]:
        return self.graph.neighbors

    @classmethod
    def from_schema(cls, schema: GraphSchema) -> "Network":
        graph = Graph.from_schema(schema)
        resources = schema.resources
        for node_id, res_list in resources.items():
            node = NetworkNode(node_id, res_list)
            graph[node_id] = node
        return cls(graph)

    def __repr__(self) -> str:
        return f"Network(graph={self.graph})"

    def fetch(self, requester_id: str, resource: str, search_method: str = "bfs", ttl: int | None = None) -> bool:
        if ttl is None:
            raise ValueError("TTL must be specified for fetch operation")
        network_search = NetworkSearch(self, ttl)
        match search_method:
            case "bfs":
                path = network_search.bfs(requester_id, resource)
            case "dfs":
                path = network_search.dfs(requester_id, resource)
            case "random":
                path = network_search.random_walk(requester_id, resource)
            case _:
                raise ValueError(f"Unknown search method: {search_method}")
        return path
