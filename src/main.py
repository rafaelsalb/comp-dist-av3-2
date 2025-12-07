from config import Config
from loader import NetworkLoader


def example(case_index: int = 1, search_method: str = "bfs", requester_id: str | None = None, resource: str | None = None):
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
        case _:
            print(f"Caso de exemplo {case_index} não encontrado.")
            return
    network = NetworkLoader().load(case_path)
    found = network.fetch(requester_id, resource, search_method=search_method)
    print(f"Resource {resource} found by {requester_id} using {search_method}: {found}")

def case(case_path: str, search_method: str = "bfs", requester_id: str | None = None, resource: str | None = None, ttl: int | None = None):
    if requester_id is None or resource is None:
        raise ValueError("requester_id and resource must be provided for the case function.")
    print(f"Executando o caso específico: {case_path}...")
    network = NetworkLoader().load(case_path)
    found = network.fetch(requester_id, resource, search_method=search_method, ttl=ttl)
    print(f"Resource {resource} found by {requester_id} using {search_method}: {found}")
