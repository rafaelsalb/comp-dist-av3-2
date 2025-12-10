from config import Config
from loader import NetworkLoader
from cache import Cache
from pathlib import Path
import json

from visualization.network import NetworkVisualizer


def example(case_index: int = 1, search_method: str = "bfs", requester_id: str | None = None, resource: str | None = None, ttl: int | None = None, use_cache: bool = False, cache_file: str | None = None, visualize: bool = False):
    if requester_id is None or resource is None:
        raise ValueError("requester_id and resource must be provided for the example function.")
    case_path = ""
    match case_index:
        case 1:
            print("Executando o caso de exemplo 1...")
            case_path = Config.EXAMPLES_DIR / "ex1.json"
        case 2:
            print("Executando o caso de exemplo 2...")
            case_path = Config.EXAMPLES_DIR / "ex2.json"
        case 3:
            print("Executando o caso de exemplo 3...")
            case_path = Config.EXAMPLES_DIR / "ex3.json"
        case _:
            print(f"Caso de exemplo {case_index} não encontrado.")
            return
    network = NetworkLoader().load(case_path)
    if visualize:
        visualizer = network.create_visualizer()
    found = network.fetch(requester_id, resource, search_method=search_method, ttl=ttl, use_cache=use_cache, cache_file=cache_file)
    if visualize:
        visualizer.play()
    print(f"Resource {resource} found by {requester_id} using {search_method}: {found}")

def case(case_path: str, search_method: str = "bfs", requester_id: str | None = None, resource: str | None = None, ttl: int | None = None, use_cache: bool = False, cache_file: str | None = None, visualize: bool = False):
    if requester_id is None or resource is None:
        raise ValueError("requester_id and resource must be provided for the case function.")
    print(f"Executando o caso específico: {case_path}...")
    network = NetworkLoader().load(case_path)
    if visualize:
        visualizer = network.create_visualizer()
    found = network.fetch(requester_id, resource, search_method=search_method, ttl=ttl, use_cache=use_cache, cache_file=cache_file)
    if visualize:
        visualizer.play()
    print(f"Resource {resource} found by {requester_id} using {search_method}: {found}")
