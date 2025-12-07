import json

from graph import Graph
from graph import GraphSchema

from network import Network, NetworkNode


class GraphLoader:
    def load(self, path):
        with open(path, "r") as f:
            data = json.load(f)
        graph_schema = GraphSchema.from_dict(data)
        graph = Graph.from_schema(graph_schema)
        return graph

class NetworkLoader:
    def load(self, path):
        with open(path, "r") as f:
            data = json.load(f)
        graph_schema = GraphSchema.from_dict(data)
        network = Network.from_schema(graph_schema)
        return network
