"""
Benchmark module to compare search methods with and without cache.
Generates CSV results for analysis.
"""
import sys
from pathlib import Path
import time
import csv
import tempfile

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from loader import NetworkLoader
from search import NetworkSearch
from cache import Cache
import json


class BenchmarkRunner:
    def __init__(self, network_path: Path, ttl: int = 50):
        """Initialize benchmark runner with network file."""
        self.network_path = network_path
        self.ttl = ttl
        self.results = []

        # Load network
        loader = NetworkLoader()
        self.network = loader.load(str(network_path))

        # Get all nodes and resources
        self.nodes = list(self.network.neighbors.keys())
        self.resources = self._get_all_resources()

        print(f"Loaded network with {len(self.nodes)} nodes and {len(self.resources)} resources")

    def _get_all_resources(self) -> set[str]:
        """Extract all unique resources from the network."""
        resources = set()
        with open(self.network_path, 'r') as f:
            data = json.load(f)
            for node_resources in data['resources'].values():
                resources.update(node_resources)
        return resources

    def run_single_query(
        self,
        node_id: str,
        resource: str,
        search_method: str,
        cache: Cache | None = None,
        use_cache: bool = False
    ) -> dict | None:
        """
        Run a single search query and measure performance.

        Returns dict with: node_id, resource, search_method, use_cache, steps, time_ms
        Returns None if resource not found.
        """
        network_search = NetworkSearch(self.network, self.ttl, cache=cache)

        # Measure time
        start_time = time.perf_counter()

        # Execute search
        if search_method == "bfs":
            path = network_search.bfs(node_id, resource, use_cache=use_cache)
        elif search_method == "dfs":
            path = network_search.dfs(node_id, resource, use_cache=use_cache)
        elif search_method == "random":
            # Random walk is non-deterministic, try multiple times
            path = None
            for attempt in range(5):
                path = network_search.random_walk(node_id, resource, use_cache=use_cache)
                if path is not None:
                    break
        else:
            raise ValueError(f"Unknown search method: {search_method}")

        end_time = time.perf_counter()
        time_ms = (end_time - start_time) * 1000

        # Check if resource was found
        if path is None:
            return None

        steps = len(path) - 1  # Number of hops (edges traversed)

        return {
            'node_id': node_id,
            'resource': resource,
            'search_method': search_method,
            'use_cache': use_cache,
            'steps': steps,
            'time_ms': round(time_ms, 4)
        }

    def run_all_queries(self):
        """Run all combinations of nodes, resources, and search methods."""
        methods = ['bfs', 'dfs', 'random']
        total_queries = len(self.nodes) * len(self.resources) * len(methods) * 2  # ×2 for cache on/off
        query_count = 0

        print(f"Starting benchmark: {total_queries} total queries")
        print("=" * 60)

        for search_method in methods:
            print(f"\n>>> Processing {search_method.upper()}...")

            # Create persistent cache file for this method with deferred write mode
            cache_path = Path(__file__).parent / f"cache_{search_method}.json"
            with open(cache_path, 'w') as f:
                json.dump({}, f)

            cache = Cache(nodes={}, file_path=cache_path, network=self.network, deferred_write=True)

            print(f"  Phase 1: Running WITHOUT cache (baseline)...")
            # First pass: Run without cache to establish baseline
            for node_id in self.nodes:
                for resource in self.resources:
                    query_count += 1
                    if query_count % 50 == 0:
                        print(f"    Progress: {query_count}/{total_queries} queries completed")

                    result = self.run_single_query(
                        node_id,
                        resource,
                        search_method,
                        cache=None,
                        use_cache=False
                    )
                    if result:
                        self.results.append(result)

            print(f"  Phase 2: Running WITH cache (will build cache as it runs)...")
            # Second pass: Run with cache - early queries populate cache, later queries benefit
            for node_id in self.nodes:
                for resource in self.resources:
                    query_count += 1
                    if query_count % 50 == 0:
                        print(f"    Progress: {query_count}/{total_queries} queries completed")

                    result = self.run_single_query(
                        node_id,
                        resource,
                        search_method,
                        cache=cache,
                        use_cache=True
                    )
                    if result:
                        self.results.append(result)

            # Flush cache to file at the end
            print(f"  Writing cache to file...")
            cache.flush()
            print(f"  Cache file saved to: {cache_path}")

        print(f"\n{'=' * 60}")
        print(f"Benchmark complete: {len(self.results)} successful queries")
        print(f"\nCache files created:")
        for method in methods:
            cache_file = Path(__file__).parent / f"cache_{method}.json"
            if cache_file.exists():
                print(f"  - {cache_file}")

    def save_results(self, output_path: Path):
        """Save results to CSV file."""
        if not self.results:
            print("No results to save!")
            return

        with open(output_path, 'w', newline='') as f:
            writer = csv.DictWriter(
                f,
                fieldnames=['node_id', 'resource', 'search_method', 'use_cache', 'steps', 'time_ms']
            )
            writer.writeheader()
            writer.writerows(self.results)

        print(f"\nResults saved to: {output_path}")
        print(f"Total rows: {len(self.results)}")


def main():
    """Main entry point for benchmark."""
    # Paths
    project_root = Path(__file__).parent.parent
    network_path = Path(__file__).parent / "hexagonal_network.json"
    output_path = Path(__file__).parent / "results.csv"

    # Run benchmark
    runner = BenchmarkRunner(network_path, ttl=50)
    runner.run_all_queries()
    runner.save_results(output_path)

    print("\n✅ Benchmark complete! Run the Jupyter notebook to analyze results.")


if __name__ == "__main__":
    main()
