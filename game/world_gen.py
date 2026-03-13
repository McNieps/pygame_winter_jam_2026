import random
import numpy as np
from enum import Enum
from dataclasses import dataclass, field
from typing import List, Tuple, Optional

# ---------------------------------------------------------------------------
# Node type definitions
# ---------------------------------------------------------------------------

class NodeType(str, Enum):
    combat = "combat"
    shop = "shop"
    item_drop = "item_drop"


@dataclass
class NodeDefinition:
    name: str
    type: NodeType
    weight: float


# Fixed endpoints
TOWN = NodeDefinition(name="town", type=NodeType.shop, weight=1)
VILLAGE = NodeDefinition(name="village", type=NodeType.shop, weight=1)

# Pool of possible node definitions
POOL = [
    NodeDefinition(name="crossing", type=NodeType.combat, weight=10),
    NodeDefinition(name="moor", type=NodeType.combat, weight=8),
    NodeDefinition(name="barrow", type=NodeType.combat, weight=6),
    NodeDefinition(name="hallow", type=NodeType.item_drop, weight=1),
    NodeDefinition(name="stubbing", type=NodeType.item_drop, weight=3),
    NodeDefinition(name="village", type=NodeType.shop, weight=3),
]


# ---------------------------------------------------------------------------
# Node model
# ---------------------------------------------------------------------------

@dataclass
class Node:
    column: int
    index: int
    name: Optional[str] = None
    type: Optional[NodeType] = None
    position: Tuple[float, float] = (0.0, 0.0)
    connections: List[Tuple[int, int]] = field(default_factory=list)

    def add_connection(self, col: int, idx: int) -> None:
        """Add a directed connection to another node (column, index)."""
        self.connections.append((col, idx))


# ---------------------------------------------------------------------------
# Main map generator
# ---------------------------------------------------------------------------

