from graph import Graph
from search import NetworkSearch


class Network:
    graph: Graph
    ttl: int = 4

    def __init__(self, graph: Graph, ttl: int = 4):
        self.graph = graph
        self.ttl = ttl

    def __getitem__(self, name: str) -> Graph:
        return self.graph[name]

    @classmethod
    def from_graph(cls, graph: Graph, ttl: int = 4) -> "Network":
        return cls(graph=graph, ttl=ttl)

    def __repr__(self) -> str:
        return f"Network(graph={self.graph}, ttl={self.ttl})"

    def fetch(self, requester_id: str, resource: str, search_method: str = "bfs") -> bool:
        network_search = NetworkSearch(self)
        path = network_search.bfs(requester_id, resource)
        return path is not None
