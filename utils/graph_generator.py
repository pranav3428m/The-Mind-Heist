# Mind Heist: Neural Hacker - Procedural Neural Graph Generation

import random
import math
import networkx as nx

from game.constants import (
    GRAPH_X_MIN, GRAPH_X_MAX,
    GRAPH_Y_MIN, GRAPH_Y_MAX,
    NODE_MIN_SPACING,
)


class GraphGenerator:
    """Generates a procedural neural-network-style graph for each level."""

    def __init__(self):
        self._graph = nx.Graph()
        self._positions = {}   # node_id -> (x, y)

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def generate_graph(self, difficulty: int, node_count: int = None,
                       connection_prob: float = None) -> None:
        """Create a new random graph scaled to *difficulty*.

        Args:
            difficulty: 1–4.  Controls default node count and connection
                        probability when explicit values are not supplied.
            node_count: Override the number of nodes to generate.
            connection_prob: Override the Erdős–Rényi edge probability.
        """
        if node_count is None:
            # Base node count scaled by difficulty
            base = 15 + (difficulty - 1) * 10
            node_count = random.randint(base, base + 5)

        if connection_prob is None:
            connection_prob = min(0.3 + (difficulty - 1) * 0.1, 0.7)

        self._graph.clear()
        self._positions.clear()

        # Place nodes with minimum spacing enforcement
        positions = self._place_nodes(node_count)
        for i, pos in enumerate(positions):
            self._graph.add_node(i, pos=pos)
            self._positions[i] = pos

        # Add edges based on Erdős–Rényi probability, but only connect
        # nodes that are within a reasonable visual distance to avoid
        # overly long crossing edges.
        max_edge_len = (GRAPH_X_MAX - GRAPH_X_MIN) * 0.4
        for u in range(node_count):
            for v in range(u + 1, node_count):
                dist = math.hypot(
                    positions[u][0] - positions[v][0],
                    positions[u][1] - positions[v][1],
                )
                if dist <= max_edge_len and random.random() < connection_prob:
                    self._graph.add_edge(u, v)

        # Guarantee connectivity: run a spanning tree over disconnected parts
        self._ensure_connected()

    def get_node_positions(self) -> dict:
        """Return a dict mapping node_id -> (x, y)."""
        return dict(self._positions)

    def get_edges(self) -> list:
        """Return list of (node_id_a, node_id_b) edge tuples."""
        return list(self._graph.edges())

    def is_connected(self) -> bool:
        """Return True if the graph is fully connected."""
        return nx.is_connected(self._graph)

    def get_random_spawn_point(self) -> tuple:
        """Return a random node position suitable for player spawning."""
        if not self._positions:
            return (GRAPH_X_MIN, GRAPH_Y_MIN)
        node_id = random.choice(list(self._positions.keys()))
        return self._positions[node_id]

    def get_node_count(self) -> int:
        return self._graph.number_of_nodes()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _place_nodes(self, count: int) -> list:
        """Return a list of (x, y) positions with minimum spacing."""
        placed = []
        max_attempts = count * 50
        attempts = 0

        while len(placed) < count and attempts < max_attempts:
            attempts += 1
            x = random.randint(GRAPH_X_MIN, GRAPH_X_MAX)
            y = random.randint(GRAPH_Y_MIN, GRAPH_Y_MAX)
            if all(
                math.hypot(x - px, y - py) >= NODE_MIN_SPACING
                for px, py in placed
            ):
                placed.append((x, y))

        # If we ran out of attempts, fill remaining with best-effort
        while len(placed) < count:
            x = random.randint(GRAPH_X_MIN, GRAPH_X_MAX)
            y = random.randint(GRAPH_Y_MIN, GRAPH_Y_MAX)
            placed.append((x, y))

        return placed

    def _ensure_connected(self) -> None:
        """Connect all components by linking them with the shortest bridge."""
        while not nx.is_connected(self._graph):
            components = list(nx.connected_components(self._graph))
            # Pick the two closest nodes from different components
            comp_a = components[0]
            best_u, best_v, best_dist = None, None, float("inf")

            for other in components[1:]:
                for u in comp_a:
                    for v in other:
                        d = math.hypot(
                            self._positions[u][0] - self._positions[v][0],
                            self._positions[u][1] - self._positions[v][1],
                        )
                        if d < best_dist:
                            best_dist = d
                            best_u, best_v = u, v
                break  # connect one pair per iteration

            if best_u is not None:
                self._graph.add_edge(best_u, best_v)
