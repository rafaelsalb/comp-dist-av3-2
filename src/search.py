from typing import Callable
from uuid import uuid4
from graph import Graph
import random
from cache import Cache
from network.packet import Packet
from visualization.step import VisualizationStep


class NetworkSearch:
    def __init__(self, network: Graph, ttl: int,  cache: Cache| None = None, visualize_step_function: Callable | None = None):
        self.network = network
        self.cache = cache
        self.ttl = ttl
        self.step_function = visualize_step_function

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

    def flood(self, start_node_id: str, target_resource: str, use_cache: bool = False) -> list[str] | None:
        if use_cache:
            cache_result = self._use_cache(target_resource, [start_node_id])
            if cache_result is not None:
                print(f"Cache hit for {target_resource} at {start_node_id}: {cache_result}")
                return cache_result
            else:
                print(f"No cache entry for {target_resource} at {start_node_id}")

        start_node = self.network[start_node_id]
        if start_node is None:
            return None

        # Initialize the packet
        packet = Packet(
            source_id=start_node_id,
            target_id="",
            seq_num=str(uuid4()),
            ttl=self.ttl,
            path=[start_node_id]
        )
        stats = {'total_messages': 0}

        # Initialize visited nodes and queue for BFS-like traversal
        visited = set()
        queue = [(start_node_id, packet)]

        while queue:
            current_node_id, current_packet = queue.pop(0)
            current_node = self.network[current_node_id]

            # Save the visualization step
            self.save_step(start_node_id, current_node_id, visited, current_packet.path, False, current_packet.ttl)

            # Check if the current node has the target resource
            if current_node.has_resource(target_resource):
                if self.cache:
                    self.cache.update(target_resource, current_packet.path)
                self.save_step(start_node_id, current_node_id, visited, current_packet.path, True, current_packet.ttl)
                return current_packet.path

            # Mark the current node as visited
            visited.add(current_node_id)

            # Propagate the packet to neighbors
            neighbors = self.network.neighbors.get(current_node_id, [])
            for neighbor_id in neighbors:
                neighbor_node = self.network[neighbor_id]

                # Check if the neighbor has already seen this message
                if current_packet.seq_num in neighbor_node.seen_messages:
                    continue

                # Mark the message as seen by the neighbor
                neighbor_node.seen_messages.add(current_packet.seq_num)

                # Create a new packet for the neighbor
                new_packet = Packet(
                    source_id=current_packet.source_id,
                    target_id=current_packet.target_id,
                    seq_num=current_packet.seq_num,
                    ttl=current_packet.ttl - 1,
                    path=current_packet.path + [neighbor_id]
                )

                # Check if the TTL has expired
                if new_packet.ttl > 0:
                    queue.append((neighbor_id, new_packet))
                    stats['total_messages'] += 1

        # If the resource is not found, save the final step
        self.save_step(start_node_id, None, visited, packet.path, False, packet.ttl)
        return None

    def bfs(self, start_node_id: str, target_resource: str, use_cache: bool = False) -> list[str] | None:
        visited = set()
        queue = [(start_node_id, [start_node_id])]
        jumps = 0

        while queue and jumps <= self.ttl:
            if use_cache:
                cache_result = self._use_cache(target_resource, queue[0][1])
                if cache_result is not None:
                    return cache_result

            current_node_id, path = queue.pop(0)
            current_node = self.network[current_node_id]

            self.save_step(start_node_id, current_node_id, visited, path, False)

            if current_node.has_resource(target_resource):
                if self.cache:
                    self.cache.update(target_resource, path)
                self.save_step(start_node_id, current_node_id, visited, path, True)
                return path

            if current_node_id not in visited:
                visited.add(current_node_id)
                neighbors = self.network.neighbors.get(current_node_id, [])
                for neighbor in neighbors:
                    if neighbor not in visited:
                        queue.append((neighbor, path + [neighbor]))
            jumps += 1

        self.save_step(start_node_id, None, visited, path, False)
        return None

    def dfs(self, start_node_id: str, target_resource: str, use_cache: bool = False) -> list[str] | None:
        visited = set()
        stack = [(start_node_id, [start_node_id])]
        jumps = 0

        while stack and jumps <= self.ttl:
            if use_cache:
                cache_result = self._use_cache(target_resource, stack[-1][1])
                if cache_result is not None:
                    return cache_result

            current_node_id, path = stack.pop()
            current_node = self.network[current_node_id]

            self.save_step(start_node_id, current_node_id, visited, path, False)

            if current_node.has_resource(target_resource):
                if self.cache:
                    self.cache.update(target_resource, path)
                self.save_step(start_node_id, current_node_id, visited, path, True)
                return path

            if current_node_id not in visited:
                visited.add(current_node_id)
                neighbors = self.network.neighbors.get(current_node_id, [])
                for neighbor in neighbors:
                    if neighbor not in visited:
                        stack.append((neighbor, path + [neighbor]))
            jumps += 1

        self.save_step(start_node_id, None, visited, path, False)
        return None

    def random_walk(self, start_node_id: str, target_resource: str, use_cache: bool = False) -> list[str] | None:
        if use_cache:
            cache_result = self._use_cache(target_resource, [start_node_id])
            if cache_result is not None:
                print(f"Cache hit for {target_resource} at {start_node_id}: {cache_result}")
                return cache_result
            else:
                print(f"No cache entry for {target_resource} at {start_node_id}")

        start_node = self.network[start_node_id]
        if start_node is None:
            return None

        # Initialize the packet
        packet = Packet(
            source_id=start_node_id,
            target_id="",
            seq_num=str(uuid4()),
            ttl=self.ttl,
            path=[start_node_id]
        )
        stats = {'total_messages': 0}

        # Start the random walk
        current_node_id = start_node_id
        visited = set()
        while packet.ttl > 0:
            current_node = self.network[current_node_id]

            # Save the visualization step
            self.save_step(start_node_id, current_node_id, visited, packet.path, False, packet.ttl)

            # Check if the current node has the target resource
            if current_node.has_resource(target_resource):
                if self.cache:
                    self.cache.update(target_resource, packet.path)
                self.save_step(start_node_id, current_node_id, visited, packet.path, True, packet.ttl)
                return packet.path

            # Mark the current node as visited
            visited.add(current_node_id)

            # Get unvisited neighbors
            neighbors = self.network.neighbors.get(current_node_id, [])
            unvisited_neighbors = [n for n in neighbors if n not in visited]

            # If no unvisited neighbors are left, terminate the walk
            if not unvisited_neighbors:
                break

            # Choose a random neighbor and update the packet
            current_node_id = random.choice(unvisited_neighbors)
            packet.path.append(current_node_id)
            packet.ttl -= 1
            stats['total_messages'] += 1

        # If the resource is not found, save the final step
        self.save_step(start_node_id, None, visited, packet.path, False, packet.ttl)
        return None

    def save_step(self, requester_id: str, current_node_id: str, visited_nodes: set[str], path: list[str], found: bool, ttl: int = 0) -> None:
        if self.step_function:
            step = VisualizationStep(requester_id=requester_id, current_node_id=current_node_id, visited_nodes=visited_nodes, path=path, found=found, ttl=ttl)
            self.step_function(step)
