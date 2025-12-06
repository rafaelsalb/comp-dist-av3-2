from graph import Graph


class NetworkSearch:
    def __init__(self, network: Graph):
        self.network = network

    def bfs(self, start_node_id: str, target_resource: str) -> list[str] | None:
        visited = set()
        queue = [(start_node_id, [start_node_id])]
        jumps = 0

        while queue and jumps <= self.network.ttl:
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

        while stack and jumps <= self.network.ttl:
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
