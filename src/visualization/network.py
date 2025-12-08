import matplotlib.pyplot as plt
import networkx as nx
from .step import VisualizationStep


class NetworkVisualizer:
    def __init__(self, edges):
        self.edges = edges
        self.steps: list[VisualizationStep] = []

    def add_step(self, step: VisualizationStep):
        self.steps.append(step)

    def play(self, fps: int = 1):
        G = nx.Graph()
        G.add_edges_from(self.edges)
        pos = nx.spring_layout(G)

        for step in self.steps:
            plt.clf()
            node_colors = []
            for node in G.nodes():
                if node == step.requester_id:
                    node_colors.append('lightblue')
                elif node == step.current_node_id:
                    node_colors.append('yellow' if not step.found else 'green')
                elif node in step.path:
                    node_colors.append('grey')
                else:
                    node_colors.append('white')

            plt.title(f"Step Visualization\nRequester: {step.requester_id} | Current Node: {step.current_node_id}")
            nx.draw(G, pos, with_labels=True, node_color=node_colors, edge_color='gray', node_size=500)
            plt.pause(1 / fps)
