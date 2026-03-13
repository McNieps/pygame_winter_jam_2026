import random
import numpy as np

from pydantic import BaseModel, Field, model_validator

from isec.utils.catmull_rom import evaluate_catmull_rom, symmetric_offsets

# ---------------------------------------------------------------------------
# Theoretical model
# ---------------------------------------------------------------------------

class LandmarkNode(BaseModel):
    column: int
    index: int
    destinations: list[tuple[int, int]] = Field(default_factory=list)

    def add_destination(self, col: int, idx: int) -> None:
        self.destinations.append((col, idx))


class RouteGraph(BaseModel):
    columns: list[list[LandmarkNode]] = Field(default_factory=list)

    @staticmethod
    def generate(
        n_steps: int,
        landmarks_per_step: list[int] = None,
        seed: int = None,
    ) -> "RouteGraph":

        rng = random.Random(seed)

        if landmarks_per_step is not None:
            assert len(landmarks_per_step) == n_steps
            counts = landmarks_per_step
        else:
            counts = [1] + [rng.randint(1, 3) for _ in range(n_steps - 2)] + [1]

        graph = RouteGraph()
        for col, count in enumerate(counts):
            graph.columns.append([LandmarkNode(column=col, index=i) for i in range(count)])

        for col in range(n_steps - 1):
            _connect_columns(graph.columns[col], graph.columns[col + 1], rng)

        return graph


def _connect_columns(
        src: list[LandmarkNode],
        dst: list[LandmarkNode],
        rng: random.Random,
) -> None:
    """
    Order-preserving connection between two columns.
    Guarantees every node has at least one edge in and one edge out.

    Crossing-free invariant: if edge (si -> di) exists, then no edge
    (si2 -> di2) may exist where si2 > si and di2 < di (or si2 < si and di2 > di).
    We enforce this by tracking, for each si, the allowed dst range:
      - min_di[si] = max dst index reached by any src < si
      - max_di[si] = min dst index reached by any src > si
    """
    n_src, n_dst = len(src), len(dst)
    si, di = 0, 0

    # Coverage walk — guaranteed crossing-free by construction (monotone)
    while si < n_src and di < n_dst:
        src[si].add_destination(dst[di].column, dst[di].index)
        if si == n_src - 1:
            di += 1
        elif di == n_dst - 1:
            si += 1
        else:
            if rng.random() < 0.5:
                si += 1
            else:
                di += 1

    # Build per-src the current [min_di, max_di] allowed range from existing edges
    # min_di[si] = highest dst index used by any src index < si  (can't go below this)
    # max_di[si] = lowest  dst index used by any src index > si  (can't go above this)
    def _allowed_range(si: int) -> tuple[int, int]:
        lo = max(
            (max(di for _, di in src[prev].destinations) for prev in range(si) if src[prev].destinations),
            default=0,
        )
        hi = min(
            (min(di for _, di in src[nxt].destinations) for nxt in range(si + 1, n_src) if src[nxt].destinations),
            default=n_dst - 1,
        )
        return lo, hi

    # Optional extra edges — only within the allowed range
    for si, s_node in enumerate(src):
        lo, hi = _allowed_range(si)
        for di in range(lo, min(hi + 1, n_dst)):
            if (dst[di].column, dst[di].index) not in s_node.destinations:
                if rng.random() < 0.3:
                    s_node.add_destination(dst[di].column, dst[di].index)


# ---------------------------------------------------------------------------
# Concrete model
# ---------------------------------------------------------------------------

class PassagePoint(BaseModel):
    x: float
    y: float
    n_landmarks: int = Field(..., ge=1, le=3)


class PlacedLandmark(BaseModel):
    column: int
    index: int
    x: float
    y: float


class ConcreteRoute(BaseModel):
    passage_points: list[PassagePoint] = Field(..., min_length=2)
    placed_landmarks: list[list[PlacedLandmark]] = Field(default_factory=list)
    graph: RouteGraph = None
    landmark_spacing: float = Field(default=40.0, ge=10.0)

    @model_validator(mode="after")
    def validate_counts_match(self) -> "ConcreteRoute":
        if self.placed_landmarks:
            assert len(self.placed_landmarks) == len(self.passage_points), (
                "placed_landmarks columns must match passage_points length"
            )
        return self

    def build(self, seed: int = None) -> RouteGraph:
        pts = np.array([(p.x, p.y) for p in self.passage_points])
        n = len(pts)

        positions, tangents = evaluate_catmull_rom(pts, n)

        self.placed_landmarks = []
        for i, (pos, tan) in enumerate(zip(positions, tangents)):
            length = max(float(np.linalg.norm(tan)), 1e-9)
            nx, ny = -tan[1] / length, tan[0] / length  # normal (90° rotation)

            count = self.passage_points[i].n_landmarks
            offsets = symmetric_offsets(count, self.landmark_spacing)

            col_nodes = [
                PlacedLandmark(
                    column=i,
                    index=idx,
                    x=float(pos[0]) + nx * offset,
                    y=float(pos[1]) + ny * offset,
                )
                for idx, offset in enumerate(offsets)
            ]
            self.placed_landmarks.append(col_nodes)

        counts_list = [p.n_landmarks for p in self.passage_points]
        self.graph = RouteGraph.generate(n, landmarks_per_step=counts_list, seed=seed)
        return self.graph

    def get_position(self, column: int, index: int) -> tuple[float, float]:
        node = self.placed_landmarks[column][index]
        return node.x, node.y


if __name__ == "__main__":
    passage_points = [
        PassagePoint(x=50,  y=300, n_landmarks=1),
        PassagePoint(x=150, y=200, n_landmarks=2),
        PassagePoint(x=300, y=350, n_landmarks=3),
        PassagePoint(x=450, y=150, n_landmarks=2),
        PassagePoint(x=600, y=300, n_landmarks=1),
    ]

    route = ConcreteRoute(passage_points=passage_points)
    route.build(seed=42)

    print("=== Placed Landmarks ===")
    for col in route.placed_landmarks:
        for lm in col:
            print(f"  col={lm.column} idx={lm.index}  ({lm.x:.1f}, {lm.y:.1f})")

    print("\n=== Edges ===")
    for col in route.graph.columns:
        for node in col:
            for dst in node.destinations:
                print(f"  ({node.column},{node.index}) -> {dst}")

    route.save("route.json")
    print("\nSaved to route.json")

    reloaded = ConcreteRoute.load("route.json")
    print(f"Reloaded {sum(len(c) for c in reloaded.placed_landmarks)} landmarks.")