class MapGenerator:
    """
    Generates a procedural map consisting of columns of nodes connected in a
    directed acyclic graph, placed along a Catmull‑Rom spline, and assigns
    semantic types (combat, shop, item drop) to each node.
    """

    def __init__(self):
        self.map: List[List[Node]] = []          # columns → list of nodes
        self._rng: Optional[random.Random] = None   # per‑method RNG

    # -----------------------------------------------------------------------
    # Public API
    # -----------------------------------------------------------------------

    def generate_structure(
        self,
        n_steps: int,
        counts: Optional[List[int]] = None,
        seed: Optional[int] = None
    ) -> None:
        """
        Create the graph structure (columns and connections).

        :param n_steps: number of columns (must be ≥ 2)
        :param counts: optional list of node counts per column (length n_steps).
                       If omitted, first and last are 1, middle columns get
                       random counts between 1 and 3.
        :param seed: random seed for reproducibility
        """
        self._rng = random.Random(seed)

        # Determine node counts per column
        if counts is not None:
            if len(counts) != n_steps:
                raise ValueError("counts length must match n_steps")
            col_counts = counts
        else:
            col_counts = [1] + [self._rng.randint(1, 3) for _ in range(n_steps - 2)] + [1]

        # Create nodes
        self.map = []
        for col, cnt in enumerate(col_counts):
            column_nodes = [Node(column=col, index=i) for i in range(cnt)]
            self.map.append(column_nodes)

        # Connect adjacent columns
        for col in range(n_steps - 1):
            self._connect_columns(self.map[col], self.map[col + 1])

    def generate_map_layout(
        self,
        passage_points: List[Tuple[float, float]],
        spacing: float = 40.0,
        seed: Optional[int] = None
    ) -> None:
        """
        Place nodes along a path defined by the given passage points.
        The number of columns must already exist (from generate_structure).

        For each column i, the centre is passage_points[i]. Nodes are placed
        perpendicular to the path tangent at that point, symmetrically spaced
        by `spacing`.

        :param passage_points: list of (x, y) centre points for each column
        :param spacing: distance between nodes in the same column
        :param seed: (unused here, kept for API consistency)
        """

        if not self.map:
            raise RuntimeError("Call generate_structure before generate_map_layout")
        if len(passage_points) != len(self.map):
            raise ValueError(
                f"Number of passage points ({len(passage_points)}) "
                f"must match number of columns ({len(self.map)})"
            )

        self._rng = random.Random(seed)   # (not used, but stored for uniformity)

        pts = np.array(passage_points)
        n = len(pts)

        # Approximate tangents using finite differences
        tangents = []
        for i in range(n):
            if i == 0:
                tangents.append(pts[i + 1] - pts[i])
            elif i == n - 1:
                tangents.append(pts[i] - pts[i - 1])
            else:
                tangents.append((pts[i + 1] - pts[i - 1]) / 2.0)

        for i, (centre, tan) in enumerate(zip(pts, tangents)):
            length = max(float(np.linalg.norm(tan)), 1e-9)
            nx, ny = -tan[1] / length, tan[0] / length   # unit normal

            count = len(self.map[i])
            # Symmetric offsets around the centre
            offsets = [(idx - (count - 1) / 2.0) * spacing for idx in range(count)]

            for idx, node in enumerate(self.map[i]):
                x = float(centre[0] + nx * offsets[idx])
                y = float(centre[1] + ny * offsets[idx])
                node.position = (x, y)

    def affect_node_type(self, seed: Optional[int] = None) -> None:
        """
        Assign a name and type to every node.

        Rules:
        - First column (one node) → TOWN (shop)
        - Last column  (one node) → CITY (shop)
        - Other columns: weighted random from POOL, but if a column with more
          than one node ends up all combat, one node is demoted to a non‑combat
          type (the node with the most outgoing connections; ties broken by
          lowest index).

        :param seed: random seed for reproducibility
        """
        if not self.map:
            raise RuntimeError("Call generate_structure before affect_node_type")

        self._rng = random.Random(seed)
        n_cols = len(self.map)

        for col_idx, col_nodes in enumerate(self.map):
            self._assign_node_types_column(
                col_nodes,
                is_first_col=(col_idx == 0),
                is_last_col=(col_idx == n_cols - 1)
            )

    # -----------------------------------------------------------------------
    # Internal helpers
    # -----------------------------------------------------------------------

    def _weighted_choice(
        self,
        definitions: List[NodeDefinition],
        exclude_types: Optional[set] = None
    ) -> NodeDefinition:
        """Pick a random definition by weight, optionally excluding some types."""
        pool = definitions
        if exclude_types:
            pool = [d for d in definitions if d.type not in exclude_types]
        if not pool:                     # fallback to full pool
            pool = definitions
        weights = [d.weight for d in pool]
        return self._rng.choices(pool, weights=weights, k=1)[0]

    def _connect_columns(self, src: List[Node], dst: List[Node]) -> None:
        """
        Create order‑preserving, crossing‑free connections between two columns.
        Every node gets at least one outgoing / incoming edge.
        Additional random edges are added with probability 0.3.
        """
        n_src, n_dst = len(src), len(dst)
        si, di = 0, 0

        # Guarantee at least one edge for every node (like a "staggered" walk)
        while si < n_src and di < n_dst:
            src[si].add_connection(dst[di].column, dst[di].index)
            if si == n_src - 1:
                di += 1
            elif di == n_dst - 1:
                si += 1
            else:
                if self._rng.random() < 0.5:
                    si += 1
                else:
                    di += 1

        # Helper to compute allowed destination range for a given source node
        def allowed_range(si: int) -> Tuple[int, int]:
            lo = max(
                (max(di for _, di in src[prev].connections)
                 for prev in range(si) if src[prev].connections),
                default=0
            )
            hi = min(
                (min(di for _, di in src[nxt].connections)
                 for nxt in range(si + 1, n_src) if src[nxt].connections),
                default=n_dst - 1
            )
            return lo, hi

        # Add extra random edges
        for si, s_node in enumerate(src):
            lo, hi = allowed_range(si)
            for di in range(lo, min(hi + 1, n_dst)):
                if (dst[di].column, dst[di].index) not in s_node.connections:
                    if self._rng.random() < 0.3:
                        s_node.add_connection(dst[di].column, dst[di].index)

    def _assign_node_types_column(
        self,
        col_nodes: List[Node],
        is_first_col: bool,
        is_last_col: bool
    ) -> None:
        """Assign types to all nodes in a single column."""
        if is_first_col:
            col_nodes[0].name = VILLAGE.name
            col_nodes[0].type = VILLAGE.type
            return

        if is_last_col:
            col_nodes[0].name = TOWN.name
            col_nodes[0].type = TOWN.type
            return

        # Normal column: random picks
        for node in col_nodes:
            chosen = self._weighted_choice(POOL)
            node.name = chosen.name
            node.type = chosen.type

        # Enforce at least one non‑combat node if the column has >1 node
        if len(col_nodes) > 1:
            all_combat = all(n.type == NodeType.combat for n in col_nodes)
            if all_combat:
                # Demote the node with most connections (lowest index if tie)
                demote = max(col_nodes, key=lambda n: (len(n.connections), -n.index))
                chosen = self._weighted_choice(POOL, exclude_types={NodeType.combat})
                demote.name = chosen.name
                demote.type = chosen.type
