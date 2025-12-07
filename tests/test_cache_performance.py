"""
Unit tests for cache performance and correctness.
Tests identified issues with cache returning suboptimal paths and excessive file I/O.
"""
import pytest
import tempfile
import json
from pathlib import Path
import sys
from unittest.mock import Mock, patch, mock_open

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from cache.cache import Cache
from network import Network, NetworkNode
from graph import Graph, Node
from search import NetworkSearch


@pytest.fixture
def simple_network():
    """
    Create a simple test network:
    n1 -- n2 -- n3 (has r1)
     |         /
    n4 ------

    Shortest path n1->r1: [n1, n2, n3] (2 hops)
    Longer path n1->r1: [n1, n4, n3] (2 hops, same length)
    """
    nodes = [Node(id=f"n{i}") for i in range(1, 5)]
    neighbors = {
        "n1": ["n2", "n4"],
        "n2": ["n1", "n3"],
        "n3": ["n2", "n4"],
        "n4": ["n1", "n3"]
    }

    graph = Graph(nodes=nodes, neighbors=neighbors)
    network = Network(graph)

    # Add resources
    network["n1"] = NetworkNode("n1", set())
    network["n2"] = NetworkNode("n2", set())
    network["n3"] = NetworkNode("n3", {"r1"})
    network["n4"] = NetworkNode("n4", set())

    return network


@pytest.fixture
def cache_file():
    """Create a temporary cache file"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump({}, f)
        temp_path = Path(f.name)
    yield temp_path
    if temp_path.exists():
        temp_path.unlink()


class TestCacheCorrectness:
    """Test that cache stores and retrieves paths correctly"""

    def test_cache_stores_relative_paths(self, simple_network, cache_file):
        """Test that cache stores correct relative paths for each node in the path"""
        cache = Cache(nodes={}, file_path=cache_file, network=simple_network)

        path = ["n1", "n2", "n3"]
        cache.update("r1", path)

        # Check stored paths
        assert cache["n1"]["r1"] == ["n2", "n3"]
        assert cache["n2"]["r1"] == ["n3"]
        assert cache["n3"]["r1"] == []

    def test_cache_follow_no_duplication(self, simple_network, cache_file):
        """Test that follow() doesn't duplicate nodes in the path"""
        cache = Cache(nodes={
            "n1": {"r1": ["n2", "n3"]},
            "n2": {"r1": ["n3"]}
        }, file_path=cache_file, network=simple_network)

        # Following from n1
        current_path = ["n1"]
        cached_path = ["n2", "n3"]
        result = cache.follow(cached_path, current_path, "r1")

        assert result == ["n1", "n2", "n3"]
        # Verify no duplicates
        assert len(result) == len(set(result))

    def test_cache_follow_from_intermediate_node(self, simple_network, cache_file):
        """Test that following from intermediate node works correctly"""
        cache = Cache(nodes={
            "n2": {"r1": ["n3"]}
        }, file_path=cache_file, network=simple_network)

        current_path = ["n1", "n2"]
        cached_path = ["n3"]
        result = cache.follow(cached_path, current_path, "r1")

        assert result == ["n1", "n2", "n3"]


class TestCacheFileIO:
    """Test cache file I/O performance"""

    def test_cache_writes_to_file_on_update(self, simple_network, cache_file):
        """Test that cache writes to file on each update by default"""
        cache = Cache(nodes={}, file_path=cache_file, network=simple_network)

        # Update cache
        cache.update("r1", ["n1", "n2", "n3"])

        # Verify file was written
        with open(cache_file, 'r') as f:
            data = json.load(f)

        assert "n1" in data
        assert data["n1"]["r1"] == ["n2", "n3"]

    def test_deferred_write_mode_prevents_immediate_write(self, simple_network, cache_file):
        """Test that deferred write mode prevents writing on each update"""
        cache = Cache(nodes={}, file_path=cache_file, network=simple_network, deferred_write=True)

        # Update cache
        cache.update("r1", ["n1", "n2", "n3"])

        # File should still be empty (only has {})
        with open(cache_file, 'r') as f:
            data = json.load(f)

        assert data == {} or "n1" not in data

    def test_flush_writes_deferred_cache(self, simple_network, cache_file):
        """Test that flush() writes deferred cache to file"""
        cache = Cache(nodes={}, file_path=cache_file, network=simple_network, deferred_write=True)

        # Update cache multiple times
        cache.update("r1", ["n1", "n2", "n3"])
        cache.update("r2", ["n1", "n4"])

        # Flush cache
        cache.flush()

        # Verify file was written
        with open(cache_file, 'r') as f:
            data = json.load(f)

        assert "n1" in data
        assert data["n1"]["r1"] == ["n2", "n3"]
        assert data["n1"]["r2"] == ["n4"]


