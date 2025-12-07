import pytest
import json
import tempfile
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from loader import NetworkLoader
from search import NetworkSearch
from cache.cache import Cache


@pytest.fixture
def test_network():
    """
    Network structure:
    n1 -> n2 (has r1), n3 (has r2)
    n2 -> n3, n4 (has r3)
    n3 -> n5 (has r4)

    Expected paths from n1:
    - r1: n1 -> n2
    - r2: n1 -> n3
    - r3: n1 -> n2 -> n4
    - r4: n1 -> n3 -> n5
    """
    loader = NetworkLoader()
    network_path = Path(__file__).parent / "test_network.json"
    network = loader.load(str(network_path))
    return network


@pytest.fixture
def cache_file():
    """Create a temporary cache file"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump({}, f)
        temp_path = Path(f.name)
    yield temp_path
    # Cleanup
    if temp_path.exists():
        temp_path.unlink()


@pytest.fixture
def search_with_cache(test_network, cache_file):
    """NetworkSearch instance with cache"""
    cache = Cache(nodes={}, file_path=cache_file, network=test_network)
    return NetworkSearch(network=test_network, ttl=10, cache=cache)


@pytest.fixture
def search_without_cache(test_network):
    """NetworkSearch instance without cache"""
    return NetworkSearch(network=test_network, ttl=10, cache=None)


class TestBFSWithoutCache:
    def test_find_r1(self, search_without_cache):
        result = search_without_cache.bfs("n1", "r1", use_cache=False)
        assert result == ["n1", "n2"]

    def test_find_r2(self, search_without_cache):
        result = search_without_cache.bfs("n1", "r2", use_cache=False)
        assert result == ["n1", "n3"]

    def test_find_r3(self, search_without_cache):
        result = search_without_cache.bfs("n1", "r3", use_cache=False)
        assert result == ["n1", "n2", "n4"]

    def test_find_r4(self, search_without_cache):
        result = search_without_cache.bfs("n1", "r4", use_cache=False)
        assert result == ["n1", "n3", "n5"]

    def test_resource_not_found(self, search_without_cache):
        result = search_without_cache.bfs("n1", "r999", use_cache=False)
        assert result is None


class TestBFSWithCache:
    def test_find_r1_first_time(self, search_with_cache):
        result = search_with_cache.bfs("n1", "r1", use_cache=True)
        assert result == ["n1", "n2"]
        # Verify cache was updated
        assert search_with_cache.cache["n1"] is not None
        assert search_with_cache.cache["n1"].get("r1") == ["n2"]

    def test_find_r1_from_cache(self, search_with_cache):
        # First search to populate cache
        search_with_cache.bfs("n1", "r1", use_cache=True)
        # Second search should use cache
        result = search_with_cache.bfs("n1", "r1", use_cache=True)
        assert result == ["n1", "n2"]

    def test_find_r3_multilevel_cache(self, search_with_cache):
        result = search_with_cache.bfs("n1", "r3", use_cache=True)
        assert result == ["n1", "n2", "n4"]
        # Verify all nodes in path cached the resource
        assert search_with_cache.cache["n1"]["r3"] == ["n2", "n4"]
        assert search_with_cache.cache["n2"]["r3"] == ["n4"]


class TestDFSWithoutCache:
    def test_find_r1(self, search_without_cache):
        result = search_without_cache.dfs("n1", "r1", use_cache=False)
        assert result == ["n1", "n2"]

    def test_find_r2(self, search_without_cache):
        result = search_without_cache.dfs("n1", "r2", use_cache=False)
        assert result in [["n1", "n3"], ["n1", "n2", "n3"]]

    def test_find_r3(self, search_without_cache):
        result = search_without_cache.dfs("n1", "r3", use_cache=False)
        assert result == ["n1", "n2", "n4"]

    def test_find_r4(self, search_without_cache):
        result = search_without_cache.dfs("n1", "r4", use_cache=False)
        assert "n5" in result and result[-1] == "n5"

    def test_resource_not_found(self, search_without_cache):
        result = search_without_cache.dfs("n1", "r999", use_cache=False)
        assert result is None


class TestDFSWithCache:
    def test_find_r1_first_time(self, search_with_cache):
        result = search_with_cache.dfs("n1", "r1", use_cache=True)
        assert result == ["n1", "n2"]
        assert search_with_cache.cache["n1"]["r1"] == ["n2"]

    def test_find_r1_from_cache(self, search_with_cache):
        search_with_cache.dfs("n1", "r1", use_cache=True)
        result = search_with_cache.dfs("n1", "r1", use_cache=True)
        assert result == ["n1", "n2"]


class TestRandomWalkWithoutCache:
    def test_find_r1(self, search_without_cache):
        # Try multiple times since random walk is non-deterministic
        found = False
        for _ in range(10):
            result = search_without_cache.random_walk("n1", "r1", use_cache=False)
            if result is not None and result[0] == "n1" and result[-1] == "n2":
                found = True
                break
        assert found, "Random walk should eventually find r1"

    def test_find_r2(self, search_without_cache):
        # Try multiple times since random walk is non-deterministic
        found = False
        for _ in range(10):
            result = search_without_cache.random_walk("n1", "r2", use_cache=False)
            if result is not None and result[0] == "n1" and result[-1] == "n3":
                found = True
                break
        assert found, "Random walk should eventually find r2"

    def test_resource_may_not_be_found_with_ttl(self, search_without_cache):
        # With low TTL, random walk might not find resource
        search_without_cache.ttl = 1
        result = search_without_cache.random_walk("n1", "r4", use_cache=False)
        # Result can be None or a valid path depending on random choices
        assert result is None or (result[0] == "n1" and result[-1] == "n5")


class TestRandomWalkWithCache:
    def test_find_r1_first_time(self, search_with_cache):
        # Try multiple times since random walk is non-deterministic
        found = False
        for _ in range(10):
            result = search_with_cache.random_walk("n1", "r1", use_cache=True)
            if result is not None and result[0] == "n1" and result[-1] == "n2":
                found = True
                assert search_with_cache.cache["n1"]["r1"] is not None
                break
        assert found, "Random walk should eventually find r1"

    def test_find_r1_from_cache(self, search_with_cache):
        # First populate cache using BFS to ensure cache is populated
        search_with_cache.bfs("n1", "r1", use_cache=True)
        # Now random walk should use cache immediately
        result = search_with_cache.random_walk("n1", "r1", use_cache=True)
        assert result == ["n1", "n2"]


class TestCachePersistence:
    def test_cache_file_persistence(self, test_network, cache_file):
        cache = Cache(nodes={}, file_path=cache_file, network=test_network)
        search = NetworkSearch(network=test_network, ttl=10, cache=cache)

        # Perform search to populate cache
        search.bfs("n1", "r1", use_cache=True)

        # Load cache from file
        with cache_file.open("r") as f:
            cache_data = json.load(f)

        assert "n1" in cache_data
        assert "r1" in cache_data["n1"]
        assert cache_data["n1"]["r1"] == ["n2"]
