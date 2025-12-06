from loader import GraphLoader
from network import Network


def main():
    print("Hello from comp-dist-av3-2!")
    graph = GraphLoader().load("graphs/ex1.json")
    network = Network.from_graph(graph, ttl=4)
    print(network)
    requester_id = "n1"
    resource = "r2"
    found = network.fetch(requester_id, resource, search_method="bfs")
    print(f"Resource {resource} found by {requester_id} using BFS: {found}")

if __name__ == "__main__":
    main()
