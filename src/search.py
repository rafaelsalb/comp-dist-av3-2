from graph import Graph
import random
from cache import Cache


class NetworkSearch:
    def __init__(self, network: Graph, ttl: int,  cache: Cache| None = None):
        self.network = network
        self.cache = cache
        self.ttl = ttl

    def _use_cache(self, target_resource: str, current_path: list[str]) -> list[str] | None:
        if self.cache is None:
            return None
        current_node_id = current_path[-1]
        node_cache = self.cache[current_node_id]
        if node_cache is None:
            return None
        cache_path = node_cache.get(target_resource)
        if cache_path is None:
            return None
        return self.cache.follow(cache_path, current_path, target_resource)


    def bfs(self, start_node_id: str, target_resource: str, use_cache: bool = False) -> list[str] | None:
        visited = set()
        queue = [(start_node_id, [start_node_id])]
        jumps = 0

        while queue and jumps <= self.ttl:
            if use_cache:
                cache_result = self._use_cache(target_resource, queue[0][1])
                if cache_result is not None:
                    self.cache.update(target_resource, cache_result)
                    return cache_result

            current_node_id, path = queue.pop(0)
            current_node = self.network[current_node_id]

            if current_node.has_resource(target_resource):
                if self.cache:
                    self.cache.update(target_resource, path)
                return path

            if current_node_id not in visited:
                visited.add(current_node_id)
                neighbors = self.network.neighbors.get(current_node_id, [])
                for neighbor in neighbors:
                    if neighbor not in visited:
                        queue.append((neighbor, path + [neighbor]))
            jumps += 1

        return None

    def dfs(self, start_node_id: str, target_resource: str, use_cache: bool = False) -> list[str] | None:
        visited = set()
        stack = [(start_node_id, [start_node_id])]
        jumps = 0

        while stack and jumps <= self.ttl:
            if use_cache:
                cache_result = self._use_cache(target_resource, stack[-1][1])
                if cache_result is not None:
                    self.cache.update(target_resource, cache_result)
                    return cache_result

            current_node_id, path = stack.pop()
            current_node = self.network[current_node_id]

            if current_node.has_resource(target_resource):
                if self.cache:
                    self.cache.update(target_resource, path)
                return path

            if current_node_id not in visited:
                visited.add(current_node_id)
                neighbors = self.network.neighbors.get(current_node_id, [])
                for neighbor in neighbors:
                    if neighbor not in visited:
                        stack.append((neighbor, path + [neighbor]))
            jumps += 1

        return None

    def random_walk(self, start_node_id: str, target_resource: str, use_cache: bool = False) -> list[str] | None:
        visited = set()
        current_node_id = start_node_id
        path = [current_node_id]
        jumps = 0

        while jumps <= self.ttl:
            if use_cache:
                cache_result = self._use_cache(target_resource, path)
                if cache_result is not None:
                    self.cache.update(target_resource, cache_result)
                    return cache_result

            current_node = self.network[current_node_id]

            if current_node.has_resource(target_resource):
                if self.cache:
                    self.cache.update(target_resource, path)
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
