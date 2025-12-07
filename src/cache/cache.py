from pathlib import Path
from typing import TYPE_CHECKING
import json

if TYPE_CHECKING:
    from network import Network


class Cache:
    def __init__(self, nodes: dict[str, dict[str, list[str]]], file_path: Path, network: "Network", deferred_write: bool = False):
        self.nodes: dict[str, dict[str, list[str]]] = nodes
        self.path: Path = file_path
        self.network: "Network" = network
        self.deferred_write: bool = deferred_write

    def __getitem__(self, node_id: str) -> dict[str, list[str]] | None:
        return self.nodes.get(node_id)

    def follow(self, cache_path: list[str], current_path: list[str], target_resource: str) -> list[str] | None:
        new_path: list[str] = current_path.copy()
        for node_id in cache_path:
            try:
                node = self.network[node_id]
            except Exception:
                return None

            if node is None:
                return None

            new_path.append(node_id)
            

        # Only check if resource exists at the final node in the cached path
        if len(cache_path) > 0:
            final_node = self.network[cache_path[-1]]
            if final_node and final_node.has_resource(target_resource):
                return new_path

        return None

    def update(self, resource: str, network_path: list[str]) -> None:
        for i in range(len(network_path)):
            current_node = network_path[i]
            remaining_path = network_path[i + 1:]
            if current_node not in self.nodes:
                self.nodes[current_node] = {}
            self.nodes[current_node][resource] = remaining_path

        if not self.deferred_write:
            self._write_to_file()

    def flush(self) -> None:
        """Write cache to file. Use this when deferred_write is enabled."""
        self._write_to_file()

    def _write_to_file(self) -> None:
        """Internal method to write cache to file."""
        with self.path.open("w") as f:
            json.dump(self.nodes, f, indent=2)
