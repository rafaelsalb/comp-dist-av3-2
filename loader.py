import json

from graph import Graph
from graphs.schema import GraphSchema


class GraphLoader:
    def load(self, path):
        with open(path, "r") as f:
            data = json.load(f)
        graph_schema = GraphSchema.from_dict(data)
        graph = Graph.from_schema(graph_schema)
        return graph
