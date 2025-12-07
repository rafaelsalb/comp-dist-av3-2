# Distributed Systems Cache Simulation

Simulação de sistema de cache distribuído para busca de recursos em redes P2P.

## Instalação

```bash
uv sync
```

## Uso

### Exemplos pré-configurados

```bash
uv run example --index 0 --search-method bfs --requester-id n1 --resource r1 --ttl 24
```

```bash
uv run example --index 1 --search-method dfs --requester-id n1 --resource r1 --ttl 24
```

### Caso customizado

```bash
uv run case --path teste.json --search-method random --requester-id n1 --resource r1 --ttl 24
```

### Uso com Cache

Para habilitar o sistema de cache, adicione as flags `--use-cache` e opcionalmente `--cache-file`:

```bash
# Usando cache com arquivo padrão (cache.json)
uv run example --index 0 --search-method bfs --requester-id n1 --resource r1 --ttl 24 --use-cache

# Especificando arquivo de cache customizado
uv run case --path teste.json --search-method bfs --requester-id n1 --resource r1 --ttl 24 --use-cache --cache-file my_cache.json
```

**Opções de cache:**
- `--use-cache`: Habilita o sistema de cache
- `--cache-file <path>`: Define o arquivo de cache (padrão: `cache.json`)

O cache armazena os caminhos conhecidos para cada recurso em cada nó da rede. Quando habilitado:
1. Antes de iniciar a busca, verifica se existe um caminho em cache
2. Se encontrado, valida se o caminho ainda é válido
3. Se válido, usa o caminho em cache (economizando buscas)
4. Atualiza o cache sempre que um recurso é encontrado

## Métodos de Busca

- `bfs`: Busca em largura (Breadth-First Search)
- `dfs`: Busca em profundidade (Depth-First Search)
- `random`: Caminhada aleatória (Random Walk)

## Estrutura de Arquivos

Exemplos em: `graphs/examples/`

O formato JSON de rede deve seguir:
```json
{
  "num_nodes": 5,
  "min_neighbors": 0,
  "max_neighbors": 3,
  "resources": {
    "n1": ["r1"],
    "n2": ["r2"]
  },
  "edges": [
    ["n1", "n2"],
    ["n2", "n3"]
  ]
}
```

## Testes

Execute os testes com:
```bash
pytest tests/test_search.py -v
```
