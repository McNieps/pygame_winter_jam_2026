import numpy as np


def catmull_rom_point(p0, p1, p2, p3, t: float) -> np.ndarray:
    """Evaluate one point on a Catmull-Rom segment between p1 and p2."""
    t2, t3 = t * t, t * t * t
    return 0.5 * (
        2 * p1
        + (-p0 + p2) * t
        + (2*p0 - 5*p1 + 4*p2 - p3) * t2
        + (-p0 + 3*p1 - 3*p2 + p3) * t3
    )


def catmull_rom_tangent(p0, p1, p2, p3, t: float) -> np.ndarray:
    """Evaluate the tangent at t on a Catmull-Rom segment."""
    t2 = t * t
    return 0.5 * (
        (-p0 + p2)
        + 2 * (2*p0 - 5*p1 + 4*p2 - p3) * t
        + 3 * (-p0 + 3*p1 - 3*p2 + p3) * t2
    )


def evaluate_catmull_rom(pts: np.ndarray, n_points: int) -> tuple[np.ndarray, np.ndarray]:
    """
    Sample `n_points` evenly spaced along a Catmull-Rom spline through `pts`.
    Phantom endpoints are mirrored for natural boundary behaviour.
    Returns (positions, tangents) arrays of shape (n_points, 2).
    """
    extended = np.concatenate([
        [2 * pts[0] - pts[1]],
        pts,
        [2 * pts[-1] - pts[-2]],
    ])

    n_segments = len(pts) - 1
    positions, tangents = [], []

    for i in range(n_points):
        gt = i / (n_points - 1) * n_segments
        seg = int(min(gt, n_segments - 1))
        lt = gt - seg

        p0 = extended[seg]
        p1 = extended[seg + 1]
        p2 = extended[seg + 2]
        p3 = extended[seg + 3]

        positions.append(catmull_rom_point(p0, p1, p2, p3, lt))
        tangents.append(catmull_rom_tangent(p0, p1, p2, p3, lt))

    return np.array(positions), np.array(tangents)


def symmetric_offsets(count: int, spacing: float) -> list[float]:
    if count == 1:
        return [0.0]
    half = (count - 1) / 2.0
    return [(i - half) * spacing for i in range(count)]

