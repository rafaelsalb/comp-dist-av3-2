from graph import Graph, GraphSchema
from visualization.network import NetworkVisualizer
from .network_node import NetworkNode
from search import NetworkSearch
from cache import Cache
from pathlib import Path
import json


class Network:
    graph: Graph
    visualizer: NetworkVisualizer | None

    def __init__(self, graph: Graph, visualizer: NetworkVisualizer | None = None):
        self.graph = graph
        self.visualizer = visualizer

    def __getitem__(self, name: str) -> Graph:
        return self.graph[name]

    def __setitem__(self, name: str, value: NetworkNode) -> None:
        self.graph[name] = value

    def create_visualizer(self):
        visualizer = NetworkVisualizer(self.edge_list)
        self.visualizer = visualizer
        return self.visualizer

    @property
    def neighbors(self) -> dict[str, list[str]]:
        return self.graph.neighbors

    @property
    def edge_list(self) -> list[list[str, str]] | None:
        return self.graph.edge_list

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

    def fetch(self, requester_id: str, resource: str, search_method: str = "bfs", ttl: int | None = None, use_cache: bool = False, cache_file: str | None = None) -> bool:
        if ttl is None:
            raise ValueError("TTL must be specified for fetch operation")

        cache = None
        if use_cache:
            if cache_file is None:
                cache_file = "cache.json"
            cache_path = Path(cache_file)

            # Load existing cache or create new one
            if cache_path.exists():
                with cache_path.open("r") as f:
                    cache_data = json.load(f)
            else:
                cache_data = {}

            cache = Cache(nodes=cache_data, file_path=cache_path, network=self)

        network_search = NetworkSearch(self, ttl, cache=cache, visualize_step_function=self.visualizer.add_step)
        match search_method:
            case "bfs":
                path = network_search.bfs(requester_id, resource, use_cache=use_cache)
            case "dfs":
                path = network_search.dfs(requester_id, resource, use_cache=use_cache)
            case "random":
                path = network_search.random_walk(requester_id, resource, use_cache=use_cache)
            case _:
                raise ValueError(f"Unknown search method: {search_method}")
        return path
