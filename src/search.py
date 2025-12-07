from graph import Graph
import random


class NetworkSearch:
    def __init__(self, network: Graph, ttl: int):
        self.network = network
        self.ttl = ttl

    def bfs(self, start_node_id: str, target_resource: str) -> list[str] | None:
        visited = set()
        queue = [(start_node_id, [start_node_id])]
        jumps = 0

        while queue and jumps <= self.ttl:
            current_node_id, path = queue.pop(0)
            current_node = self.network[current_node_id]

            if current_node.has_resource(target_resource):
                return path

            if current_node_id not in visited:
                visited.add(current_node_id)
                neighbors = self.network.neighbors.get(current_node_id, [])
                for neighbor in neighbors:
                    if neighbor not in visited:
                        queue.append((neighbor, path + [neighbor]))
            jumps += 1

        return None

    def dfs(self, start_node_id: str, target_resource: str) -> list[str] | None:
        visited = set()
        stack = [(start_node_id, [start_node_id])]
        jumps = 0

        while stack and jumps <= self.ttl:
            current_node_id, path = stack.pop()
            current_node = self.network[current_node_id]

            if current_node.has_resource(target_resource):
                return path

            if current_node_id not in visited:
                visited.add(current_node_id)
                neighbors = self.network.neighbors.get(current_node_id, [])
                for neighbor in neighbors:
                    if neighbor not in visited:
                        stack.append((neighbor, path + [neighbor]))

        return None

    def random_walk(self, start_node_id: str, target_resource: str) -> list[str] | None:
        visited = set()
        current_node_id = start_node_id
        path = [current_node_id]
        jumps = 0

        while jumps <= self.ttl:
            current_node = self.network[current_node_id]

            if current_node.has_resource(target_resource):
                return path

            visited.add(current_node_id)
            neighbors = self.network.neighbors.get(current_node_id, [])
            unvisited_neighbors = [n for n in neighbors if n not in visited]

            if not unvisited_neighbors:
                break

            current_node_id = random.choice(unvisited_neighbors)
            path.append(current_node_id)
            jumps += 1

        return None
