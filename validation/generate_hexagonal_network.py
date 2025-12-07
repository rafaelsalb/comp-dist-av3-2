"""
Generate a large hexagonal network with 100 nodes and 200 resources.
"""
import json
from pathlib import Path
import math


def generate_hexagonal_network(num_nodes: int = 100, num_resources: int = 200):
    """
    Generate a hexagonal grid network.

    Args:
        num_nodes: Number of nodes in the network
        num_resources: Number of resources to distribute
    """
    # Calculate grid dimensions for hexagonal layout
    # For a hexagonal grid, we use axial coordinates
    grid_size = math.ceil(math.sqrt(num_nodes))

    nodes = []
    edges = []
    resources_dict = {}

    # Generate nodes in hexagonal pattern
    node_count = 0
    for q in range(-grid_size, grid_size + 1):
        for r in range(-grid_size, grid_size + 1):
            if abs(q + r) <= grid_size and node_count < num_nodes:
                node_id = f"n{node_count + 1}"
                nodes.append((node_id, q, r))
                node_count += 1

    # Create dictionary for quick lookup
    coord_to_node = {(q, r): node_id for node_id, q, r in nodes}

    # Generate edges (hexagonal connectivity)
    # In axial coordinates, neighbors are at offsets: (+1,0), (-1,0), (0,+1), (0,-1), (+1,-1), (-1,+1)
    hex_directions = [(1, 0), (-1, 0), (0, 1), (0, -1), (1, -1), (-1, 1)]

    edges_set = set()
    for node_id, q, r in nodes:
        for dq, dr in hex_directions:
            neighbor_q, neighbor_r = q + dq, r + dr
            if (neighbor_q, neighbor_r) in coord_to_node:
                neighbor_id = coord_to_node[(neighbor_q, neighbor_r)]
                # Add edge (avoid duplicates by sorting)
                edge = tuple(sorted([node_id, neighbor_id]))
                edges_set.add(edge)

    edges = [list(edge) for edge in edges_set]

    # Distribute resources across nodes
    resources_per_node = num_resources // num_nodes
    extra_resources = num_resources % num_nodes

    resource_id = 1
    for i, (node_id, _, _) in enumerate(nodes):
        node_resources = []
        # Give base resources to all nodes
        for _ in range(resources_per_node):
            node_resources.append(f"r{resource_id}")
            resource_id += 1
        # Distribute extra resources to first nodes
        if i < extra_resources:
            node_resources.append(f"r{resource_id}")
            resource_id += 1

        resources_dict[node_id] = node_resources

    # Create network structure
    network = {
        "num_nodes": num_nodes,
        "min_neighbors": 0,  # Edge nodes have fewer neighbors
        "max_neighbors": 6,  # Hexagonal grid max
        "resources": resources_dict,
        "edges": edges
    }

    return network


def main():
    """Generate and save the network."""
    print("Generating hexagonal network with 100 nodes and 200 resources...")

    network = generate_hexagonal_network(num_nodes=100, num_resources=200)

    output_path = Path(__file__).parent / "hexagonal_network.json"

    with open(output_path, 'w') as f:
        json.dump(network, f, indent=2)

    print(f"✅ Network generated successfully!")
    print(f"   Nodes: {network['num_nodes']}")
    print(f"   Resources: {sum(len(r) for r in network['resources'].values())}")
    print(f"   Edges: {len(network['edges'])}")
    print(f"   Saved to: {output_path}")

    # Calculate average degree
    node_degrees = {}
    for edge in network['edges']:
        node_degrees[edge[0]] = node_degrees.get(edge[0], 0) + 1
        node_degrees[edge[1]] = node_degrees.get(edge[1], 0) + 1

    avg_degree = sum(node_degrees.values()) / len(node_degrees)
    print(f"   Average degree: {avg_degree:.2f}")


if __name__ == "__main__":
    main()