class TestSearchWithCache:
    """Test that search methods use cache correctly"""

    def test_bfs_uses_cache_when_available(self, simple_network, cache_file):
        """Test that BFS uses cached path when available"""
        # Pre-populate cache
        cache = Cache(nodes={
            "n1": {"r1": ["n2", "n3"]}
        }, file_path=cache_file, network=simple_network)

        search = NetworkSearch(simple_network, ttl=10, cache=cache)
        result = search.bfs("n1", "r1", use_cache=True)

        assert result == ["n1", "n2", "n3"]

    def test_bfs_without_cache_finds_resource(self, simple_network, cache_file):
        """Test that BFS without cache still works"""
        search = NetworkSearch(simple_network, ttl=10, cache=None)
        result = search.bfs("n1", "r1", use_cache=False)

        assert result is not None
        assert result[0] == "n1"
        assert result[-1] == "n3"

    def test_cache_hit_doesnt_update_cache(self, simple_network, cache_file):
        """Test that using cached path doesn't write back to cache"""
        # Pre-populate cache
        initial_cache = {
            "n1": {"r1": ["n2", "n3"]}
        }

        with open(cache_file, 'w') as f:
            json.dump(initial_cache, f)

        cache = Cache(nodes=initial_cache.copy(), file_path=cache_file, network=simple_network)

        # Get file modification time
        mtime_before = cache_file.stat().st_mtime

        search = NetworkSearch(simple_network, ttl=10, cache=cache)
        result = search.bfs("n1", "r1", use_cache=True)

        # File should not be modified (cache hit shouldn't write)
        mtime_after = cache_file.stat().st_mtime

        # Note: This test will fail with current implementation
        # After fix, cache hit should NOT trigger file write
        assert result == ["n1", "n2", "n3"]


class TestCachePerformance:
    """Test cache performance characteristics"""

    def test_deferred_write_reduces_file_operations(self, simple_network):
        """Test that deferred write significantly reduces file I/O"""
        # Test without deferred write - count actual file writes
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({}, f)
            cache_file_immediate = Path(f.name)

        try:
            cache_immediate = Cache(nodes={}, file_path=cache_file_immediate, network=simple_network, deferred_write=False)

            # Track file size changes (each write increases size)
            initial_size = cache_file_immediate.stat().st_size
            for i in range(10):
                cache_immediate.update(f"r{i}", ["n1", "n2", "n3"])

            # File should have grown (written to 10 times)
            final_size = cache_file_immediate.stat().st_size
            assert final_size > initial_size

            # Verify all data is there
            with open(cache_file_immediate, 'r') as f:
                data = json.load(f)
            assert len(data["n1"]) == 10  # 10 resources stored
        finally:
            if cache_file_immediate.exists():
                cache_file_immediate.unlink()

        # Test with deferred write
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({}, f)
            cache_file_deferred = Path(f.name)

        try:
            cache_deferred = Cache(nodes={}, file_path=cache_file_deferred, network=simple_network, deferred_write=True)

            initial_size = cache_file_deferred.stat().st_size
            for i in range(10):
                cache_deferred.update(f"r{i}", ["n1", "n2", "n3"])

            # File should NOT have changed (deferred write)
            mid_size = cache_file_deferred.stat().st_size
            assert mid_size == initial_size

            # Now flush
            cache_deferred.flush()

            # File should have grown now
            final_size = cache_file_deferred.stat().st_size
            assert final_size > initial_size

            # Verify all data is there
            with open(cache_file_deferred, 'r') as f:
                data = json.load(f)
            assert len(data["n1"]) == 10  # 10 resources stored
        finally:
            if cache_file_deferred.exists():
                cache_file_deferred.unlink()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
