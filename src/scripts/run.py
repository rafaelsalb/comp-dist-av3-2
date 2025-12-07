import argparse
from main import example as example_main, case as case_main

parser = argparse.ArgumentParser(description="Script para rodar casos de exemplo ou casos específicos.")
parser.add_argument("--search-method", type=str, default="bfs", help="O método de busca a ser utilizado.")
parser.add_argument("--requester-id", type=str, help="O ID do solicitante.")
parser.add_argument("--resource", type=str, help="O recurso a ser buscado.")
parser.add_argument("--ttl", type=int, default=None, help="O TTL para a busca.")

def example():
    parser.add_argument("--index", type=int, help="O índice do caso a ser executado.")

    args = parser.parse_args()
    example_main(case_index=args.index, search_method=args.search_method, requester_id=args.requester_id, resource=args.resource, ttl=args.ttl)

def case():
    parser.add_argument("--path", type=str, help="O caminho do arquivo do caso a ser executado.")
    args = parser.parse_args()
    case_main(case_path=args.path, search_method=args.search_method, requester_id=args.requester_id, resource=args.resource, ttl=args.ttl)
